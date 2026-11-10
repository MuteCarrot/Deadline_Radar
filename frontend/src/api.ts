import { EventItem, OverviewData, SourceIntegration, AppSettings } from './types';

const BASE_URL = '/api';

export async function fetchOverview(): Promise<OverviewData> {
  const res = await fetch(`${BASE_URL}/overview`);
  if (!res.ok) throw new Error('Failed to load overview data');
  return res.json();
}

export async function fetchEvents(params?: {
  category?: string;
  status?: string;
  needs_review?: boolean;
  search?: string;
}): Promise<EventItem[]> {
  const query = new URLSearchParams();
  if (params?.category) query.append('category', params.category);
  if (params?.status) query.append('status', params.status);
  if (params?.needs_review !== undefined) query.append('needs_review', String(params.needs_review));
  if (params?.search) query.append('search', params.search);

  const res = await fetch(`${BASE_URL}/events?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch events');
  return res.json();
}

export async function fetchEventDetail(eventId: string): Promise<EventItem> {
  const res = await fetch(`${BASE_URL}/events/${eventId}`);
  if (!res.ok) throw new Error('Failed to fetch event detail');
  return res.json();
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
  use_live_ai: boolean = false
): Promise<any> {
  const res = await fetch(`${BASE_URL}/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, anonymize, use_live_ai }),
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
  use_live_ai: boolean = false
): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('anonymize', String(anonymize));
  formData.append('use_live_ai', String(use_live_ai));

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
  const res = await fetch(`${BASE_URL}/sources`);
  if (!res.ok) throw new Error('Failed to fetch sources');
  return res.json();
}

export async function fetchSettings(): Promise<AppSettings> {
  const res = await fetch(`${BASE_URL}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
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

