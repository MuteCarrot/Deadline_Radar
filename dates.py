"""
Deadline Radar - Date & Time Parsing & Resolution Module
Resolves absolute and relative date/time expressions in English, Hindi, and Hinglish.
Always resolves relative dates against the message's sent_at timestamp.
Default Timezone: Asia/Kolkata (IST).
"""

import re
from datetime import datetime, date, timedelta, time
from typing import Optional, Tuple, Dict, Any
import dateparser
import pytz

IST = pytz.timezone("Asia/Kolkata")

# Hinglish relative date dictionary
# Maps common Hindi/Hinglish terms to day offsets
HINGLISH_OFFSETS = {
    r"\baaj\b": 0,
    r"\btoday\b": 0,
    r"\bkal\b": 1,          # kal can mean yesterday or tomorrow, in campus announcements it almost always means tomorrow
    r"\btomorrow\b": 1,
    r"\bparso[n]?\b": 2,    # day after tomorrow
    r"\btarso[n]?\b": 3,    # 3 days later
}

# Hinglish time of day hints
TIME_OF_DAY_HINTS = [
    (r"\b(subah|morning|early morning)\b", "AM"),
    (r"\b(dopahar|afternoon)\b", "PM"),
    (r"\b(shaam|sham|evening)\b", "PM"),
    (r"\b(raat|night)\b", "PM"),
]


def normalize_hinglish_date_phrase(phrase: str) -> Tuple[Optional[int], str]:
    """
    Checks if phrase contains Hinglish day words like 'kal', 'parso', 'aaj'.
    Returns (day_offset, cleaned_phrase).
    """
    p_lower = phrase.lower().strip()
    
    for pattern, offset in HINGLISH_OFFSETS.items():
        if re.search(pattern, p_lower):
            # If it's "kal tak" or "kal subah", we know it's +1 day
            return offset, p_lower

    return None, p_lower


def parse_time_string(time_str: Optional[str], text_hint: str = "") -> Optional[str]:
    """
    Normalizes time to HH:MM (24-hour format).
    e.g. '10 am' -> '10:00', '5 pm' -> '17:00', '5 baje shaam' -> '17:00', '11:59 pm' -> '23:59'
    """
    if not time_str and not text_hint:
        return None

    raw = (time_str or "").strip()
    hint = (text_hint or "").lower()

    # Look for Hindi "X baje"
    baje_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*baje", f"{raw} {hint}")
    if baje_match:
        hour = int(baje_match.group(1))
        minute = int(baje_match.group(2) or 0)
        is_pm = any(re.search(p, hint) for p, tod in TIME_OF_DAY_HINTS if tod == "PM")
        is_am = any(re.search(p, hint) for p, tod in TIME_OF_DAY_HINTS if tod == "AM")
        
        if is_pm and hour < 12:
            hour += 12
        elif is_am and hour == 12:
            hour = 0
        elif hour <= 7 and not is_am:  # e.g., 5 baje typically means 5 PM in campus context unless morning stated
            hour += 12
            
        return f"{hour:02d}:{minute:02d}"

    if not raw:
        return None

    # Check for direct HH:MM 24h or 12h
    clean_raw = raw.replace(".", ":")
    parsed_dt = dateparser.parse(clean_raw, settings={"PREFER_DATES_FROM": "future"})
    if parsed_dt:
        return parsed_dt.strftime("%H:%M")

    # Regex for standard 10 am / 11:59 pm
    m = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", raw, re.IGNORECASE)
    if m:
        h = int(m.group(1))
        minute = int(m.group(2) or 0)
        meridiem = (m.group(3) or "").lower()
        if meridiem == "pm" and h < 12:
            h += 12
        elif meridiem == "am" and h == 12:
            h = 0
        return f"{h:02d}:{minute:02d}"

    return None


def resolve_date(
    date_iso: Optional[str],
    date_phrase: Optional[str],
    sent_at: datetime,
    context_text: str = ""
) -> Optional[date]:
    """
    Resolves date expression into a standard python datetime.date.
    Prioritizes:
    1. Valid ISO date YYYY-MM-DD
    2. Hinglish relative offsets (kal = sent_at + 1, parso = sent_at + 2)
    3. dateparser with sent_at as RELATIVE_BASE and DMY order
    4. Context text scanning if phrase is missing
    """
    # 1. Try ISO date if provided and valid
    if date_iso:
        date_iso_clean = str(date_iso).strip()
        try:
            return datetime.strptime(date_iso_clean, "%Y-%m-%d").date()
        except ValueError:
            pass

    # 2. Check phrase or context text
    phrase = (date_phrase or "").strip()
    if not phrase:
        phrase = context_text

    if not phrase:
        return None

    # Check Hinglish offset
    offset, cleaned = normalize_hinglish_date_phrase(phrase)
    if offset is not None:
        base_d = sent_at.date() if isinstance(sent_at, datetime) else sent_at
        return base_d + timedelta(days=offset)

    # 3. Use dateparser with relative base
    # Handle "coming Friday", "next Monday", "15th Nov", etc.
    settings = {
        "RELATIVE_BASE": sent_at if isinstance(sent_at, datetime) else datetime.combine(sent_at, time.min),
        "PREFER_DATES_FROM": "future",
        "DATE_ORDER": "DMY",
        "TIMEZONE": "Asia/Kolkata",
        "RETURN_AS_TIMEZONE_AWARE": False,
    }
    
    parsed = dateparser.parse(phrase, settings=settings)
    if parsed:
        return parsed.date()

    return None

