<script lang="ts">
  import { formatNumber } from '$lib/format';
  import type { Metric } from '$lib/types';

  export let metric: Metric;
  export let accent = false;
</script>

<div class="card card-hover p-4" class:ring-1={accent} class:ring-accent={accent}>
  <div class="flex items-baseline justify-between">
    <span class="text-xs font-medium uppercase tracking-wide text-slate-400">{metric.label}</span>
    {#if metric.delta !== null && metric.delta !== undefined}
      <span
        class="text-xs"
        class:text-emerald-400={metric.delta >= 0}
        class:text-rose-400={metric.delta < 0}
      >
        {metric.delta >= 0 ? '+' : ''}{metric.delta}%
      </span>
    {/if}
  </div>
  <div class="mt-2 text-2xl font-semibold tracking-tight text-white">
    {formatNumber(metric.value, metric.unit)}
  </div>
  {#if metric.help}
    <p class="mt-1 text-xs text-slate-500">{metric.help}</p>
  {/if}
</div>
