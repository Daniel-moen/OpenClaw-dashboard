import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';
import type {
  AssistantAction,
  BusinessStats,
  BusinessSummary,
  CalendarEvent,
  ChatMessage,
  ChatSendResponse,
  ChatStatus,
  DashboardSummary,
  Me,
  Profile,
  Skill,
  VaultFile
} from './types';

const API_BASE =
  (browser && env.PUBLIC_API_BASE) ||
  (typeof process !== 'undefined' && process.env?.PUBLIC_API_BASE) ||
  'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, message: string, body: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

async function request<T>(
  path: string,
  init: RequestInit = {},
  fetchFn: typeof fetch = fetch
): Promise<T> {
  const headers = new Headers(init.headers || {});
  if (init.body && !(init.body instanceof FormData) && !headers.has('content-type')) {
    headers.set('content-type', 'application/json');
  }
  const res = await fetchFn(`${API_BASE}${path}`, {
    credentials: 'include',
    ...init,
    headers
  });
  if (res.status === 204) return undefined as T;
  let body: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }
  if (!res.ok) {
    let message = `request failed: ${res.status}`;
    if (body && typeof body === 'object' && 'detail' in body) {
      message = String((body as { detail: unknown }).detail);
    }
    throw new ApiError(res.status, message, body);
  }
  return body as T;
}

export const api = {
  base: API_BASE,
  health: (f?: typeof fetch) => request<{ status: string }>('/api/health', {}, f),

  auth: {
    login: (password: string, f?: typeof fetch) =>
      request<{ ok: boolean }>(
        '/api/auth/login',
        { method: 'POST', body: JSON.stringify({ password }) },
        f
      ),
    logout: (f?: typeof fetch) => request<{ ok: boolean }>('/api/auth/logout', { method: 'POST' }, f),
    session: (f?: typeof fetch) =>
      request<{ authenticated: boolean; subject?: string }>('/api/auth/session', {}, f)
  },

  dashboard: {
    summary: (f?: typeof fetch) => request<DashboardSummary>('/api/dashboard/summary', {}, f)
  },

  businesses: {
    list: (f?: typeof fetch) => request<BusinessSummary[]>('/api/businesses', {}, f),
    stats: (slug: string, f?: typeof fetch) =>
      request<BusinessStats>(`/api/businesses/${slug}/stats`, {}, f)
  },

  calendar: {
    list: (f?: typeof fetch) => request<CalendarEvent[]>('/api/calendar/events', {}, f),
    create: (
      body: { title: string; starts_at: string; ends_at?: string | null; location?: string; notes?: string },
      f?: typeof fetch
    ) =>
      request<CalendarEvent>(
        '/api/calendar/events',
        { method: 'POST', body: JSON.stringify(body) },
        f
      ),
    remove: (id: number, f?: typeof fetch) =>
      request<void>(`/api/calendar/events/${id}`, { method: 'DELETE' }, f)
  },

  skills: {
    list: (f?: typeof fetch) => request<Skill[]>('/api/skills', {}, f)
  },

  vault: {
    list: (q?: string, f?: typeof fetch) =>
      request<VaultFile[]>(`/api/vault${q ? `?q=${encodeURIComponent(q)}` : ''}`, {}, f),
    upload: (file: File, f?: typeof fetch) => {
      const fd = new FormData();
      fd.append('file', file);
      return request<VaultFile>('/api/vault', { method: 'POST', body: fd }, f);
    },
    remove: (id: number, f?: typeof fetch) =>
      request<void>(`/api/vault/${id}`, { method: 'DELETE' }, f),
    downloadUrl: (id: number) => `${API_BASE}/api/vault/${id}/download`,
    previewUrl: (id: number) => `${API_BASE}/api/vault/${id}/preview`
  },

  me: (f?: typeof fetch) => request<Me>('/api/me', {}, f),

  profiles: {
    list: (f?: typeof fetch) => request<Profile[]>('/api/profiles', {}, f),
    active: (f?: typeof fetch) =>
      request<Profile | null>('/api/profiles/active', {}, f),
    setActive: (key: string, f?: typeof fetch) =>
      request<Profile>(
        '/api/profiles/active',
        { method: 'POST', body: JSON.stringify({ key }) },
        f
      ),
    update: (
      id: number,
      body: { name: string; role: string; emoji: string },
      f?: typeof fetch
    ) =>
      request<Profile>(
        `/api/profiles/${id}`,
        { method: 'PUT', body: JSON.stringify(body) },
        f
      )
  },

  chat: {
    status: (f?: typeof fetch) => request<ChatStatus>('/api/chat/status', {}, f),
    list: (f?: typeof fetch) => request<ChatMessage[]>('/api/chat/messages', {}, f),
    send: (content: string, f?: typeof fetch) =>
      request<ChatSendResponse>(
        '/api/chat/messages',
        { method: 'POST', body: JSON.stringify({ content }) },
        f
      ),
    clear: (f?: typeof fetch) =>
      request<void>('/api/chat/messages', { method: 'DELETE' }, f)
  },

  assistant: {
    list: (f?: typeof fetch) => request<AssistantAction[]>('/api/assistant/actions', {}, f),
    create: (
      body: { label: string; prompt: string; category?: string },
      f?: typeof fetch
    ) =>
      request<AssistantAction>(
        '/api/assistant/actions',
        { method: 'POST', body: JSON.stringify(body) },
        f
      ),
    update: (
      id: number,
      body: { label: string; prompt: string; category?: string },
      f?: typeof fetch
    ) =>
      request<AssistantAction>(
        `/api/assistant/actions/${id}`,
        { method: 'PUT', body: JSON.stringify(body) },
        f
      ),
    remove: (id: number, f?: typeof fetch) =>
      request<void>(`/api/assistant/actions/${id}`, { method: 'DELETE' }, f)
  }
};
