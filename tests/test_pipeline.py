"""
Unit & Integration Test Suite for Deadline Radar
Covers chat parsing, date resolution, deduplication, conflict detection, and .ics export.
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date
from parser import parse_chat, parse_timestamp
from dates import resolve_date, parse_time_string, normalize_hinglish_date_phrase
from reconcile import reconcile_events
from ics_export import export_to_ics
from sample_data import SAMPLE_CHAT_RAW, SAMPLE_DETERMINISTIC_EXTRACTION


def test_parse_chat_formats():
    raw_sample = """[10/11/26, 09:15:20] Aman: Message 1
10/11/26, 09:20 am - Rohan: Message 2
with multiline continuation
"""
    messages = parse_chat(raw_sample, anonymize=False)
    assert len(messages) == 2
    assert messages[0]["sender"] == "Aman"
    assert "Message 1" in messages[0]["text"]
    assert "multiline continuation" in messages[1]["text"]


def test_anonymization():
    raw_sample = "10/11/26, 09:15 am - Student Guy: Call me at +91 98765 43210 or email test@iiit.ac.in"
    messages = parse_chat(raw_sample, anonymize=True)
    assert len(messages) == 1
    assert "Student" in messages[0]["sender"]
    assert "+91 98765 43210" not in messages[0]["text"]
    assert "<phone>" in messages[0]["text"]
    assert "<email>" in messages[0]["text"]


def test_hinglish_relative_dates():
    sent_at = datetime(2026, 11, 10, 10, 0)  # Tuesday
    
    # "kal" should resolve to sent_at + 1 day (Wednesday 11 Nov)
    d_kal = resolve_date(None, "kal tak", sent_at)
    assert d_kal == date(2026, 11, 11)
    
    # "parso" should resolve to sent_at + 2 days (Thursday 12 Nov)
    d_parso = resolve_date(None, "parso", sent_at)
    assert d_parso == date(2026, 11, 12)
    
    # Time string resolution
    t_10am = parse_time_string("10:00 AM")
    assert t_10am == "10:00"
    
    t_midnight = parse_time_string("11:59 PM")
    assert t_midnight == "23:59"
    
    t_baje = parse_time_string("5 baje shaam")
    assert t_baje == "17:00"


def test_reconciliation_pipeline():
    messages = parse_chat(SAMPLE_CHAT_RAW, anonymize=False)
    events = reconcile_events(SAMPLE_DETERMINISTIC_EXTRACTION, messages)
    
    # 1. Verify DBMS Assignment deduplicated into 1 event from 3 messages
    dbms_event = next(e for e in events if "DBMS" in e["title"])
    assert len(dbms_event["sources"]) >= 3
    assert dbms_event["date"] == date(2026, 11, 14)
    assert dbms_event["status"] == "Upcoming"
    
    # 2. Verify ML Quiz 1 postponement updated from Nov 14 to Nov 17
    quiz_event = next(e for e in events if "ML Quiz" in e["title"])
    assert quiz_event["status"] == "Updated"
    assert quiz_event["date"] == date(2026, 11, 17)
    assert len(quiz_event["sources"]) == 2
    
    # 3. Verify Speculative Rumor (ECE 202) was flagged for Human Review
    ece_event = next(e for e in events if "ECE 202" in e["title"])
    assert ece_event["has_conflict"] is True
    assert ece_event["needs_review"] is True
    assert ece_event["date"] == date(2026, 11, 20)  # Preserves official date
    
    # 4. Verify Cancellations
    cancelled_events = [e for e in events if e["status"] == "Cancelled"]
    assert len(cancelled_events) == 2


def test_ics_export():
    messages = parse_chat(SAMPLE_CHAT_RAW, anonymize=False)
    events = reconcile_events(SAMPLE_DETERMINISTIC_EXTRACTION, messages)
    
    ics_text = export_to_ics(events)
    assert "BEGIN:VCALENDAR" in ics_text
    assert "VERSION:2.0" in ics_text
    assert "Asia/Kolkata" in ics_text
    assert "UID:dr-" in ics_text
    # Cancelled events must not be in active calendar
    assert "Robotics Club Internal Project Review" not in ics_text
    assert "DBMS Assignment 2 Submission" in ics_text


if __name__ == "__main__":
    print("Running Pipeline Unit Tests...")
    test_parse_chat_formats()
    print("  [✓] test_parse_chat_formats PASSED")
    test_anonymization()
    print("  [✓] test_anonymization PASSED")
    test_hinglish_relative_dates()
    print("  [✓] test_hinglish_relative_dates PASSED")
    test_reconciliation_pipeline()
    print("  [✓] test_reconciliation_pipeline PASSED")
    test_ics_export()
    print("  [✓] test_ics_export PASSED")
    print("\nAll 5 test suites passed successfully!")
