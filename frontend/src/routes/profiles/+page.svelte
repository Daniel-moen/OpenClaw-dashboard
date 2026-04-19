<script lang="ts">
  import { onMount } from 'svelte';
  import { api, ApiError } from '$lib/api';
  import { activeProfile, allProfiles } from '$lib/stores/profile';
  import { toast } from '$lib/stores/toast';
  import type { Profile } from '$lib/types';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import ErrorState from '$lib/components/ErrorState.svelte';
  import LoadingSkeleton from '$lib/components/LoadingSkeleton.svelte';
  import Modal from '$lib/components/Modal.svelte';
  import Icon from '$lib/components/Icon.svelte';

  let loading = true;
  let error = '';
  let editing: Profile | null = null;
  let modalOpen = false;
  let busy = false;
  let form = { name: '', role: '', emoji: '' };

  async function load() {
    loading = true;
    error = '';
    try {
      const list = await api.profiles.list();
      allProfiles.set(list);
    } catch (e) {
      error = e instanceof ApiError ? e.message : 'Failed to load profiles';
    } finally {
      loading = false;
    }
  }

  onMount(load);

  function openEdit(p: Profile) {
    editing = p;
    form = { name: p.name, role: p.role, emoji: p.emoji };
    modalOpen = true;
  }

  async function submit(e: SubmitEvent) {
    e.preventDefault();
    if (!editing) return;
    busy = true;
    try {
      const updated = await api.profiles.update(editing.id, form);
      toast(`Saved "${updated.name}"`, 'ok');
      modalOpen = false;
      // If we're editing the active profile, refresh it.
      if ($activeProfile?.id === updated.id) activeProfile.set(updated);
      await load();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Save failed', 'bad');
    } finally {
      busy = false;
    }
  }

  async function switchTo(p: Profile) {
    try {
      await api.profiles.setActive(p.key);
      activeProfile.set(p);
      toast(`Now signed in as ${p.name}`, 'ok');
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Switch failed', 'bad');
    }
  }
</script>

<div class="space-y-6">
  <header>
    <h2 class="text-xl font-semibold text-white">Profiles</h2>
    <p class="text-sm text-slate-400">
      Two seats — you and your business partner. Pick a name and avatar so Mia knows who she's
      talking to. (Profiles are identity, not a separate password.)
    </p>
  </header>

  {#if error}<ErrorState message={error} onRetry={load} />{/if}

  {#if loading}
    <div class="card p-4"><LoadingSkeleton rows={4} /></div>
  {:else if $allProfiles.length === 0}
    <EmptyState icon="grid" title="No profiles yet" />
  {:else}
    <div class="grid gap-3 sm:grid-cols-2">
      {#each $allProfiles as p (p.id)}
        {@const active = $activeProfile?.id === p.id}
        <article class="card card-hover p-4">
          <div class="flex items-center gap-3">
            <span
              class="grid h-12 w-12 place-items-center rounded-xl bg-accent/15 text-lg font-bold text-accent-soft"
            >
              {p.emoji || p.name.charAt(0).toUpperCase()}
            </span>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-white">{p.name}</p>
              <p class="text-xs text-slate-400">{p.role}</p>
            </div>
            {#if active}<span class="badge-ok">Active</span>{/if}
          </div>
          <div class="mt-4 flex justify-end gap-2">
            {#if !active}
              <button class="btn-ghost" type="button" onclick={() => switchTo(p)}>
                <Icon name="check" size={14} /><span>Switch to</span>
              </button>
            {/if}
            <button class="btn-ghost" type="button" onclick={() => openEdit(p)}>
              <Icon name="edit" size={14} /><span>Edit</span>
            </button>
          </div>
        </article>
      {/each}
    </div>
  {/if}
</div>

{#if modalOpen && editing}
  <Modal onClose={() => (modalOpen = false)} labelledBy="edit-profile-title">
    <form class="card w-full max-w-md p-5" onsubmit={submit}>
      <h3 id="edit-profile-title" class="mb-4 text-base font-semibold text-white">
        Edit profile
      </h3>
      <div class="space-y-3">
        <label class="block">
          <span class="mb-1 block text-xs text-slate-400">Display name</span>
          <input class="input" bind:value={form.name} required maxlength="60" />
        </label>
        <label class="block">
          <span class="mb-1 block text-xs text-slate-400">Role</span>
          <input
            class="input"
            bind:value={form.role}
            maxlength="40"
            placeholder="owner, co-founder, …"
          />
        </label>
        <label class="block">
          <span class="mb-1 block text-xs text-slate-400">Avatar (1–4 chars or emoji)</span>
          <input class="input" bind:value={form.emoji} maxlength="4" required />
        </label>
      </div>
      <div class="mt-4 flex justify-end gap-2">
        <button class="btn-ghost" type="button" onclick={() => (modalOpen = false)}>Cancel</button>
        <button class="btn-primary" type="submit" disabled={busy}>
          {busy ? 'Saving…' : 'Save'}
        </button>
      </div>
    </form>
  </Modal>
{/if}
