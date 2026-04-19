<script lang="ts">
  import { page } from '$app/stores';
  import Icon from './Icon.svelte';

  const links = [
    { href: '/', label: 'Home', icon: 'grid' },
    { href: '/businesses/jobcarver', label: 'JobCarver', icon: 'chart' },
    { href: '/calendar', label: 'Calendar', icon: 'calendar' },
    { href: '/vault', label: 'Vault', icon: 'folder' },
    { href: '/assistant', label: 'AI', icon: 'bolt' }
  ];

  function active(href: string, current: string): boolean {
    if (href === '/') return current === '/';
    return current === href || current.startsWith(href + '/');
  }
</script>

<nav
  class="sticky bottom-0 z-10 flex border-t border-border bg-bg-subtle/90 backdrop-blur md:hidden"
>
  {#each links as l (l.href)}
    {@const a = active(l.href, $page.url.pathname)}
    <a
      href={l.href}
      class="flex flex-1 flex-col items-center gap-0.5 py-2 text-[11px]"
      class:text-white={a}
      class:text-slate-400={!a}
    >
      <Icon name={l.icon} />
      <span>{l.label}</span>
    </a>
  {/each}
</nav>
