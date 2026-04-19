<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { api, ApiError } from '$lib/api';
  import { activeProfile, allProfiles } from '$lib/stores/profile';
  import { toast } from '$lib/stores/toast';
  import type { Profile } from '$lib/types';

  let loading = true;
  let busy: string | null = null;
  let error = '';

  onMount(async () => {
    try {
      const list = await api.profiles.list();
      allProfiles.set(list);
    } catch (e) {
      error = e instanceof ApiError ? e.message : 'Failed to load profiles';
    } finally {
      loading = false;
    }
  });

  async function pick(p: Profile) {
    busy = p.key;
    try {
      await api.profiles.setActive(p.key);
      activeProfile.set(p);
      toast(`Hi ${p.name} — Mia knows it's you.`, 'ok');
      const redirect = $page.url.searchParams.get('redirect') || '/';
      goto(redirect);
    } catch (e) {
      toast(e instanceof ApiError ? e.message : 'Could not select profile', 'bad');
    } finally {
      busy = null;
    }
  }
</script>

<div class="grid h-full place-items-center px-4 py-10">
  <div class="w-full max-w-xl space-y-6">
    <div class="text-center">
      <h1 class="text-xl font-semibold text-white">Who's at the keyboard?</h1>
      <p class="mt-1 text-sm text-slate-400">
        Pick a profile so Mia knows who she's talking to. You can switch any time.
      </p>
    </div>

    {#if error}
      <div class="card border-rose-500/30 bg-rose-500/5 px-4 py-3 text-sm text-rose-200">
        {error}
      </div>
    {/if}

    {#if loading}
      <div class="card p-6 text-center text-sm text-slate-500">Loading profiles…</div>
    {:else}
      <div class="grid gap-3 sm:grid-cols-2">
        {#each $allProfiles as p (p.id)}
          <button
            type="button"
            class="card card-hover flex items-center gap-3 p-4 text-left transition-colors hover:border-accent/50"
            disabled={busy !== null}
            onclick={() => pick(p)}
          >
            <span
              class="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-accent/15 text-lg font-bold text-accent-soft"
            >
              {p.emoji || p.name.charAt(0).toUpperCase()}
            </span>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-white">{p.name}</p>
              <p class="text-xs text-slate-400">{p.role}</p>
            </div>
            {#if busy === p.key}
              <span class="text-xs text-slate-500">Switching…</span>
            {/if}
          </button>
        {/each}
      </div>

      <p class="text-center text-xs text-slate-500">
        Want to rename a profile? Head to <a class="link" href="/profiles">Profiles</a> after
        picking.
      </p>
    {/if}
  </div>
</div>
