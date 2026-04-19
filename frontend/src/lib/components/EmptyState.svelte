<script lang="ts">
  export let title = 'Nothing here yet';
  export let message: string | undefined = undefined;
  export let icon: string | undefined = undefined;
  import Icon from './Icon.svelte';
</script>

<div
  class="flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-bg-subtle/40 px-6 py-10 text-center"
>
  {#if icon}
    <div class="mb-3 grid h-10 w-10 place-items-center rounded-full bg-bg-elevated text-slate-400">
      <Icon name={icon} size={20} />
    </div>
  {/if}
  <p class="text-sm font-medium text-slate-200">{title}</p>
  {#if message}
    <p class="mt-1 max-w-sm text-xs text-slate-500">{message}</p>
  {/if}
  <slot />
</div>
