import { writable } from 'svelte/store';

export const authStatus = writable<'unknown' | 'in' | 'out'>('unknown');
