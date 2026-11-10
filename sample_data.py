"""
Deadline Radar - Synthetic & Real IIIT-H M26 Campus Datasets
Contains:
1. Synthetic multi-issue benchmark dataset (16 notices with all edge cases)
2. M26 Product Management (Real IIIT-H WhatsApp Chat)
3. M26 Design Thinking (Real IIIT-H WhatsApp Chat)
4. M26 Business Fundamentals (Real IIIT-H WhatsApp Chat)
5. M26 AI for Product Managers (Real IIIT-H WhatsApp Chat)
6. All 4 M26 Courses Combined Multi-Channel Feed
"""

import os
from typing import List, Dict, Any

# Base synthetic benchmark chat (16 notices)
SAMPLE_CHAT_RAW = """[10/11/26, 09:15:20] Aman (CR): @all Important: DBMS Assignment 2 submission deadline is 14th Nov 11:59 PM on LMS portal. No extensions will be given.
[10/11/26, 09:22:45] Rohan: Guys attendance ka proxy laga dena please lecture mein
[10/11/26, 10:05:12] Prof. Sharma: ML Quiz 1 scheduled for this Friday 14 Nov at 10:00 AM in Audi 2. Syllabus is Modules 1 and 2.
[10/11/26, 11:30:00] Aman (CR): Reminder: DBMS Assignment 2 portal closes 14 Nov at 23:59. Pls submit early.
[10/11/26, 14:15:33] Sneha: Koi canteen chal raha hai kya lunch ke liye?
[10/11/26, 16:40:10] Prof. Sharma: Notice: ML Quiz 1 has been postponed to next Monday 17 Nov at 10:00 AM due to faculty senate meeting. Venue remains Audi 2.
[10/11/26, 17:05:00] Robotics Club: Robotics Club internal project review cancelled for today. Next sync will be notified later.
[10/11/26, 18:20:15] TA Priya: Operating Systems Lab 4 venue changed from Lab 1 to Room 302 tomorrow at 2:00 PM.
[10/11/26, 19:45:00] Vikram (ECE Rep): ECE 202 Midsem Exam announced for 20th Nov at 9:30 AM in Exam Hall 1.
[10/11/26, 20:10:18] Kabir: Bro Vikram check with HOD once, someone in group said ECE 202 exam is shifted to 24th Nov because of Felicity tech fest?
[10/11/26, 21:00:44] Ananya: GSoC 2027 orientation session next week, date and venue TBA by Open Source Club.
[10/11/26, 21:30:12] Rahul: Bhai quiz ka kya scene hai kal padhna hai ya nahi?
[10/11/26, 22:15:00] Divya: Kal tak Cloud Computing project topic approval form bharna hai mandatory, Google form link pinned.
[10/11/26, 22:45:50] Aman (CR): Final reminder: DBMS Assignment 2 is due on 14th Nov 11:59 PM.
[10/11/26, 23:10:05] Mohit: yaar mess ka food aaj bohot bekar tha lol
[10/11/26, 23:30:20] Prof. Verma: Computer Networks tutorial cancelled for tomorrow morning.
"""

# Pre-computed deterministic extraction for the 16-message benchmark
SAMPLE_DETERMINISTIC_EXTRACTION: List[Dict[str, Any]] = [
    {
        "message_id": 1,
        "category": "deadline",
        "title": "DBMS Assignment 2 Submission",
        "date": "2026-11-14",
        "original_date_phrase": "14th Nov",
        "time": "23:59",
        "venue": "LMS Portal",
        "course_or_subject": "DBMS",
        "audience": "All Students",
        "refers_to": None,
        "source_message": "@all Important: DBMS Assignment 2 submission deadline is 14th Nov 11:59 PM on LMS portal. No extensions will be given.",
        "confidence": 0.98,
        "explanation": "Clear deadline announcement from CR with specific date, time, and submission portal."
    },
    {
        "message_id": 2,
        "category": "chatter",
        "title": None,
        "date": None,
        "original_date_phrase": None,
        "time": None,
        "venue": None,
        "course_or_subject": None,
        "audience": None,
        "refers_to": None,
        "source_message": "Guys attendance ka proxy laga dena please lecture mein",
        "confidence": 0.99,
        "explanation": "Informal peer message requesting attendance proxy; no academic deadline or event."
    },
    {
        "message_id": 3,
        "category": "event",
        "title": "ML Quiz 1",
        "date": "2026-11-14",
        "original_date_phrase": "this Friday 14 Nov",
        "time": "10:00",
        "venue": "Audi 2",
        "course_or_subject": "Machine Learning",
        "audience": "ML Students",
        "refers_to": None,
        "source_message": "ML Quiz 1 scheduled for this Friday 14 Nov at 10:00 AM in Audi 2. Syllabus is Modules 1 and 2.",
        "confidence": 0.96,
        "explanation": "Official faculty announcement for an academic quiz with explicit date, time, and venue."
    },
    {
        "message_id": 4,
        "category": "deadline",
        "title": "DBMS Assignment 2 Submission",
        "date": "2026-11-14",
        "original_date_phrase": "14 Nov",
        "time": "23:59",
        "venue": "LMS Portal",
        "course_or_subject": "DBMS",
        "audience": "All Students",
        "refers_to": "DBMS Assignment 2 Submission",
        "source_message": "Reminder: DBMS Assignment 2 portal closes 14 Nov at 23:59. Pls submit early.",
        "confidence": 0.97,
        "explanation": "Reminder repeat for the earlier announced DBMS Assignment 2 deadline."
    },
    {
        "message_id": 5,
        "category": "chatter",
        "title": None,
        "date": None,
        "original_date_phrase": None,
        "time": None,
        "venue": None,
        "course_or_subject": None,
        "audience": None,
        "refers_to": None,
        "source_message": "Koi canteen chal raha hai kya lunch ke liye?",
        "confidence": 0.99,
        "explanation": "Casual lunch query; irrelevant chatter."
    },
    {
        "message_id": 6,
        "category": "schedule_change",
        "title": "ML Quiz 1 Postponed",
        "date": "2026-11-17",
        "original_date_phrase": "next Monday 17 Nov",
        "time": "10:00",
        "venue": "Audi 2",
        "course_or_subject": "Machine Learning",
        "audience": "ML Students",
        "refers_to": "ML Quiz 1",
        "source_message": "Notice: ML Quiz 1 has been postponed to next Monday 17 Nov at 10:00 AM due to faculty senate meeting. Venue remains Audi 2.",
        "confidence": 0.97,
        "explanation": "Authoritative postponement from Prof. Sharma shifting ML Quiz 1 to Nov 17."
    },
    {
        "message_id": 7,
        "category": "cancellation",
        "title": "Robotics Club Internal Project Review",
        "date": "2026-11-10",
        "original_date_phrase": "today",
        "time": None,
        "venue": None,
        "course_or_subject": "Robotics Club",
        "audience": "Club Members",
        "refers_to": "Robotics Club internal project review",
        "source_message": "Robotics Club internal project review cancelled for today. Next sync will be notified later.",
        "confidence": 0.94,
        "explanation": "Official club notice cancelling today's project review meeting."
    },
    {
        "message_id": 8,
        "category": "schedule_change",
        "title": "OS Lab 4 Venue Change",
        "date": "2026-11-11",
        "original_date_phrase": "tomorrow",
        "time": "14:00",
        "venue": "Room 302",
        "course_or_subject": "Operating Systems",
        "audience": "OS Lab Students",
        "refers_to": "Operating Systems Lab 4",
        "source_message": "Operating Systems Lab 4 venue changed from Lab 1 to Room 302 tomorrow at 2:00 PM.",
        "confidence": 0.95,
        "explanation": "TA announcement shifting lab venue to Room 302 for tomorrow 2 PM."
    },
    {
        "message_id": 9,
        "category": "event",
        "title": "ECE 202 Midsem Exam",
        "date": "2026-11-20",
        "original_date_phrase": "20th Nov",
        "time": "09:30",
        "venue": "Exam Hall 1",
        "course_or_subject": "ECE 202",
        "audience": "ECE Students",
        "refers_to": None,
        "source_message": "ECE 202 Midsem Exam announced for 20th Nov at 9:30 AM in Exam Hall 1.",
        "confidence": 0.95,
        "explanation": "Official representative exam notice with date, time, and room."
    },
    {
        "message_id": 10,
        "category": "schedule_change",
        "title": "ECE 202 Midsem Date Conflict",
        "date": "2026-11-24",
        "original_date_phrase": "24th Nov",
        "time": None,
        "venue": None,
        "course_or_subject": "ECE 202",
        "audience": "ECE Students",
        "refers_to": "ECE 202 Midsem Exam",
        "source_message": "Bro Vikram check with HOD once, someone in group said ECE 202 exam is shifted to 24th Nov because of Felicity tech fest?",
        "confidence": 0.60,
        "explanation": "Student rumour/speculation alleging postponement to 24th Nov. Unconfirmed hearsay; requires human review."
    },
    {
        "message_id": 11,
        "category": "event",
        "title": "GSoC 2027 Orientation Session",
        "date": None,
        "original_date_phrase": "next week",
        "time": None,
        "venue": "TBA",
        "course_or_subject": "Open Source Club",
        "audience": "All Students",
        "refers_to": None,
        "source_message": "GSoC 2027 orientation session next week, date and venue TBA by Open Source Club.",
        "confidence": 0.72,
        "explanation": "Upcoming event confirmed but exact date is TBA. Needs review to assign date."
    },
    {
        "message_id": 12,
        "category": "chatter",
        "title": None,
        "date": None,
        "original_date_phrase": "kal",
        "time": None,
        "venue": None,
        "course_or_subject": None,
        "audience": None,
        "refers_to": None,
        "source_message": "Bhai quiz ka kya scene hai kal padhna hai ya nahi?",
        "confidence": 0.92,
        "explanation": "Informal student query about studying; not a notice."
    },
    {
        "message_id": 13,
        "category": "deadline",
        "title": "Cloud Computing Project Topic Approval",
        "date": "2026-11-11",
        "original_date_phrase": "Kal tak",
        "time": "23:59",
        "venue": "Google Form",
        "course_or_subject": "Cloud Computing",
        "audience": "Cloud Computing Students",
        "refers_to": None,
        "source_message": "Kal tak Cloud Computing project topic approval form bharna hai mandatory, Google form link pinned.",
        "confidence": 0.93,
        "explanation": "Actionable mandatory form submission due tomorrow."
    },
    {
        "message_id": 14,
        "category": "deadline",
        "title": "DBMS Assignment 2 Submission",
        "date": "2026-11-14",
        "original_date_phrase": "14th Nov",
        "time": "23:59",
        "venue": "LMS Portal",
        "course_or_subject": "DBMS",
        "audience": "All Students",
        "refers_to": "DBMS Assignment 2 Submission",
        "source_message": "Final reminder: DBMS Assignment 2 is due on 14th Nov 11:59 PM.",
        "confidence": 0.99,
        "explanation": "Third repeated announcement for DBMS Assignment 2."
    },
    {
        "message_id": 15,
        "category": "chatter",
        "title": None,
        "date": None,
        "original_date_phrase": "aaj",
        "time": None,
        "venue": None,
        "course_or_subject": None,
        "audience": None,
        "refers_to": None,
        "source_message": "yaar mess ka food aaj bohot bekar tha lol",
        "confidence": 0.99,
        "explanation": "Student commentary on hostel food; pure chatter."
    },
    {
        "message_id": 16,
        "category": "cancellation",
        "title": "Computer Networks Tutorial",
        "date": "2026-11-11",
        "original_date_phrase": "tomorrow morning",
        "time": "09:00",
        "venue": None,
        "course_or_subject": "Computer Networks",
        "audience": "CN Students",
        "refers_to": "Computer Networks tutorial",
        "source_message": "Computer Networks tutorial cancelled for tomorrow morning.",
        "confidence": 0.95,
        "explanation": "Faculty notice cancelling tomorrow's Computer Networks tutorial."
    }
]


def load_real_chat_text(course_folder_name: str) -> str:
    """Loads chat.txt from data/real_chats/{course_folder_name}."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "data", "real_chats", course_folder_name, "chat.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


# Real IIIT-H M26 Course Datasets Dictionary
REAL_COURSE_DATASETS = {
    "m26_pm": {
        "title": "📚 M26: Product Management (Real Chat)",
        "folder": "M26_Product_Management",
        "description": "Team selection Google Form deadline (Aug 7 11:59 PM), team matching polls, and Moodle project guidelines.",
        "deterministic_extractions": [
            {
                "message_id": 5,
                "category": "deadline",
                "title": "PM Course Team Selection Form Submission",
                "date": "2026-08-07",
                "original_date_phrase": "7th August, 11:59 PM",
                "time": "23:59",
                "venue": "Google Forms (forms.gle/SHEswvz3RnQHWHVXA)",
                "course_or_subject": "Product Management",
                "audience": "All M26 Students",
                "refers_to": None,
                "confidence": 0.98,
                "explanation": "Official deadline announcement to submit Google Form for PM team selection."
            },
            {
                "message_id": 12,
                "category": "deadline",
                "title": "PM Course Team Selection Form Submission",
                "date": "2026-08-07",
                "original_date_phrase": "7th August",
                "time": "23:59",
                "venue": "Google Forms",
                "course_or_subject": "Product Management",
                "audience": "All M26 Students",
                "refers_to": "PM Course Team Selection Form Submission",
                "confidence": 0.97,
                "explanation": "Follow-up reminder regarding team selection submissions."
            }
        ]
    },
    "m26_dt": {
        "title": "📚 M26: Design Thinking (Real Chat)",
        "folder": "M26_Design_Thinking",
        "description": "Keshav (TA) announcement for Moodle Assignment 1 (Aug 16 11:59 PM), Lecture 1-4 slides, and 3-member team form.",
        "deterministic_extractions": [
            {
                "message_id": 8,
                "category": "deadline",
                "title": "Design Thinking Assignment 1 Submission",
                "date": "2026-08-16",
                "original_date_phrase": "16th August 11:59 PM",
                "time": "23:59",
                "venue": "Moodle Portal",
                "course_or_subject": "Design Thinking",
                "audience": "All Students",
                "refers_to": None,
                "confidence": 0.98,
                "explanation": "TA Keshav announced Assignment 1 updated on Moodle with Aug 16 deadline."
            },
            {
                "message_id": 14,
                "category": "deadline",
                "title": "Design Thinking Group Project Team Form",
                "date": "2026-08-18",
                "original_date_phrase": "Tuesday",
                "time": "23:59",
                "venue": "Google Form",
                "course_or_subject": "Design Thinking",
                "audience": "3-Member Teams",
                "refers_to": None,
                "confidence": 0.92,
                "explanation": "Mandatory individual form submission for 3-member project groups."
            }
        ]
    },
    "m26_bf": {
        "title": "📚 M26: Business Fundamentals (Real Chat)",
        "folder": "M26_Business_Fundamentals",
        "description": "Bhumii (Senior) lecture notices (2:00 PM - 5:00 PM), punctuality rules, and venue shift to SH3 Vindhya A2.",
        "deterministic_extractions": [
            {
                "message_id": 2,
                "category": "event",
                "title": "Business Fundamentals Lecture (Punctuality Mandatory)",
                "date": "2026-08-01",
                "original_date_phrase": "tomorrow",
                "time": "14:00",
                "venue": "SH3, 2nd Floor, Vindhya A6",
                "course_or_subject": "Business Fundamentals",
                "audience": "All PDM 26",
                "refers_to": None,
                "confidence": 0.97,
                "explanation": "Official class announcement from Bhumii (Senior) 2:00 PM - 5:00 PM."
            },
            {
                "message_id": 6,
                "category": "schedule_change",
                "title": "Business Fundamentals Venue Shift",
                "date": "2026-08-01",
                "original_date_phrase": "today",
                "time": "14:00",
                "venue": "SH3, Vindhya A2, 2nd Floor",
                "course_or_subject": "Business Fundamentals",
                "audience": "All PDM 26",
                "refers_to": "Business Fundamentals Lecture (Punctuality Mandatory)",
                "confidence": 0.95,
                "explanation": "Venue update: class shifted to Vindhya A2, 2nd Floor."
            }
        ]
    },
    "m26_ai_pm": {
        "title": "📚 M26: AI for Product Managers (Real Chat)",
        "folder": "M26_AI_for_Product_Managers",
        "description": "Raman Sir's lecture in H101 at 8:30 AM, holiday rescheduling announcements, and online class polls.",
        "deterministic_extractions": [
            {
                "message_id": 3,
                "category": "event",
                "title": "AI for Product Managers Lecture (Raman Sir)",
                "date": "2026-09-26",
                "original_date_phrase": "today",
                "time": "08:30",
                "venue": "H101",
                "course_or_subject": "AI for Product Managers",
                "audience": "All PDM 26",
                "refers_to": None,
                "confidence": 0.96,
                "explanation": "Official TA notice: class happening in H101 at 8:30 AM."
            },
            {
                "message_id": 8,
                "category": "schedule_change",
                "title": "AI for PM Class Reschedule Notice",
                "date": "2026-10-05",
                "original_date_phrase": "advance notice",
                "time": None,
                "venue": "Moodle / H101",
                "course_or_subject": "AI for Product Managers",
                "audience": "All PDM 26",
                "refers_to": "AI for Product Managers Lecture",
                "confidence": 0.88,
                "explanation": "Rescheduling and holiday notification communicated in advance."
            }
        ]
    }
}


def get_all_real_chats_combined() -> str:
    """Concatenates all 4 real course chats chronologically."""
    combined = []
    for k in ["m26_pm", "m26_dt", "m26_bf", "m26_ai_pm"]:
        txt = load_real_chat_text(REAL_COURSE_DATASETS[k]["folder"])
        if txt:
            combined.append(f"--- {REAL_COURSE_DATASETS[k]['title']} ---\n" + txt)
    return "\n\n".join(combined)
