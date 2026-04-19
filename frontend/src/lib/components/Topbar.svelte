<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { api, ApiError } from '$lib/api';
  import { authStatus } from '$lib/stores/auth';
  import { activeProfile, allProfiles } from '$lib/stores/profile';
  import { toast } from '$lib/stores/toast';
  import type { Profile } from '$lib/types';
  import Icon from './Icon.svelte';

  let busy = false;
  let menuOpen = false;
  let menuRoot: HTMLDivElement;

  function titleFor(path: string): string {
    if (path === '/') return 'Command center';
    if (path.startsWith('/businesses/')) {
      const slug = path.split('/')[2] ?? '';
      return slug.charAt(0).toUpperCase() + slug.slice(1);
    }
    return path.replace(/^\//, '').split('/')[0]?.replace(/^./, (c) => c.toUpperCase()) ?? '';
  }

  function sectionFor(path: string): string {
    if (path === '/') return 'Overview';
    if (path.startsWith('/businesses/')) return 'Brand';
    return titleFor(path);
  }

  async function logout() {
    busy = true;
    try {
      await api.auth.logout();
      authStatus.set('out');
      activeProfile.set(null);
      toast('Signed out', 'ok');
      goto('/login');
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : 'Logout failed';
      toast(msg, 'bad');
    } finally {
      busy = false;
    }
  }

  async function switchTo(p: Profile) {
    if (p.id === $activeProfile?.id) {
      menuOpen = false;
      return;
    }
    try {
      await api.profiles.setActive(p.key);
      activeProfile.set(p);
      toast(`Now signed in as ${p.name}`, 'ok');
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Switch failed', 'bad');
    } finally {
      menuOpen = false;
    }
  }

  function onDocClick(e: MouseEvent) {
    if (menuOpen && menuRoot && !menuRoot.contains(e.target as Node)) {
      menuOpen = false;
    }
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') menuOpen = false;
  }
</script>

<svelte:window on:click={onDocClick} on:keydown={onKey} />

<header
  class="sticky top-0 z-20 flex h-16 shrink-0 items-center gap-2 border-b border-border bg-bg/80 px-3 backdrop-blur safe-pt sm:gap-3 md:px-6"
>
  <div class="md:hidden">
    <a href="/" class="brand-mark h-9 w-9 text-sm" aria-label="Home">O</a>
  </div>
  <div class="min-w-0 flex-1">
    <p class="hidden font-mono text-[10px] uppercase tracking-[0.22em] text-zinc-600 sm:block">
      Openclaw / {sectionFor($page.url.pathname)}
    </p>
    <h1 class="truncate font-display text-lg font-semibold tracking-tight text-zinc-100">
      {titleFor($page.url.pathname)}
    </h1>
  </div>
  <div class="flex shrink-0 items-center gap-1.5 sm:gap-2">
    {#if $activeProfile}
      <div class="relative" bind:this={menuRoot}>
        <button
          class="flex min-h-[40px] items-center gap-2 rounded-md border border-border bg-bg-subtle/60 px-2 py-1.5 text-xs text-zinc-200 transition-colors hover:border-border-strong hover:bg-bg-elevated"
          type="button"
          onclick={() => (menuOpen = !menuOpen)}
          aria-haspopup="menu"
          aria-expanded={menuOpen}
          aria-label="Switch profile"
        >
          <span
            class="grid h-6 w-6 place-items-center rounded-full border border-border bg-bg text-[10px] font-medium uppercase text-zinc-300"
          >
            {$activeProfile.emoji || $activeProfile.name.charAt(0).toUpperCase()}
          </span>
          <span class="hidden sm:inline">{$activeProfile.name}</span>
          <span class="hidden h-1.5 w-1.5 rounded-full bg-accent sm:inline-block" aria-hidden="true"></span>
          <Icon name="chevron-down" size={12} />
        </button>
        {#if menuOpen}
          <div
            class="absolute right-0 mt-2 w-[min(17rem,calc(100vw-1.5rem))] overflow-hidden rounded-md border border-border bg-bg-elevated shadow-card"
            role="menu"
          >
            <div class="px-3 pt-2 font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500">
              Switch profile
            </div>
            <div class="py-1">
              {#each $allProfiles as p (p.id)}
                <button
                  class="flex w-full items-center gap-2 px-3 py-2 text-left text-xs transition-colors hover:bg-bg-subtle"
                  type="button"
                  role="menuitemradio"
                  aria-checked={p.id === $activeProfile.id}
                  onclick={() => switchTo(p)}
                >
                  <span
                    class="grid h-6 w-6 place-items-center rounded-full border border-border bg-bg text-[10px] font-medium uppercase text-zinc-300"
                  >
                    {p.emoji || p.name.charAt(0).toUpperCase()}
                  </span>
                  <span class="flex-1 text-zinc-200">{p.name}</span>
                  {#if p.id === $activeProfile.id}
                    <span class="h-1.5 w-1.5 rounded-full bg-accent" aria-hidden="true"></span>
                  {/if}
                </button>
              {/each}
            </div>
            <a
              href="/profiles"
              class="block border-t border-border px-3 py-2 text-xs text-zinc-300 transition-colors hover:bg-bg-subtle hover:text-white"
              role="menuitem"
              onclick={() => (menuOpen = false)}
            >
              Manage profiles
            </a>
          </div>
        {/if}
      </div>
    {/if}
    <button
      class="btn-ghost"
      type="button"
      onclick={logout}
      disabled={busy}
      aria-label="Sign out"
    >
      <Icon name="logout" />
      <span class="hidden sm:inline">Sign out</span>
    </button>
  </div>
</header>
