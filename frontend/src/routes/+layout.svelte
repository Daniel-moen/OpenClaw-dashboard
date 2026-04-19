<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import { authStatus } from '$lib/stores/auth';
  import { activeProfile, allProfiles } from '$lib/stores/profile';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import Topbar from '$lib/components/Topbar.svelte';
  import MobileNav from '$lib/components/MobileNav.svelte';
  import Toaster from '$lib/components/Toaster.svelte';

  let checking = true;

  onMount(async () => {
    try {
      const me = await api.me();
      authStatus.set(me.authenticated ? 'in' : 'out');
      activeProfile.set(me.profile);

      if (!me.authenticated) {
        if ($page.url.pathname !== '/login') {
          const redirect = encodeURIComponent($page.url.pathname + $page.url.search);
          goto(`/login?redirect=${redirect}`, { replaceState: true });
        }
      } else {
        // Preload profile list for switcher.
        try {
          allProfiles.set(await api.profiles.list());
        } catch {
          /* non-fatal */
        }
        if (!me.profile && $page.url.pathname !== '/select-profile') {
          const redirect = encodeURIComponent($page.url.pathname + $page.url.search);
          goto(`/select-profile?redirect=${redirect}`, { replaceState: true });
        }
      }
    } catch {
      authStatus.set('out');
      if ($page.url.pathname !== '/login') goto('/login', { replaceState: true });
    } finally {
      checking = false;
    }
  });

  $: isLogin = $page.url.pathname === '/login';
  $: isPicker = $page.url.pathname === '/select-profile';
  $: chromeless = isLogin || isPicker;
</script>

{#if chromeless}
  <slot />
{:else if checking || $authStatus === 'unknown'}
  <div class="grid h-full place-items-center px-4 text-sm text-slate-500">Loading…</div>
{:else if $authStatus === 'in'}
  <div class="flex h-full">
    <Sidebar />
    <div class="flex min-w-0 flex-1 flex-col">
      <Topbar />
      <main class="min-w-0 flex-1 overflow-x-hidden overflow-y-auto p-3 sm:p-4 md:p-6">
        <div class="mx-auto w-full max-w-7xl">
          <slot />
        </div>
      </main>
      <MobileNav />
    </div>
  </div>
{:else}
  <div class="grid h-full place-items-center px-4 text-sm text-slate-500">Redirecting…</div>
{/if}

<Toaster />
