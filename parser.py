"""
Deadline Radar - Chat Parser Module
Handles parsing of WhatsApp and Telegram chat exports and plain text pastes.
Supports multi-line messages, date formats, and optional privacy anonymization.
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
import dateparser

# Regex patterns for WhatsApp and common chat exports
# 1. Android style: "10/11/26, 9:12 am - Priya: message" or "10/11/2026, 09:12 - Priya: message"
# 2. iOS style: "[10/11/26, 9:12:00 AM] Priya: message" or "[10/11/2026, 09:12:00] Priya: message"
# 3. Telegram style: "[10.11.2026 09:12] Priya: message" or "Priya, [10.11.26 09:12]: message"

CHAT_PATTERNS = [
    # Android 12h / 24h: "DD/MM/YY, HH:MM [am/pm] - Sender: Text"
    re.compile(
        r"^\[?(\d{1,2}[/\.-]\d{1,2}[/\.-]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?)\]?\s*[-–—]?\s*([^:]+?):\s*(.*)$"
    ),
    # Alternate format: "Sender, [DD/MM/YY HH:MM]: Text"
    re.compile(
        r"^([^,]+?),\s*\[?(\d{1,2}[/\.-]\d{1,2}[/\.-]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?)\]?:\s*(.*)$"
    ),
    # Timestamp without sender: "[DD/MM/YY, HH:MM] Text"
    re.compile(
        r"^\[?(\d{1,2}[/\.-]\d{1,2}[/\.-]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?)\]?\s*[-–—]?\s*(.*)$"
    ),
]

PHONE_PATTERN = re.compile(r"\+?\d[\d\s-]{8,}\d")
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
SYSTEM_MSG_PATTERN = re.compile(
    r"(Messages and calls are end-to-end encrypted|created group|created the group|added you|changed the subject|changed the group|\[System notification\]|joined via invite link|added .*|removed .*|<message_history_notice message>|<image omitted>|<video omitted>|<audio omitted>|<attached: .*>)",
    re.IGNORECASE
)


def detect_date_order(raw_text: str) -> str:
    """Auto-detects whether chat export dates are in MDY or DMY format."""
    matches = re.findall(r"\[?(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})", raw_text)
    if any(int(m[1]) > 12 for m in matches):
        return "MDY"
    if any(int(m[0]) > 12 for m in matches):
        return "DMY"
    return "DMY"


def parse_timestamp(date_str: str, time_str: str, default_date: datetime = None, date_order: str = "DMY") -> datetime:
    """Parse date and time strings with auto-detected date order."""
    clean_date = date_str.replace(".", "/").replace("-", "/").strip()
    
    # Expand 2-digit year to 20XX (e.g. 7/31/26 -> 7/31/2026)
    parts = clean_date.split("/")
    if len(parts) == 3 and len(parts[2]) == 2:
        clean_date = f"{parts[0]}/{parts[1]}/20{parts[2]}"
        
    combined = f"{clean_date} {time_str}".strip()
    
    parsed = dateparser.parse(
        combined,
        settings={
            "DATE_ORDER": date_order,
            "PREFER_DATES_FROM": "past",
            "RELATIVE_BASE": default_date or datetime.now(),
        }
    )
    if parsed and parsed.year < 2000:
        parsed = parsed.replace(year=parsed.year + 100)
    return parsed or (default_date or datetime.now())


def parse_chat(raw_text: str, anonymize: bool = False, base_date: datetime = None) -> List[Dict[str, Any]]:
    """
    Parses WhatsApp/Telegram chat export or raw lines into structured message records.
    
    Returns list of dicts:
    [
        {
            "id": int,
            "sender": str,
            "original_sender": str,
            "sent_at": datetime,
            "text": str,
            "raw": str
        },
        ...
    ]
    """
    if not raw_text or not raw_text.strip():
        return []

    lines = raw_text.splitlines()
    messages: List[Dict[str, Any]] = []
    sender_map: Dict[str, str] = {}
    current_time = base_date or datetime.now()
    date_order = detect_date_order(raw_text)

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Skip WhatsApp system messages
        if SYSTEM_MSG_PATTERN.search(stripped):
            continue

        matched = False
        
        # Match Pattern 1: standard timestamp - sender: text
        m1 = CHAT_PATTERNS[0].match(stripped)
        if m1:
            d_str, t_str, sender, text = m1.groups()
            sent_at = parse_timestamp(d_str, t_str, current_time, date_order=date_order)
            messages.append({
                "sender": sender.strip(),
                "original_sender": sender.strip(),
                "sent_at": sent_at,
                "text": text.strip(),
                "raw": stripped
            })
            matched = True
            continue

        # Match Pattern 2: sender, [timestamp]: text
        m2 = CHAT_PATTERNS[1].match(stripped)
        if m2:
            sender, d_str, t_str, text = m2.groups()
            sent_at = parse_timestamp(d_str, t_str, current_time, date_order=date_order)
            messages.append({
                "sender": sender.strip(),
                "original_sender": sender.strip(),
                "sent_at": sent_at,
                "text": text.strip(),
                "raw": stripped
            })
            matched = True
            continue

        # Match Pattern 3: timestamp text (no explicit sender)
        m3 = CHAT_PATTERNS[2].match(stripped)
        if m3:
            d_str, t_str, text = m3.groups()
            sent_at = parse_timestamp(d_str, t_str, current_time, date_order=date_order)
            messages.append({
                "sender": "Notice/Broadcast",
                "original_sender": "Notice/Broadcast",
                "sent_at": sent_at,
                "text": text.strip(),
                "raw": stripped
            })
            matched = True
            continue

        # If it doesn't match any timestamp header:
        # Check if it is a continuation of the previous message
        if messages:
            messages[-1]["text"] += " " + stripped
            messages[-1]["raw"] += "\n" + stripped
        else:
            # First line without timestamp: standalone message
            messages.append({
                "sender": "Unknown",
                "original_sender": "Unknown",
                "sent_at": current_time,
                "text": stripped,
                "raw": stripped
            })

    # Anonymization & ID assignment
    for i, msg in enumerate(messages):
        msg["id"] = i + 1
        
        # Check if sender contains indicative roles (CR, Admin, Prof) to preserve context
        orig_s = msg["original_sender"]
        is_role = bool(re.search(r"\b(cr|admin|ta|prof|faculty|coordinator|rep)\b", orig_s, re.IGNORECASE))
        
        if anonymize:
            if orig_s not in sender_map:
                if is_role:
                    sender_map[orig_s] = f"{orig_s.strip()}"
                else:
                    sender_map[orig_s] = f"Student {len(sender_map) + 1}"
            msg["sender"] = sender_map[orig_s]
            # Anonymize phone numbers and emails in body
            msg["text"] = PHONE_PATTERN.sub("<phone>", msg["text"])
            msg["text"] = EMAIL_PATTERN.sub("<email>", msg["text"])

    return messages
