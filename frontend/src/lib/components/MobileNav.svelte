<script lang="ts">
  import { page } from '$app/stores';
  import Icon from './Icon.svelte';

  const links = [
    { href: '/', label: 'Home', icon: 'grid' },
    { href: '/chat', label: 'Mia', icon: 'chat' },
    { href: '/calendar', label: 'Calendar', icon: 'calendar' },
    { href: '/vault', label: 'Vault', icon: 'folder' },
    { href: '/businesses/jobcarver', label: 'Stats', icon: 'chart' }
  ];

  function active(href: string, current: string): boolean {
    if (href === '/') return current === '/';
    return current === href || current.startsWith(href + '/');
  }
</script>

<nav
  class="sticky bottom-0 z-20 flex shrink-0 border-t border-border bg-bg-subtle/95 safe-pb safe-px backdrop-blur md:hidden"
  aria-label="Primary"
>
  {#each links as l (l.href)}
    {@const a = active(l.href, $page.url.pathname)}
    <a
      href={l.href}
      class="relative flex flex-1 flex-col items-center justify-center gap-0.5 px-1 py-2 text-[11px] font-medium transition-colors active:bg-bg-elevated"
      class:text-white={a}
      class:text-slate-400={!a}
      aria-current={a ? 'page' : undefined}
      style="min-height: 56px;"
    >
      {#if a}
        <span
          class="absolute left-1/2 top-0 h-0.5 w-8 -translate-x-1/2 rounded-b-full bg-accent"
          aria-hidden="true"
        ></span>
      {/if}
      <Icon name={l.icon} size={20} />
      <span class="truncate">{l.label}</span>
    </a>
  {/each}
</nav>
