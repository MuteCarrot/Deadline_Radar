"""
Deadline Radar - AI Extraction Engine
Powered by the official Google GenAI Python SDK.
Extracts structured deadline and event entities from multilingual campus chats:
English, Hindi, Roman Hindi, and Hinglish.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

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
        raise ValueError("Missing Gemini API Key. Please provide a key in the sidebar or via GEMINI_API_KEY.")

    active_model = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Import the official google-genai SDK
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=active_key.strip())
        use_new_sdk = True
    except ImportError:
        # Fallback to legacy google-generativeai if new SDK not available
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
                # Official Google GenAI SDK v0.1+
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
                # Legacy SDK fallback
                response = client.generate_content(
                    prompt_text,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.0}
                )
                raw_json = response.text

            # Clean and parse JSON
            cleaned_json = raw_json.strip()
            if cleaned_json.startswith("```json"):
                cleaned_json = cleaned_json[7:]
            if cleaned_json.startswith("```"):
                cleaned_json = cleaned_json[3:]
            if cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[:-3]

            parsed_data = json.loads(cleaned_json.strip())
            items = parsed_data.get("items", [])
            
            # Attach source_message text for provenance
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

