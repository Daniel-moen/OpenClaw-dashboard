<script lang="ts">
  import { page } from '$app/stores';
  import Icon from './Icon.svelte';

  type NavLink = { href: string; label: string; icon: string };
  type NavGroup = { label: string; items: NavLink[] };

  const groups: NavGroup[] = [
    {
      label: 'Pinned',
      items: [
        { href: '/', label: 'Dashboard', icon: 'grid' },
        { href: '/chat', label: 'Chat with Mia', icon: 'chat' }
      ]
    },
    {
      label: 'Operations',
      items: [
        { href: '/calendar', label: 'Calendar', icon: 'calendar' },
        { href: '/vault', label: 'Vault', icon: 'folder' },
        { href: '/skills', label: 'Skills', icon: 'sparkle' },
        { href: '/assistant', label: 'Quick actions', icon: 'bolt' }
      ]
    },
    {
      label: 'Brands',
      items: [
        { href: '/businesses/jobcarver', label: 'JobCarver', icon: 'chart' },
        { href: '/businesses/cohesionsupps', label: 'CohesionSupps', icon: 'chart' }
      ]
    },
    {
      label: 'Workspace',
      items: [{ href: '/profiles', label: 'Profiles', icon: 'user' }]
    }
  ];

  function isActive(href: string, current: string): boolean {
    if (href === '/') return current === '/';
    return current === href || current.startsWith(href + '/');
  }
</script>

<aside
  class="hidden h-full w-64 shrink-0 flex-col border-r border-border bg-bg-subtle/50 backdrop-blur md:flex"
>
  <a href="/" class="flex items-center gap-3 px-5 py-5">
    <span class="brand-mark h-9 w-9 text-base">O</span>
    <span class="flex flex-col leading-tight">
      <span class="font-display text-base font-semibold tracking-tight text-zinc-100">Openclaw</span>
      <span class="font-mono text-[9px] uppercase tracking-[0.22em] text-zinc-600">v0.2 · internal</span>
    </span>
  </a>

  <div class="mx-5 divider-hair"></div>

  <nav class="flex-1 space-y-5 overflow-y-auto px-3 pb-4 pt-4">
    {#each groups as group (group.label)}
      <div>
        <p class="mb-1.5 px-3 font-display text-[11px] italic tracking-wide text-zinc-500">
          {group.label}
        </p>
        <div class="space-y-0.5">
          {#each group.items as l (l.href)}
            {@const active = isActive(l.href, $page.url.pathname)}
            <a
              href={l.href}
              class="relative flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors"
              class:bg-bg-elevated={active}
              class:text-white={active}
              class:text-zinc-400={!active}
              class:hover:bg-bg-elevated={!active}
              class:hover:text-zinc-100={!active}
            >
              {#if active}
                <span
                  class="absolute left-0 top-1/2 h-5 w-[2px] -translate-y-1/2 rounded-r-full bg-accent"
                  aria-hidden="true"
                ></span>
              {/if}
              <Icon name={l.icon} size={16} />
              <span>{l.label}</span>
            </a>
          {/each}
        </div>
      </div>
    {/each}
  </nav>

  <div class="border-t border-border px-5 py-4">
    <p class="font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-600">
      Command center
    </p>
    <p class="mt-1 font-display text-xs italic text-zinc-500">
      Quietly in control.
    </p>
  </div>
</aside>
