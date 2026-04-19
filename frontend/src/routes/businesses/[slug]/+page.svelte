<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api, ApiError } from '$lib/api';
  import { formatNumber, formatRelative } from '$lib/format';
  import type { BusinessStats } from '$lib/types';
  import StatCard from '$lib/components/StatCard.svelte';
  import ChartCard from '$lib/components/ChartCard.svelte';
  import DataTable from '$lib/components/DataTable.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import ErrorState from '$lib/components/ErrorState.svelte';
  import LoadingSkeleton from '$lib/components/LoadingSkeleton.svelte';
  import Icon from '$lib/components/Icon.svelte';

  let stats: BusinessStats | null = null;
  let loading = true;
  let error = '';
  let showRaw = false;

  $: slug = $page.params.slug ?? '';

  async function load() {
    loading = true;
    error = '';
    stats = null;
    try {
      stats = await api.businesses.stats(slug);
    } catch (e) {
      error = e instanceof ApiError ? e.message : 'Failed to load stats';
    } finally {
      loading = false;
    }
  }

  $: if (slug) load();
</script>

<div class="space-y-6">
  <header class="flex flex-wrap items-end justify-between gap-3">
    <div>
      <p class="text-xs uppercase tracking-wide text-slate-500">Business</p>
      <h2 class="text-xl font-semibold text-white">
        {stats?.name ?? slug.charAt(0).toUpperCase() + slug.slice(1)}
      </h2>
      {#if stats}
        <p class="text-xs text-slate-500">
          Updated {formatRelative(stats.fetched_at)} ·
          {#if stats.source === 'live'}
            <span class="text-emerald-400">live source</span>
          {:else}
            <span class="text-amber-400">mock data — set JOBCARVER_STATS_URL to go live</span>
          {/if}
        </p>
      {/if}
    </div>
    <div class="flex gap-2">
      <button class="btn-ghost" type="button" onclick={load} disabled={loading}>
        <Icon name="refresh" /> <span>Refresh</span>
      </button>
    </div>
  </header>

  {#if error}
    <ErrorState message={error} onRetry={load} />
  {/if}

  {#if loading && !stats}
    <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {#each Array(8) as _, i (i)}
        <div class="card p-4"><LoadingSkeleton rows={2} /></div>
      {/each}
    </div>
  {:else if stats}
    {#if stats.metrics.length === 0 && stats.series.length === 0}
      <EmptyState
        icon="chart"
        title={`${stats.name} stats not yet wired`}
        message="Implement the BusinessStatsProvider for this brand or set its upstream URL."
      />
    {:else}
      <section class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {#each stats.metrics as m (m.key)}
          <StatCard metric={m} />
        {/each}
      </section>

      {#if stats.series.length > 0}
        <section class="grid gap-4 lg:grid-cols-2">
          {#each stats.series as s, i (s.key)}
            <ChartCard series={s} kind={i === 0 ? 'line' : 'bar'} />
          {/each}
        </section>
      {/if}

      {#each Object.entries(stats.tables) as [name, rows] (name)}
        <DataTable
          title={name.replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase())}
          rows={rows}
        />
      {/each}

      <div class="card p-4">
        <button
          type="button"
          class="flex w-full items-center justify-between text-sm text-slate-300 hover:text-white"
          onclick={() => (showRaw = !showRaw)}
          aria-expanded={showRaw}
        >
          <span class="font-semibold">Raw payload</span>
          <span class="text-xs text-slate-500">{showRaw ? 'Hide' : 'Show'}</span>
        </button>
        {#if showRaw}
          <pre
            class="mt-3 max-h-96 overflow-auto rounded-lg border border-border bg-bg-subtle p-3 text-xs text-slate-300">{JSON.stringify(
              stats.raw,
              null,
              2
            )}</pre>
        {/if}
      </div>
    {/if}
  {/if}
</div>
