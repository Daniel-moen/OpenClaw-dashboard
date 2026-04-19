import { writable } from 'svelte/store';
import type { Profile } from '$lib/types';

export const activeProfile = writable<Profile | null>(null);
export const allProfiles = writable<Profile[]>([]);
