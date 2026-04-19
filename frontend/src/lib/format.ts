export function formatNumber(v: number | string, unit?: string | null): string {
  if (typeof v === 'string') return unit ? `${v} ${unit}` : v;
  let s: string;
  if (Math.abs(v) >= 1000) {
    s = v.toLocaleString(undefined, { maximumFractionDigits: 2 });
  } else if (Number.isInteger(v)) {
    s = v.toString();
  } else {
    s = v.toFixed(2);
  }
  return unit ? `${s} ${unit}` : s;
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const units = ['KB', 'MB', 'GB', 'TB'];
  let v = bytes / 1024;
  let i = 0;
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024;
    i++;
  }
  return `${v.toFixed(v >= 100 ? 0 : 1)} ${units[i]}`;
}

export function formatRelative(iso: string): string {
  const t = new Date(iso).getTime();
  if (!Number.isFinite(t)) return iso;
  const diff = (Date.now() - t) / 1000;
  const abs = Math.abs(diff);
  const past = diff >= 0;
  const fmt = (n: number, unit: string) => `${n}${unit} ${past ? 'ago' : 'from now'}`;
  if (abs < 60) return past ? 'just now' : 'in a moment';
  if (abs < 3600) return fmt(Math.floor(abs / 60), 'm');
  if (abs < 86400) return fmt(Math.floor(abs / 3600), 'h');
  if (abs < 86400 * 7) return fmt(Math.floor(abs / 86400), 'd');
  return new Date(iso).toLocaleDateString();
}

export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  if (!Number.isFinite(d.getTime())) return iso;
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  });
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  if (!Number.isFinite(d.getTime())) return iso;
  return d.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });
}
