<script lang="ts">
  import { onMount } from 'svelte';
  import { api, ApiError } from '$lib/api';
  import { formatDateTime, formatRelative } from '$lib/format';
  import { activeProfile } from '$lib/stores/profile';
  import type { DashboardSummary } from '$lib/types';
  import StatCard from '$lib/components/StatCard.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import ErrorState from '$lib/components/ErrorState.svelte';
  import LoadingSkeleton from '$lib/components/LoadingSkeleton.svelte';
  import Icon from '$lib/components/Icon.svelte';

  let data: DashboardSummary | null = null;
  let loading = true;
  let error = '';

  async function load() {
    loading = true;
    error = '';
    try {
      data = await api.dashboard.summary();
    } catch (e) {
      error = e instanceof ApiError ? e.message : 'Failed to load dashboard';
    } finally {
      loading = false;
    }
  }

  onMount(load);
</script>

<div class="space-y-5">
  <header class="space-y-3 sm:flex sm:flex-wrap sm:items-end sm:justify-between sm:gap-3 sm:space-y-0">
    <div class="min-w-0">
      <h2 class="truncate text-lg font-semibold text-white sm:text-xl">
        Welcome back{$activeProfile ? `, ${$activeProfile.name}` : ''}
      </h2>
      <p class="text-sm text-slate-400">Today at a glance.</p>
    </div>
    <div class="-mx-1 flex flex-nowrap gap-2 overflow-x-auto px-1 pb-1 sm:mx-0 sm:flex-wrap sm:overflow-visible sm:px-0 sm:pb-0">
      <a href="/chat" class="btn-primary shrink-0"><Icon name="chat" size={14} /><span>Chat with Mia</span></a>
      <a href="/calendar" class="btn-ghost shrink-0"><Icon name="plus" size={14} /><span>New event</span></a>
      <a href="/vault" class="btn-ghost shrink-0"><Icon name="upload" size={14} /><span>Upload</span></a>
    </div>
  </header>

  {#if error}<ErrorState message={error} onRetry={load} />{/if}

  {#if loading && !data}
    <div class="grid gap-3 grid-cols-2 lg:grid-cols-4">
      {#each Array(4) as _, i (i)}
        <div class="card p-3"><LoadingSkeleton rows={2} /></div>
      {/each}
    </div>
  {:else if data}
    <!-- Stats: 2 cols on mobile, 4 on desktop. Compact. -->
    <section class="grid gap-3 grid-cols-2 lg:grid-cols-4">
      {#each data.stats as m (m.key)}
        <StatCard metric={m} />
      {/each}
    </section>

    <!-- Two-column main: chat + ops on the left, side rail on the right. -->
    <section class="grid gap-4 lg:grid-cols-3">
      <div class="space-y-4 lg:col-span-2">
        <a
          href="/chat"
          class="card card-hover flex items-center gap-4 p-4 transition-colors hover:border-accent/40"
        >
          <span
            class="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-accent/15 text-lg font-bold text-accent-soft"
          >
            M
          </span>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-semibold text-white">Chat with Mia</p>
            <p class="truncate text-xs text-slate-400">
              Ask about JobCarver, your calendar, the vault, or what's on for today.
            </p>
          </div>
          <span class="shrink-0 text-xs text-slate-500">Open →</span>
        </a>

        <div class="card p-4">
          <div class="mb-3 flex items-center justify-between">
            <h3 class="text-sm font-semibold text-slate-200">Brands</h3>
            <a class="text-xs text-slate-400 hover:text-white" href="/businesses/jobcarver">Stats</a>
          </div>
          <ul class="grid gap-2 sm:grid-cols-2">
            {#each data.businesses as b (b.slug)}
              <li>
                <a
                  href={`/businesses/${b.slug}`}
                  class="flex items-center justify-between gap-3 rounded-lg border border-border bg-bg-subtle/60 px-3 py-2 transition-colors hover:border-accent/40"
                >
                  <div class="min-w-0">
                    <p class="truncate text-sm font-medium text-slate-100">{b.name}</p>
                    <p class="truncate text-xs text-slate-500">{b.tagline ?? ''}</p>
                  </div>
                  {#if b.status === 'live'}
                    <span class="badge-ok shrink-0">Live</span>
                  {:else}
                    <span class="badge-muted shrink-0">Soon</span>
                  {/if}
                </a>
              </li>
            {/each}
          </ul>
        </div>
      </div>

      <aside class="space-y-4">
        <div class="card p-4">
          <div class="mb-3 flex items-center justify-between">
            <h3 class="text-sm font-semibold text-slate-200">Upcoming</h3>
            <a class="text-xs text-slate-400 hover:text-white" href="/calendar">All</a>
          </div>
          {#if data.upcoming_events.length === 0}
            <EmptyState
              icon="calendar"
              title="Nothing scheduled"
              message="Your next 7 days are clear."
            />
          {:else}
            <ul class="space-y-2 text-sm">
              {#each data.upcoming_events.slice(0, 4) as ev (ev.id)}
                <li class="rounded-lg border border-border bg-bg-subtle/60 px-3 py-2">
                  <p class="truncate font-medium text-slate-100">{ev.title}</p>
                  <p class="text-xs text-slate-500">{formatDateTime(ev.starts_at)}</p>
                </li>
              {/each}
            </ul>
          {/if}
        </div>

        <div class="card p-4">
          <div class="mb-3 flex items-center justify-between">
            <h3 class="text-sm font-semibold text-slate-200">Recent activity</h3>
            <span class="text-xs text-slate-500">{data.recent_activity.length}</span>
          </div>
          {#if data.recent_activity.length === 0}
            <EmptyState
              icon="bolt"
              title="Quiet so far"
              message="Uploads, sign-ins and chat will show up here."
            />
          {:else}
            <ul class="divide-y divide-border text-sm">
              {#each data.recent_activity.slice(0, 5) as a (a.id)}
                <li class="flex items-start justify-between gap-2 py-2">
                  <div class="min-w-0">
                    <p class="truncate text-slate-200">{a.message}</p>
                    <p class="truncate text-[11px] text-slate-500">
                      {a.kind}{#if a.profile_name} · {a.profile_name}{/if}
                    </p>
                  </div>
                  <span class="shrink-0 text-[11px] text-slate-500">
                    {formatRelative(a.created_at)}
                  </span>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </aside>
    </section>
  {/if}
</div>
