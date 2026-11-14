"""
Deadline Radar - AI Extraction Engine
Powered by the official Google GenAI Python SDK (`google-genai`) with
an intelligent rule-based multilingual campus extractor fallback.
Extracts structured deadline and event entities from multilingual campus chats:
English, Hindi, Roman Hindi, and Hinglish.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from dates import resolve_date, parse_time_string

logger = logging.getLogger(__name__)

# System prompt enforcing strict structured JSON extraction schema
EXTRACTION_SYSTEM_PROMPT = """You are an expert AI parser for Indian university / college WhatsApp and Telegram chat notices.
Your task is to extract academic deadlines, scheduled events, schedule changes, postponements, cancellations, and filter out irrelevant chatter.

The messages are in English, Hindi (Roman script), or Hinglish (e.g. "kal tak submit karna hai", "quiz postpone ho gaya", "parso lab hai", "proxy laga do").

For each input message, you are given:
- id: integer message id
- sent_at: ISO timestamp and weekday when the message was sent (USE THIS EXACT SENT_AT TIME TO INTERPRET RELATIVE DATES LIKE 'kal', 'parso', 'tomorrow', 'this Friday', 'next Monday')
- sender: name or role of sender
- text: the message content

You must return a JSON object with this EXACT structure:
{
  "items": [
    {
      "message_id": <int matching input id>,
      "category": "deadline" | "event" | "schedule_change" | "cancellation" | "chatter",
      "title": <concise standardized title e.g. "DBMS Assignment 2 Submission", or null if chatter>,
      "date": <"YYYY-MM-DD" resolved date based on sent_at, or null if unspecified/unclear>,
      "original_date_phrase": <the exact phrase used, e.g. "kal tak", "14th Nov", "next Monday", or null>,
      "time": <"HH:MM" 24-hour format e.g. "23:59", "10:00", or null>,
      "venue": <classroom/hall/online link e.g. "Audi 2", "LMS Portal", "Room 302", or null>,
      "course_or_subject": <course name or club e.g. "DBMS", "Machine Learning", "ECE 202", or null>,
      "audience": <intended audience e.g. "All Students", "Section B", "Club Members", or null>,
      "refers_to": <for schedule_change/cancellation: concise title of the original event being modified, else null>,
      "confidence": <float between 0.0 and 1.0 representing extraction confidence>,
      "explanation": <one brief sentence explaining why this classification was made>
    }
  ]
}

STRICT EXTRACTION RULES:
1. "deadline": Actionable submission or task required by a specific date/time (e.g. assignments, project reports, form submissions).
2. "event": Academic or campus gathering occurring at a specific date/time (e.g. quizzes, lectures, workshops, club sessions, exams).
3. "schedule_change": Postponement, rescheduling, or venue/time alteration of a previously planned event.
4. "cancellation": Explicit cancellation of an event or class.
5. "chatter": Casual student banter, food complaints, proxy requests, memes, "ok", "thank you", or rhetorical questions.
6. NEVER INVENT OR HALLUCINATE DATES, TIMES, OR VENUES. If a date is missing or announced as "TBA" / "later", set "date" to null and note in explanation.
7. TIMEZONE & RELATIVE DATES: Sent timestamps are Asia/Kolkata (IST).
   - "kal" = sent_at + 1 day
   - "parso" = sent_at + 2 days
   - "aaj" = sent_at date
8. Keep "title" consistent across repeated reminders of the same item so they can be merged.
"""

# Multilingual pattern definitions for campus extraction
CHATTER_PATTERNS = [
    r"\b(proxy|attendance|canteen|food|lunch|dinner|mess|lol|haha|lmao|treat|party|chai|coffee|bakwas|bekar)\b",
    r"\b(kya scene hai|padhna hai ya nahi|chal raha hai kya|kaise ho|mast hai)\b",
    r"^(ok|okay|k|cool|thx|thanks|thank you|done|noted|yes|haan|ha|theek hai)[.!]?$",
]

COURSES = [
    ("Machine Learning", ["machine learning", r"\bml\b"]),
    ("NLP", ["nlp", "natural language processing"]),
    ("DBMS", ["dbms", "database"]),
    ("Operating Systems", ["operating systems", r"\bos\b"]),
    ("Computer Networks", ["computer networks", r"\bcn\b"]),
    ("ECE 202", ["ece 202", r"\bece\b"]),
    ("Cloud Computing", ["cloud computing", r"\bcc\b"]),
    ("Product Management", ["product management", r"\bpm\b"]),
    ("Design Thinking", ["design thinking", r"\bdt\b"]),
    ("Business Fundamentals", ["business fundamentals", r"\bbf\b"]),
    ("AI for PM", ["ai for product managers", "ai for pm", "raman sir"]),
    ("Robotics Club", ["robotics club", "robotics"]),
    ("Open Source Club", ["open source club", "gsoc"]),
]

VENUES = [
    r"Audi(?:torium)?\s*\d+",
    r"Room\s*\d+",
    r"Lab\s*\d+",
    r"Exam Hall\s*\d*",
    r"Hall\s*\d+",
    r"LMS\s*(?:Portal)?",
    r"Google\s*Forms?(?:\s*\([^)]+\))?",
    r"Moodle",
    r"CRC\s*Room",
    r"SH\d+",
    r"H\d+",
    r"Vindhya\s*[A-Z0-9]+",
    r"forms\.gle/\S+",
]


def extract_with_heuristics(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Intelligent heuristic extractor for multilingual university chats.
    Extracts deadlines, events, dates (absolute & Hinglish relative), times,
    courses, and cancellations directly from message text without requiring external API keys.
    """
    extracted_items: List[Dict[str, Any]] = []

    for m in messages:
        text = m.get("text", "")
        sender = m.get("sender", "Unknown")
        sent_at = m.get("sent_at")

        # 1. Chatter Check FIRST
        if any(re.search(p, text, re.I) for p in CHATTER_PATTERNS):
            extracted_items.append({
                "message_id": m["id"],
                "category": "chatter",
                "title": None,
                "date": None,
                "original_date_phrase": None,
                "time": None,
                "venue": None,
                "course_or_subject": None,
                "audience": None,
                "refers_to": None,
                "source_message": text,
                "confidence": 0.99,
                "explanation": "Casual message or student banter without academic deadlines/events."
            })
            continue

        # 2. Category Detection
        category = "chatter"
        if re.search(r"\b(cancelled|canceled|cancel|no class|suspended|called off|chhutti|holiday|tutorial cancelled)\b", text, re.I):
            category = "cancellation"
        elif re.search(r"\b(postponed|postpone|rescheduled|reschedule|shifted|shifted to|shift ho gaya|delayed|preponed|venue changed|venue change|room changed|room change|moved to)\b", text, re.I):
            category = "schedule_change"
        elif re.search(r"\b(deadline|submit|submission|due date|due on|due|last date|form bharna|fill the form|google form|forms\.gle|portal close|portal closes|assignment|project report|upload on|hw|homework|registration closes|fee payment|pay before)\b", text, re.I):
            category = "deadline"
        elif re.search(r"\b(quiz|exam|midsem|endsem|test|lecture|session|orientation|meeting|sync|workshop|seminar|talk|tutorial|lab|review|presentation|hackathon|fest|ceremony|class)\b", text, re.I):
            category = "event"

        if category == "chatter":
            extracted_items.append({
                "message_id": m["id"],
                "category": "chatter",
                "title": None,
                "date": None,
                "original_date_phrase": None,
                "time": None,
                "venue": None,
                "course_or_subject": None,
                "audience": None,
                "refers_to": None,
                "source_message": text,
                "confidence": 0.95,
                "explanation": "Informal peer message without actionable deadline or event."
            })
            continue

        # 3. Course detection
        course = None
        for c_name, patterns in COURSES:
            if any(re.search(p, text, re.I) for p in patterns):
                course = c_name
                break

        if not course:
            # Check for dynamic course codes or title prefix before Quiz/Exam/Assignment/Lab
            dyn_m = re.search(r"\b([A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)*)\s+(?:Quiz|Assignment|Exam|Lab|Midsem|Endsem|Project|Tutorial)\b", text)
            if dyn_m:
                course = dyn_m.group(1).strip()
            else:
                acro_m = re.search(r"\b([A-Z]{2,4}\s*\d{0,3})\b", text)
                if acro_m and acro_m.group(1).strip() not in ("AM", "PM", "IST", "LMS", "CRC"):
                    course = acro_m.group(1).strip()

        # 4. Venue detection
        venue = None
        for vp in VENUES:
            vm = re.search(vp, text, re.I)
            if vm:
                venue = vm.group(0).strip()
                break

        # 5. Time detection
        time_val = None
        tm = re.search(r"(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)|\d{1,2}:\d{2}|\d{1,2}\s*baje)", text)
        if tm:
            time_val = parse_time_string(tm.group(0), text)

        # 6. Date detection (Fixed regex: prevent capturing hours as years)
        date_val = None
        date_phrase = None
        dm = re.search(r"\b(kal tak|kal subah|kal shaam|kal|parso|tarso|aaj|tomorrow|today|this Friday|next Monday|coming Friday|next week|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:\s+20\d{2})?|\d{1,2}[/-]\d{1,2}(?:[/-]20\d{2})?)\b", text, re.I)
        if dm:
            date_phrase = dm.group(0)
            resolved = resolve_date(None, date_phrase, sent_at, context_text=text)
            if resolved:
                date_val = resolved.strftime("%Y-%m-%d")

        # 7. Title synthesis
        kw_match = re.search(r"\b(Assignment\s*\d+|Quiz\s*\d+|Midsem(?:\s*Exam)?|Endsem(?:\s*Exam)?|Lab\s*\d+|Project Topic Approval|Orientation Session|Internal Project Review|Tutorial|Lecture|Team Selection Form)\b", text, re.I)
        kw = kw_match.group(0) if kw_match else None
        
        if kw:
            if course and course.lower() not in kw.lower():
                title = f"{course} {kw}"
            else:
                title = kw
        elif course:
            if category == "deadline":
                title = f"{course} Submission Deadline"
            elif category == "event":
                title = f"{course} Academic Session"
            elif category == "cancellation":
                title = f"{course} Session Cancelled"
            else:
                title = f"{course} Notice"
        else:
            words = text.split()[:5]
            title = " ".join(words)

        if category == "deadline" and not title.lower().endswith(("submission", "deadline", "form", "approval")):
            title += " Submission"

        refers_to = title.replace(" Cancelled", "").replace(" Postponed", "") if category in ("cancellation", "schedule_change") else None

        # Confidence calculation
        conf = 0.85
        if date_val: conf += 0.05
        if time_val: conf += 0.04
        if venue: conf += 0.04
        if "someone in group said" in text.lower() or "check with" in text.lower():
            conf = 0.65

        extracted_items.append({
            "message_id": m["id"],
            "category": category,
            "title": title.title(),
            "date": date_val,
            "original_date_phrase": date_phrase,
            "time": time_val,
            "venue": venue,
            "course_or_subject": course,
            "audience": "All Students",
            "refers_to": refers_to,
            "source_message": text,
            "confidence": round(min(conf, 0.98), 2),
            "explanation": f"Pattern detection identified {category} for {course or 'campus notice'} with date phrase '{date_phrase or 'unspecified'}'."
        })

    return extracted_items


def extract_with_gemini(
    messages: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    batch_size: int = 15
) -> List[Dict[str, Any]]:
    """
    Extracts structured entities using the official Google GenAI Python SDK (`google-genai`).
    Batches messages to ensure reliability and avoid token limits.
    """
    active_key = api_key or os.getenv("GEMINI_API_KEY")
    if not active_key or not active_key.strip():
        raise ValueError("Missing Gemini API Key. Please provide a key in Settings or via GEMINI_API_KEY.")

    active_model = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Import the official google-genai SDK
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=active_key.strip())
        use_new_sdk = True
    except ImportError:
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=active_key.strip())
            client = legacy_genai.GenerativeModel(active_model)
            use_new_sdk = False
        except ImportError as e:
            raise ImportError("Neither 'google-genai' nor 'google-generativeai' SDK is installed.") from e

    all_extracted_items: List[Dict[str, Any]] = []

    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        batch_payload = [
            {
                "id": m["id"],
                "sent_at": m["sent_at"].strftime("%Y-%m-%d %H:%M (%A)") if hasattr(m["sent_at"], "strftime") else str(m["sent_at"]),
                "sender": m.get("sender", "Unknown"),
                "text": m["text"]
            }
            for m in batch
        ]

        prompt_text = (
            f"{EXTRACTION_SYSTEM_PROMPT}\n\n"
            f"Here are the messages to extract from (JSON array):\n"
            f"{json.dumps(batch_payload, ensure_ascii=False, indent=2)}\n\n"
            f"Return ONLY valid JSON matching the schema."
        )

        try:
            if use_new_sdk:
                response = client.models.generate_content(
                    model=active_model,
                    contents=prompt_text,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0,
                    )
                )
                raw_json = response.text
            else:
                response = client.generate_content(
                    prompt_text,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.0}
                )
                raw_json = response.text

            cleaned_json = raw_json.strip()
            if cleaned_json.startswith("```json"):
                cleaned_json = cleaned_json[7:]
            if cleaned_json.startswith("```"):
                cleaned_json = cleaned_json[3:]
            if cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[:-3]

            parsed_data = json.loads(cleaned_json.strip())
            items = parsed_data.get("items", [])
            
            for it in items:
                mid = it.get("message_id")
                matching_msg = next((m for m in batch if m["id"] == mid), None)
                if matching_msg:
                    it["source_message"] = matching_msg["text"]

            all_extracted_items.extend(items)

        except Exception as e:
            logger.error(f"Error during Gemini extraction batch {i//batch_size}: {e}")
            raise RuntimeError(f"Gemini API Extraction failed on batch {i//batch_size + 1}: {str(e)}")

    return all_extracted_items


def extract_entities(
    messages: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    prefer_live_ai: bool = True
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Unified extraction router:
    - If prefer_live_ai and API key available: runs Gemini LLM.
    - If Gemini fails or no API key: smoothly falls back to multilingual heuristic extraction.
    Returns (extracted_items, engine_used).
    """
    active_key = api_key or os.getenv("GEMINI_API_KEY")
    if prefer_live_ai and active_key and active_key.strip():
        try:
            items = extract_with_gemini(messages, api_key=active_key, model_name=model_name)
            return items, f"Gemini ({model_name or 'gemini-2.5-flash'})"
        except Exception as e:
            logger.warning(f"Live Gemini extraction failed ({e}), falling back to campus heuristic engine.")
            items = extract_with_heuristics(messages)
            return items, "Multilingual Heuristic AI Engine (Gemini fallback)"

    items = extract_with_heuristics(messages)
    return items, "Multilingual Heuristic AI Engine"
