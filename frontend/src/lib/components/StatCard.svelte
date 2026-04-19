<script lang="ts">
  import { formatNumber } from '$lib/format';
  import type { Metric } from '$lib/types';

  export let metric: Metric;
  export let accent = false;
</script>

<div class="card card-hover p-3 sm:p-4" class:ring-1={accent} class:ring-accent={accent}>
  <div class="flex items-baseline justify-between gap-2">
    <span class="truncate text-[11px] font-medium uppercase tracking-wide text-slate-400">
      {metric.label}
    </span>
    {#if metric.delta !== null && metric.delta !== undefined}
      <span
        class="text-[11px] shrink-0"
        class:text-emerald-400={metric.delta >= 0}
        class:text-rose-400={metric.delta < 0}
      >
        {metric.delta >= 0 ? '+' : ''}{metric.delta}%
      </span>
    {/if}
  </div>
  <div class="mt-1.5 text-xl font-semibold tracking-tight text-white sm:text-2xl">
    {formatNumber(metric.value, metric.unit)}
  </div>
  {#if metric.help}
    <p class="mt-0.5 truncate text-[11px] text-slate-500">{metric.help}</p>
  {/if}
</div>
