<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import {
    Chart,
    LineController,
    BarController,
    LineElement,
    PointElement,
    BarElement,
    LinearScale,
    CategoryScale,
    Tooltip,
    Filler
  } from 'chart.js';
  import type { Series } from '$lib/types';

  Chart.register(
    LineController,
    BarController,
    LineElement,
    PointElement,
    BarElement,
    LinearScale,
    CategoryScale,
    Tooltip,
    Filler
  );

  export let series: Series;
  export let kind: 'line' | 'bar' = 'line';
  export let height = 220;

  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;

  function build() {
    if (!canvas) return;
    if (chart) chart.destroy();
    const labels = series.points.map((p) => p.t);
    const data = series.points.map((p) => p.v);
    const accent = '#7c5cff';
    chart = new Chart(canvas, {
      type: kind,
      data: {
        labels,
        datasets: [
          {
            label: series.label,
            data,
            borderColor: accent,
            backgroundColor: kind === 'line' ? 'rgba(124,92,255,0.18)' : 'rgba(124,92,255,0.6)',
            fill: kind === 'line',
            tension: 0.3,
            pointRadius: kind === 'line' ? 2 : 0,
            borderRadius: kind === 'bar' ? 4 : undefined
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { intersect: false, mode: 'index' }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: { color: '#64748b', maxRotation: 0, autoSkip: true, maxTicksLimit: 8 }
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: { color: '#64748b' },
            beginAtZero: true
          }
        }
      }
    });
  }

  onMount(build);

  $: if (chart && series) {
    build();
  }

  onDestroy(() => chart?.destroy());
</script>

<div class="card p-4">
  <div class="mb-2 flex items-baseline justify-between">
    <h3 class="text-sm font-semibold text-slate-200">{series.label}</h3>
    <span class="text-xs text-slate-500">{series.points.length} points</span>
  </div>
  <div style="height: {height}px">
    <canvas bind:this={canvas}></canvas>
  </div>
</div>
