export interface Metric {
  key: string;
  label: string;
  value: number | string;
  unit?: string | null;
  delta?: number | null;
  help?: string | null;
}

export interface SeriesPoint {
  t: string;
  v: number;
}

export interface Series {
  key: string;
  label: string;
  points: SeriesPoint[];
}

export interface BusinessSummary {
  slug: string;
  name: string;
  tagline?: string | null;
  status: 'live' | 'coming-soon' | string;
  headline?: Record<string, number | string> | null;
}

export interface BusinessStats {
  slug: string;
  name: string;
  fetched_at: string;
  source: 'live' | 'mock';
  metrics: Metric[];
  series: Series[];
  tables: Record<string, Record<string, unknown>[]>;
  raw?: Record<string, unknown> | null;
}

export interface CalendarEvent {
  id: number;
  title: string;
  starts_at: string;
  ends_at?: string | null;
  location?: string | null;
  notes?: string | null;
  created_at: string;
}

export interface VaultFile {
  id: number;
  name: string;
  original_name: string;
  mime: string;
  size: number;
  sha256: string;
  created_at: string;
}

export interface ActivityItem {
  id: number;
  kind: string;
  message: string;
  meta?: Record<string, unknown> | null;
  profile_key?: string | null;
  profile_name?: string | null;
  created_at: string;
}

export interface Profile {
  id: number;
  key: string;
  name: string;
  role: string;
  emoji: string;
  created_at: string;
}

export interface Me {
  authenticated: boolean;
  profile: Profile | null;
}

export type ChatRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: number;
  role: ChatRole;
  content: string;
  profile_key?: string | null;
  profile_name?: string | null;
  created_at: string;
}

export interface ChatStatus {
  online: boolean;
  model: string | null;
  assistant_name: string;
}

export interface ChatSendResponse {
  user: ChatMessage;
  reply: ChatMessage;
  online: boolean;
}

export interface AssistantAction {
  id: number;
  slug: string;
  label: string;
  prompt: string;
  category: string;
  created_at: string;
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  category: string;
  status: 'available' | 'beta' | 'planned' | string;
  source?: string | null;
  docs_url?: string | null;
}

export interface DashboardSummary {
  stats: Metric[];
  recent_activity: ActivityItem[];
  quick_actions: AssistantAction[];
  businesses: BusinessSummary[];
  upcoming_events: CalendarEvent[];
}
