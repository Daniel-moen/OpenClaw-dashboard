<script lang="ts">
  import { toasts } from '$lib/stores/toast';
</script>

<div class="pointer-events-none fixed bottom-4 right-4 z-50 flex w-80 flex-col gap-2">
  {#each $toasts as t (t.id)}
    <div
      class="pointer-events-auto rounded-lg border px-3 py-2 text-sm shadow-card"
      class:border-emerald-500={t.kind === 'ok'}
      class:bg-emerald-500={t.kind === 'ok'}
      class:bg-opacity-10={t.kind === 'ok' || t.kind === 'warn' || t.kind === 'bad'}
      class:text-emerald-200={t.kind === 'ok'}
      class:border-amber-500={t.kind === 'warn'}
      class:text-amber-200={t.kind === 'warn'}
      class:border-rose-500={t.kind === 'bad'}
      class:text-rose-200={t.kind === 'bad'}
      class:border-border={t.kind === 'info'}
      class:bg-bg-elevated={t.kind === 'info'}
      class:text-slate-200={t.kind === 'info'}
      role="status"
    >
      {t.message}
    </div>
  {/each}
</div>
