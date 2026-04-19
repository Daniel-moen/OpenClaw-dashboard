<script lang="ts">
  import { onMount } from 'svelte';
  import { api, ApiError } from '$lib/api';
  import { formatDateTime, formatRelative } from '$lib/format';
  import { activeProfile } from '$lib/stores/profile';
  import type { DashboardSummary } from '$lib/types';
  import StatCard from '$lib/components/StatCard.svelte';
  import QuickActions from '$lib/components/QuickActions.svelte';
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

<div class="space-y-6">
  <header class="flex flex-wrap items-end justify-between gap-3">
    <div>
      <h2 class="text-xl font-semibold text-white">
        Welcome back{$activeProfile ? `, ${$activeProfile.name}` : ''}
      </h2>
      <p class="text-sm text-slate-400">Today's view of your businesses and ops.</p>
    </div>
    <div class="flex gap-2">
      <a href="/vault" class="btn-ghost"><Icon name="upload" /> <span>Upload</span></a>
      <a href="/calendar" class="btn-primary"><Icon name="plus" /> <span>New event</span></a>
    </div>
  </header>

  {#if error}
    <ErrorState message={error} onRetry={load} />
  {/if}

  {#if loading && !data}
    <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {#each Array(4) as _, i (i)}
        <div class="card p-4"><LoadingSkeleton rows={2} /></div>
      {/each}
    </div>
  {:else if data}
    <section class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {#each data.stats as m (m.key)}
        <StatCard metric={m} />
      {/each}
    </section>

    <section class="grid gap-4 lg:grid-cols-3">
      <div class="lg:col-span-2 space-y-4">
        <QuickActions actions={data.quick_actions} />

        <div class="card p-4">
          <div class="mb-3 flex items-center justify-between">
            <h3 class="text-sm font-semibold text-slate-200">Recent activity</h3>
            <span class="text-xs text-slate-500">{data.recent_activity.length} items</span>
          </div>
          {#if data.recent_activity.length === 0}
            <EmptyState
              icon="bolt"
              title="Nothing's happened yet"
              message="Activity from uploads, logins and calendar changes will show up here."
            />
          {:else}
            <ul class="divide-y divide-border text-sm">
              {#each data.recent_activity as a (a.id)}
                <li class="flex items-center justify-between gap-3 py-2.5">
                  <div class="min-w-0">
                    <p class="truncate text-slate-200">{a.message}</p>
                    <p class="text-xs text-slate-500">
                      {a.kind}{#if a.profile_name} · {a.profile_name}{/if}
                    </p>
                  </div>
                  <span class="shrink-0 text-xs text-slate-500"
                    >{formatRelative(a.created_at)}</span
                  >
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>

      <div class="space-y-4">
        <div class="card p-4">
          <h3 class="mb-3 text-sm font-semibold text-slate-200">Brands</h3>
          <ul class="space-y-2">
            {#each data.businesses as b (b.slug)}
              <li>
                <a
                  href={`/businesses/${b.slug}`}
                  class="flex items-center justify-between gap-3 rounded-lg border border-border bg-bg-subtle/60 px-3 py-2 transition-colors hover:border-accent/40"
                >
                  <div>
                    <p class="text-sm font-medium text-slate-100">{b.name}</p>
                    <p class="text-xs text-slate-500">{b.tagline ?? ''}</p>
                  </div>
                  {#if b.status === 'live'}
                    <span class="badge-ok">Live</span>
                  {:else}
                    <span class="badge-muted">Soon</span>
                  {/if}
                </a>
              </li>
            {/each}
          </ul>
        </div>

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
              {#each data.upcoming_events as ev (ev.id)}
                <li class="rounded-lg border border-border bg-bg-subtle/60 px-3 py-2">
                  <p class="font-medium text-slate-100">{ev.title}</p>
                  <p class="text-xs text-slate-500">{formatDateTime(ev.starts_at)}</p>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>
    </section>
  {/if}
</div>
