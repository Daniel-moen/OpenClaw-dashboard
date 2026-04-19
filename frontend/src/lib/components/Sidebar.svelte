<script lang="ts">
  import { page } from '$app/stores';
  import Icon from './Icon.svelte';

  const links = [
    { href: '/', label: 'Dashboard', icon: 'grid' },
    { href: '/businesses/jobcarver', label: 'JobCarver', icon: 'chart' },
    { href: '/businesses/cohesionsupps', label: 'CohesionSupps', icon: 'chart' },
    { href: '/calendar', label: 'Calendar', icon: 'calendar' },
    { href: '/skills', label: 'Skills', icon: 'sparkle' },
    { href: '/vault', label: 'Vault', icon: 'folder' },
    { href: '/assistant', label: 'Assistant', icon: 'bolt' },
    { href: '/profiles', label: 'Profiles', icon: 'user' }
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
    <span class="ml-auto text-[10px] uppercase tracking-widest text-slate-500">v0.1</span>
  </a>

  <nav class="flex-1 space-y-0.5 px-3">
    {#each links as l (l.href)}
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
        <Icon name={l.icon} />
        <span>{l.label}</span>
      </a>
    {/each}
  </nav>

  <div class="border-t border-border px-5 py-4 text-[11px] leading-relaxed text-slate-500">
    Internal command center.<br />Single-user. Built for Daniel.
  </div>
</aside>
