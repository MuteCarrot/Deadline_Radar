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

export interface AnnotatedMessage {
  id: number;
  sender: string;
  sent_at: string;
  text: string;
  category: 'deadline' | 'event' | 'schedule_change' | 'cancellation' | 'chatter';
  title: string | null;
  event_id: string | null;
  confidence: number;
  is_event_source: boolean;
  has_conflict: boolean;
  conflict_reason: string | null;
  date: string | null;
  time: string | null;
  venue: string | null;
}

export interface OverviewMetrics {
  active_deadlines: number;
  upcoming_events: number;
  updated_postponed: number;
  needs_review: number;
  total_messages_parsed: number;
  annotated_sources?: number;
}

export interface OverviewData {
  metrics: OverviewMetrics;
  upcoming_agenda: EventItem[];
  recent_updates: EventItem[];
  needs_review_items: EventItem[];
  active_dataset: string;
  is_demo_mode: boolean;
  engine_used?: string;
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
