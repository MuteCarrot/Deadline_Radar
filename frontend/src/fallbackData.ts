import { EventItem, OverviewData, SourceIntegration, AppSettings } from './types';

export const FALLBACK_EVENTS: EventItem[] = [
  {
    id: "evt-cc-topic",
    title: "Cloud Computing Project Topic Approval",
    category: "deadline",
    status: "Upcoming",
    date: "2026-11-11",
    time: "23:59",
    venue: "Google Form (pinned link)",
    course_or_subject: "Cloud Computing",
    audience: "All Students",
    confidence: 0.95,
    needs_review: false,
    has_conflict: false,
    conflict_reason: null,
    sources: [13],
    source_details: [
      {
        msg_id: 13,
        sender: "Divya",
        sent_at: "2026-11-10 22:15",
        text: "Kal tak Cloud Computing project topic approval form bharna hai mandatory, Google form link pinned."
      }
    ],
    history: ["Created from Announcement"],
    confirmed: true
  },
  {
    id: "evt-dbms-a2",
    title: "DBMS Assignment 2 Submission",
    category: "deadline",
    status: "Upcoming",
    date: "2026-11-14",
    time: "23:59",
    venue: "LMS Portal",
    course_or_subject: "DBMS",
    audience: "All Students",
    confidence: 0.98,
    needs_review: false,
    has_conflict: false,
    conflict_reason: null,
    sources: [1, 4, 14],
    source_details: [
      {
        msg_id: 1,
        sender: "Aman (CR)",
        sent_at: "2026-11-10 09:15",
        text: "@all Important: DBMS Assignment 2 submission deadline is 14th Nov 11:59 PM on LMS portal. No extensions will be given."
      },
      {
        msg_id: 4,
        sender: "Aman (CR)",
        sent_at: "2026-11-10 11:30",
        text: "Reminder: DBMS Assignment 2 portal closes 14 Nov at 23:59. Pls submit early."
      },
      {
        msg_id: 14,
        sender: "Aman (CR)",
        sent_at: "2026-11-10 22:45",
        text: "Final reminder: DBMS Assignment 2 is due on 14th Nov 11:59 PM."
      }
    ],
    history: [
      "Created from Announcement",
      "Merged reminder from Aman (CR) at 2026-11-10 11:30",
      "Merged reminder from Aman (CR) at 2026-11-10 22:45"
    ],
    confirmed: true
  },
  {
    id: "evt-ml-q1",
    title: "ML Quiz 1",
    category: "event",
    status: "Updated",
    date: "2026-11-17",
    time: "10:00",
    venue: "Audi 2",
    course_or_subject: "Machine Learning",
    audience: "ML Students",
    confidence: 0.96,
    needs_review: false,
    has_conflict: false,
    conflict_reason: null,
    sources: [3, 6],
    source_details: [
      {
        msg_id: 3,
        sender: "Prof. Sharma",
        sent_at: "2026-11-10 10:05",
        text: "ML Quiz 1 scheduled for this Friday 14 Nov at 10:00 AM in Audi 2. Syllabus is Modules 1 and 2."
      },
      {
        msg_id: 6,
        sender: "Prof. Sharma",
        sent_at: "2026-11-10 16:40",
        text: "Notice: ML Quiz 1 has been postponed to next Monday 17 Nov at 10:00 AM due to faculty senate meeting. Venue remains Audi 2."
      }
    ],
    history: [
      "Created from Announcement",
      "Postponed from 2026-11-14 to 2026-11-17 by Prof. Sharma at 2026-11-10 16:40"
    ],
    confirmed: true
  },
  {
    id: "evt-robotics-review",
    title: "Robotics Club Internal Project Review",
    category: "event",
    status: "Cancelled",
    date: "2026-11-19",
    time: "14:00",
    venue: "CRC Room",
    course_or_subject: "Robotics Club",
    audience: "Club Members",
    confidence: 0.95,
    needs_review: false,
    has_conflict: false,
    conflict_reason: null,
    sources: [7],
    source_details: [
      {
        msg_id: 7,
        sender: "Robotics Club",
        sent_at: "2026-11-10 17:05",
        text: "Robotics Club internal project review cancelled for today. Next sync will be notified later."
      }
    ],
    history: [
      "Created from Announcement",
      "Cancelled by Robotics Club at 2026-11-10 17:05"
    ],
    confirmed: false
  },
  {
    id: "evt-ece-midsem",
    title: "ECE 202 Midsem Exam",
    category: "event",
    status: "Needs Review",
    date: "2026-11-20",
    time: "09:30",
    venue: "Exam Hall 1",
    course_or_subject: "ECE 202",
    audience: "ECE Students",
    confidence: 0.72,
    needs_review: true,
    has_conflict: true,
    conflict_reason: "Conflicting dates reported: Vikram (ECE Rep) announced 20 Nov at 9:30 AM, while Kabir reported peer claim of shift to 24 Nov due to Felicity fest.",
    sources: [9, 10],
    source_details: [
      {
        msg_id: 9,
        sender: "Vikram (ECE Rep)",
        sent_at: "2026-11-10 19:45",
        text: "ECE 202 Midsem Exam announced for 20th Nov at 9:30 AM in Exam Hall 1."
      },
      {
        msg_id: 10,
        sender: "Kabir",
        sent_at: "2026-11-10 20:10",
        text: "Bro Vikram check with HOD once, someone in group said ECE 202 exam is shifted to 24th Nov because of Felicity tech fest?"
      }
    ],
    history: [
      "Created from Announcement",
      "Conflicting date update flagged: Peer Kabir claims possible shift to 24 Nov (needs human review)"
    ],
    confirmed: false
  },
  {
    id: "evt-gsoc-session",
    title: "GSoC 2027 Orientation Session",
    category: "event",
    status: "Upcoming",
    date: "2026-11-21",
    time: null,
    venue: "TBA",
    course_or_subject: "Open Source Club",
    audience: "All Interested Students",
    confidence: 0.88,
    needs_review: false,
    has_conflict: false,
    conflict_reason: null,
    sources: [11],
    source_details: [
      {
        msg_id: 11,
        sender: "Ananya",
        sent_at: "2026-11-10 21:00",
        text: "GSoC 2027 orientation session next week, date and venue TBA by Open Source Club."
      }
    ],
    history: ["Created from Announcement"],
    confirmed: true
  }
];

export const FALLBACK_OVERVIEW: OverviewData = {
  metrics: {
    active_deadlines: 2,
    upcoming_events: 3,
    updated_postponed: 1,
    needs_review: 1,
    total_messages_parsed: 16
  },
  upcoming_agenda: FALLBACK_EVENTS.filter(e => e.status !== 'Cancelled'),
  recent_updates: FALLBACK_EVENTS.filter(e => e.status === 'Updated'),
  needs_review_items: FALLBACK_EVENTS.filter(e => e.needs_review || e.has_conflict),
  active_dataset: "Synthetic Multi-Issue Benchmark (16 notices)",
  is_demo_mode: true
};

export const FALLBACK_SOURCES: SourceIntegration[] = [
  {
    id: "gmail",
    name: "Gmail Broadcasts",
    type: "email",
    status: "active",
    status_label: "Syncing (2 new)",
    details: "Connected to academic and club digest mailing lists.",
    instructions: "Official university notices, grading circulars, and departmental announcements."
  },
  {
    id: "telegram",
    name: "Telegram Channels",
    type: "chat",
    status: "active",
    status_label: "Live",
    details: "Monitoring registered club broadcast channels and batch groups.",
    instructions: "Reads batch announcements from student council and cultural/technical clubs."
  },
  {
    id: "whatsapp",
    name: "WhatsApp Chat Exports",
    type: "upload",
    status: "available",
    status_label: "Available",
    details: "Drop your exported .txt or paste raw messages anytime.",
    instructions: "Export any WhatsApp group chat (without media) and drop it into the Import modal."
  }
];

export const FALLBACK_SETTINGS: AppSettings = {
  model: "gemini-2.5-flash",
  has_api_key: false,
  timezone: "Asia/Kolkata (IST)",
  active_dataset: "Synthetic Multi-Issue Benchmark (16 notices)"
};

