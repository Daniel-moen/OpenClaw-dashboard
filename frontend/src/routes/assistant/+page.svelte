<script lang="ts">
  import { onMount } from 'svelte';
  import { api, ApiError } from '$lib/api';
  import { toast } from '$lib/stores/toast';
  import type { AssistantAction } from '$lib/types';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import ErrorState from '$lib/components/ErrorState.svelte';
  import LoadingSkeleton from '$lib/components/LoadingSkeleton.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import Modal from '$lib/components/Modal.svelte';

  let actions: AssistantAction[] = [];
  let loading = true;
  let error = '';
  let editing: AssistantAction | null = null;
  let modalOpen = false;
  let busy = false;
  let form = { label: '', prompt: '', category: 'general' };

  async function load() {
    loading = true;
    error = '';
    try {
      actions = await api.assistant.list();
    } catch (e) {
      error = e instanceof ApiError ? e.message : 'Failed to load actions';
    } finally {
      loading = false;
    }
  }

  onMount(load);

  function openNew() {
    editing = null;
    form = { label: '', prompt: '', category: 'general' };
    modalOpen = true;
  }
  function openEdit(a: AssistantAction) {
    editing = a;
    form = { label: a.label, prompt: a.prompt, category: a.category };
    modalOpen = true;
  }

  async function submit(e: SubmitEvent) {
    e.preventDefault();
    if (!form.label || !form.prompt) return;
    busy = true;
    try {
      if (editing) {
        await api.assistant.update(editing.id, form);
        toast('Action updated', 'ok');
      } else {
        await api.assistant.create(form);
        toast('Action added', 'ok');
      }
      modalOpen = false;
      await load();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Save failed', 'bad');
    } finally {
      busy = false;
    }
  }

  async function remove(a: AssistantAction) {
    if (!confirm(`Delete "${a.label}"?`)) return;
    try {
      await api.assistant.remove(a.id);
      toast('Deleted', 'ok');
      await load();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Delete failed', 'bad');
    }
  }

  async function copy(a: AssistantAction) {
    try {
      await navigator.clipboard.writeText(a.prompt);
      toast('Prompt copied', 'ok');
    } catch {
      toast('Copy failed', 'bad');
    }
  }

  $: groups = (() => {
    const out = new Map<string, AssistantAction[]>();
    for (const a of actions) {
      if (!out.has(a.category)) out.set(a.category, []);
      out.get(a.category)!.push(a);
    }
    return Array.from(out.entries());
  })();
</script>

<div class="space-y-6">
  <header class="flex flex-wrap items-end justify-between gap-3">
    <div>
      <h2 class="text-xl font-semibold text-white">Assistant control panel</h2>
      <p class="text-sm text-slate-400">
        Curate prompts you reuse with the assistant. They show up on the dashboard too.
      </p>
    </div>
    <button class="btn-primary" type="button" onclick={openNew}>
      <Icon name="plus" /> <span>New action</span>
    </button>
  </header>

  {#if error}<ErrorState message={error} onRetry={load} />{/if}

  {#if loading}
    <div class="card p-4"><LoadingSkeleton rows={5} /></div>
  {:else if actions.length === 0}
    <EmptyState icon="bolt" title="No actions yet" message="Add your first prompt shortcut." />
  {:else}
    {#each groups as [cat, list] (cat)}
      <section class="space-y-3">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-400">{cat}</h3>
        <div class="grid gap-3 lg:grid-cols-2">
          {#each list as a (a.id)}
            <article class="card p-4">
              <div class="flex items-start justify-between gap-2">
                <h4 class="text-sm font-semibold text-slate-100">{a.label}</h4>
                <span class="badge-muted">{a.category}</span>
              </div>
              <p class="mt-2 whitespace-pre-wrap text-sm text-slate-300">{a.prompt}</p>
              <div class="mt-3 flex justify-end gap-1">
                <button class="btn-ghost" type="button" onclick={() => copy(a)}>
                  <Icon name="copy" size={14} /><span>Copy</span>
                </button>
                <button class="btn-ghost" type="button" onclick={() => openEdit(a)}>
                  <Icon name="edit" size={14} /><span>Edit</span>
                </button>
                <button
                  class="btn-ghost text-rose-400 hover:text-rose-300"
                  type="button"
                  onclick={() => remove(a)}
                >
                  <Icon name="trash" size={14} /><span>Delete</span>
                </button>
              </div>
            </article>
          {/each}
        </div>
      </section>
    {/each}
  {/if}
</div>

{#if modalOpen}
  <Modal onClose={() => (modalOpen = false)} labelledBy="action-modal-title">
    <form class="card w-full max-w-lg p-4 sm:p-5" onsubmit={submit}>
      <h3 id="action-modal-title" class="mb-4 text-base font-semibold text-white">
        {editing ? 'Edit action' : 'New action'}
      </h3>
      <div class="space-y-3">
        <label class="block">
          <span class="mb-1 block text-xs text-slate-400">Label</span>
          <input class="input" bind:value={form.label} required maxlength="120" />
        </label>
        <label class="block">
          <span class="mb-1 block text-xs text-slate-400">Category</span>
          <input
            class="input"
            bind:value={form.category}
            maxlength="40"
            placeholder="jobcarver, vault, general…"
          />
        </label>
        <label class="block">
          <span class="mb-1 block text-xs text-slate-400">Prompt</span>
          <textarea class="input" rows="6" bind:value={form.prompt} required maxlength="4000"
          ></textarea>
        </label>
      </div>
      <div class="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <button
          class="btn-ghost w-full sm:w-auto"
          type="button"
          onclick={() => (modalOpen = false)}>Cancel</button
        >
        <button class="btn-primary w-full sm:w-auto" type="submit" disabled={busy}>
          {busy ? 'Saving…' : 'Save'}
        </button>
      </div>
    </form>
  </Modal>
{/if}
