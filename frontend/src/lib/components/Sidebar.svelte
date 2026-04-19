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
  class="hidden h-full w-60 shrink-0 flex-col border-r border-border bg-bg-subtle/60 backdrop-blur md:flex"
>
  <a href="/" class="flex items-center gap-2 px-5 py-5">
    <span
      class="grid h-8 w-8 place-items-center rounded-lg bg-accent font-bold text-white shadow-card"
      >O</span
    >
    <span class="text-sm font-semibold tracking-wide text-slate-100">Openclaw</span>
    <span class="ml-auto text-[10px] uppercase tracking-widest text-slate-500">v0.2</span>
  </a>

  <nav class="flex-1 space-y-4 overflow-y-auto px-3 pb-4">
    {#each groups as group (group.label)}
      <div>
        <p class="mb-1 px-3 text-[10px] uppercase tracking-widest text-slate-500">
          {group.label}
        </p>
        <div class="space-y-0.5">
          {#each group.items as l (l.href)}
            {@const active = isActive(l.href, $page.url.pathname)}
            <a
              href={l.href}
              class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
              class:bg-accent-muted={active}
              class:text-white={active}
              class:text-slate-300={!active}
              class:hover:bg-bg-elevated={!active}
              class:hover:text-white={!active}
            >
              <Icon name={l.icon} size={16} />
              <span>{l.label}</span>
            </a>
          {/each}
        </div>
      </div>
    {/each}
  </nav>

  <div class="border-t border-border px-5 py-4 text-[11px] leading-relaxed text-slate-500">
    Internal command center.
  </div>
</aside>
