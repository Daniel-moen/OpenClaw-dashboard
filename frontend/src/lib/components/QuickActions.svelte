<script lang="ts">
  import { toast } from '$lib/stores/toast';
  import type { AssistantAction } from '$lib/types';
  import Icon from './Icon.svelte';

  export let actions: AssistantAction[] = [];
  export let title = 'Quick actions';

  async function copy(action: AssistantAction) {
    try {
      await navigator.clipboard.writeText(action.prompt);
      toast(`Copied "${action.label}" to clipboard`, 'ok');
    } catch {
      toast('Could not copy to clipboard', 'bad');
    }
  }
</script>

<div class="card p-4">
  <div class="mb-3 flex items-center justify-between">
    <h3 class="text-sm font-semibold text-slate-200">{title}</h3>
    <a class="text-xs text-slate-400 hover:text-white" href="/assistant">Manage</a>
  </div>
  <div class="grid gap-2 sm:grid-cols-2">
    {#each actions as a (a.id)}
      <button
        type="button"
        class="group flex items-start gap-2 rounded-lg border border-border bg-bg-subtle/60 p-3 text-left text-sm transition-colors hover:border-accent/40 hover:bg-bg-elevated"
        onclick={() => copy(a)}
      >
        <span
          class="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-md bg-accent/10 text-accent-soft"
        >
          <Icon name="bolt" size={14} />
        </span>
        <span class="min-w-0 flex-1">
          <span class="block truncate font-medium text-slate-100">{a.label}</span>
          <span class="block truncate text-xs text-slate-500">{a.prompt}</span>
        </span>
        <span class="text-[10px] uppercase tracking-wide text-slate-500 group-hover:text-slate-300"
          >Copy</span
        >
      </button>
    {:else}
      <p class="text-sm text-slate-500">No quick actions yet.</p>
    {/each}
  </div>
</div>
