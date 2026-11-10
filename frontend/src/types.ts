export interface SourceDetail {
  msg_id: number;
  sender: string;
  sent_at: string;
  text: string;
}

export interface EventItem {
  id: string;
  title: string;
  category: 'deadline' | 'event' | 'schedule_change' | 'cancellation';
  status: 'Upcoming' | 'Updated' | 'Cancelled' | 'Needs Review';
  date: string | null; // "YYYY-MM-DD"
  time: string | null; // "HH:MM"
  venue: string | null;
  course_or_subject: string | null;
  audience: string | null;
  confidence: number;
  needs_review: boolean;
  has_conflict: boolean;
  conflict_reason: string | null;
  sources: number[];
  source_details: SourceDetail[];
  history: string[];
  confirmed: boolean;
}

export interface OverviewMetrics {
  active_deadlines: number;
  upcoming_events: number;
  updated_postponed: number;
  needs_review: number;
  total_messages_parsed: number;
}

export interface OverviewData {
  metrics: OverviewMetrics;
  upcoming_agenda: EventItem[];
  recent_updates: EventItem[];
  needs_review_items: EventItem[];
  active_dataset: string;
  is_demo_mode: boolean;
}

export interface SourceIntegration {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'available' | 'coming_soon';
  status_label: string;
  details: string;
  instructions: string;
}

export interface AppSettings {
  model: string;
  has_api_key: boolean;
  timezone: string;
  active_dataset: string;
}

