import { writable } from 'svelte/store';

export interface Toast {
  id: number;
  kind: 'info' | 'ok' | 'warn' | 'bad';
  message: string;
}

const _toasts = writable<Toast[]>([]);
export const toasts = { subscribe: _toasts.subscribe };

let nextId = 1;

export function toast(message: string, kind: Toast['kind'] = 'info', ttl = 3500) {
  const id = nextId++;
  _toasts.update((list) => [...list, { id, kind, message }]);
  setTimeout(() => _toasts.update((list) => list.filter((t) => t.id !== id)), ttl);
}
