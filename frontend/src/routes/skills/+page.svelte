<script lang="ts">
  import { onMount } from 'svelte';
  import { api, ApiError } from '$lib/api';
  import type { Skill } from '$lib/types';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import ErrorState from '$lib/components/ErrorState.svelte';
  import LoadingSkeleton from '$lib/components/LoadingSkeleton.svelte';

  let skills: Skill[] = [];
  let loading = true;
  let error = '';

  async function load() {
    loading = true;
    error = '';
    try {
      skills = await api.skills.list();
    } catch (e) {
      error = e instanceof ApiError ? e.message : 'Failed to load skills';
    } finally {
      loading = false;
    }
  }
  onMount(load);

  $: groups = (() => {
    const out = new Map<string, Skill[]>();
    for (const s of skills) {
      if (!out.has(s.category)) out.set(s.category, []);
      out.get(s.category)!.push(s);
    }
    return Array.from(out.entries());
  })();
</script>

<div class="space-y-6">
  <header>
    <h2 class="text-xl font-semibold text-white">Assistant skills</h2>
    <p class="text-sm text-slate-400">
      What the assistant can do for you. Add new ones in
      <code class="text-slate-300">backend/app/data/skills.json</code>.
    </p>
  </header>

  {#if error}<ErrorState message={error} onRetry={load} />{/if}

  {#if loading}
    <div class="card p-4"><LoadingSkeleton rows={4} /></div>
  {:else if skills.length === 0}
    <EmptyState icon="sparkle" title="No skills yet" />
  {:else}
    {#each groups as [cat, list] (cat)}
      <section class="space-y-3">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-400">{cat}</h3>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {#each list as s (s.id)}
            <article class="card card-hover p-4">
              <div class="flex items-start justify-between gap-2">
                <h4 class="text-sm font-semibold text-slate-100">{s.name}</h4>
                {#if s.status === 'available'}
                  <span class="badge-ok">Available</span>
                {:else if s.status === 'beta'}
                  <span class="badge-warn">Beta</span>
                {:else}
                  <span class="badge-muted">{s.status}</span>
                {/if}
              </div>
              <p class="mt-2 text-sm text-slate-400">{s.description}</p>
              {#if s.source}
                <p class="mt-3 truncate font-mono text-[11px] text-slate-500">{s.source}</p>
              {/if}
            </article>
          {/each}
        </div>
      </section>
    {/each}
  {/if}
</div>
