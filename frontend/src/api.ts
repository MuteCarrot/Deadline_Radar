import { EventItem, OverviewData, SourceIntegration, AppSettings, AnnotatedMessage } from './types';
import {
  FALLBACK_EVENTS,
  FALLBACK_OVERVIEW,
  FALLBACK_SOURCES,
  FALLBACK_SETTINGS,
  FALLBACK_MESSAGES,
} from './fallbackData';

const BASE_URL = '/api';

export async function fetchOverview(): Promise<OverviewData> {
  try {
    const res = await fetch(`${BASE_URL}/overview`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('API fetchOverview fallback engaged:', err);
    return FALLBACK_OVERVIEW;
  }
}

export async function fetchEvents(params?: {
  category?: string;
  status?: string;
  needs_review?: boolean;
  search?: string;
}): Promise<EventItem[]> {
  try {
    const query = new URLSearchParams();
    if (params?.category) query.append('category', params.category);
    if (params?.status) query.append('status', params.status);
    if (params?.needs_review !== undefined) query.append('needs_review', String(params.needs_review));
    if (params?.search) query.append('search', params.search);

    const res = await fetch(`${BASE_URL}/events?${query.toString()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('API fetchEvents fallback engaged:', err);
    let items = [...FALLBACK_EVENTS];
    if (params?.category && params.category !== 'all') {
      items = items.filter(e => e.category === params.category);
    }
    if (params?.status && params.status !== 'all') {
      items = items.filter(e => e.status === params.status);
    }
    if (params?.needs_review !== undefined) {
      items = items.filter(e => Boolean(e.needs_review || e.has_conflict) === params.needs_review);
    }
    if (params?.search) {
      const q = params.search.toLowerCase();
      items = items.filter(e => e.title.toLowerCase().includes(q) || (e.course_or_subject || '').toLowerCase().includes(q));
    }
    return items;
  }
}

export async function fetchEventDetail(eventId: string): Promise<EventItem> {
  try {
    const res = await fetch(`${BASE_URL}/events/${eventId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('API fetchEventDetail fallback engaged:', err);
    const found = FALLBACK_EVENTS.find(e => e.id === eventId);
    if (!found) throw new Error('Event not found');
    return found;
  }
}

export async function updateEvent(
  eventId: string,
  data: Partial<EventItem>
): Promise<EventItem> {
  const res = await fetch(`${BASE_URL}/events/${eventId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update event');
  return res.json();
}

export async function confirmEvent(eventId: string): Promise<EventItem> {
  const res = await fetch(`${BASE_URL}/events/${eventId}/confirm`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to confirm event');
  const body = await res.json();
  return body.event;
}

export async function rejectEvent(eventId: string): Promise<EventItem> {
  const res = await fetch(`${BASE_URL}/events/${eventId}/reject`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to reject event');
  const body = await res.json();
  return body.event;
}

export async function importText(
  text: string,
  anonymize: boolean = true,
  use_live_ai: boolean = false,
  api_key?: string
): Promise<any> {
  const res = await fetch(`${BASE_URL}/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, anonymize, use_live_ai, api_key }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to import chat');
  }
  return res.json();
}

export async function importFile(
  file: File,
  anonymize: boolean = true,
  use_live_ai: boolean = false,
  api_key?: string
): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('anonymize', String(anonymize));
  formData.append('use_live_ai', String(use_live_ai));
  if (api_key) {
    formData.append('api_key', api_key);
  }

  const res = await fetch(`${BASE_URL}/import/file`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to import file');
  }
  return res.json();
}

export async function loadDataset(key: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/datasets/${key}/load`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to load dataset');
  return res.json();
}

export async function fetchSources(): Promise<SourceIntegration[]> {
  try {
    const res = await fetch(`${BASE_URL}/sources`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('API fetchSources fallback engaged:', err);
    return FALLBACK_SOURCES;
  }
}

export async function fetchMessages(filterCategory?: string): Promise<AnnotatedMessage[]> {
  try {
    const query = filterCategory ? `?filter_category=${filterCategory}` : '';
    const res = await fetch(`${BASE_URL}/messages${query}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('API fetchMessages fallback engaged:', err);
    let msgs = [...FALLBACK_MESSAGES] as AnnotatedMessage[];
    if (filterCategory && filterCategory !== 'all') {
      if (filterCategory === 'notices') {
        msgs = msgs.filter(m => m.category !== 'chatter');
      } else {
        msgs = msgs.filter(m => m.category === filterCategory);
      }
    }
    return msgs;
  }
}

export async function fetchSettings(): Promise<AppSettings> {
  try {
    const res = await fetch(`${BASE_URL}/settings`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('API fetchSettings fallback engaged:', err);
    return FALLBACK_SETTINGS;
  }
}

export async function updateSettings(data: { api_key?: string; model?: string }): Promise<any> {
  const res = await fetch(`${BASE_URL}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update settings');
  return res.json();
}
