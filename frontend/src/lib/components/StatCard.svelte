<script lang="ts">
  import { formatNumber } from '$lib/format';
  import type { Metric } from '$lib/types';

  export let metric: Metric;
  export let accent = false;

  $: deltaClass =
    metric.delta === null || metric.delta === undefined
      ? ''
      : metric.delta >= 0
        ? 'border-emerald-500/25 text-emerald-300/90 bg-emerald-500/5'
        : 'border-rose-500/25 text-rose-300/90 bg-rose-500/5';
</script>

<div class="card card-hover p-4 sm:p-5" class:border-accent={accent}>
  <div class="flex items-center justify-between gap-2">
    <span class="truncate font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500">
      {metric.label}
    </span>
    {#if metric.delta !== null && metric.delta !== undefined}
      <span class="shrink-0 rounded-full border px-1.5 py-px text-[10px] font-medium {deltaClass}">
        {metric.delta >= 0 ? '+' : ''}{metric.delta}%
      </span>
    {/if}
  </div>
  <div class="mt-2 font-display text-3xl font-semibold tracking-tight text-zinc-50 sm:text-[2rem]">
    {formatNumber(metric.value, metric.unit)}
  </div>
  {#if metric.help}
    <p class="mt-1 truncate text-[11px] text-zinc-500">{metric.help}</p>
  {/if}
</div>
