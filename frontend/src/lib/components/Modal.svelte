<script lang="ts">
  import { onMount } from 'svelte';

  export let onClose: () => void;
  export let labelledBy: string | undefined = undefined;

  function onBackdrop(e: MouseEvent) {
    if (e.target === e.currentTarget) onClose();
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') onClose();
  }

  onMount(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prev;
    };
  });
</script>

<svelte:window on:keydown={onKey} />

<div
  class="fixed inset-0 z-30 grid place-items-center bg-black/65 px-4"
  role="dialog"
  aria-modal="true"
  aria-labelledby={labelledBy}
  tabindex="-1"
  onclick={onBackdrop}
  onkeydown={(e) => {
    if (e.key === 'Escape') onClose();
  }}
>
  <slot />
</div>
