<script lang="ts">
  export let message = 'Something went wrong';
  export let onRetry: (() => void) | null = null;
</script>

<div
  class="rounded-xl border border-rose-500/30 bg-rose-500/5 px-4 py-3 text-sm text-rose-200"
>
  <div class="font-medium">Error</div>
  <div class="mt-0.5 text-rose-300/90">{message}</div>
  {#if onRetry}
    <button class="btn-ghost mt-3" type="button" onclick={onRetry}>Retry</button>
  {/if}
</div>
