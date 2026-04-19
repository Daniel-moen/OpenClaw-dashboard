<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { api, ApiError } from '$lib/api';
  import { authStatus } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';

  let password = '';
  let busy = false;
  let error = '';
  let pwInput: HTMLInputElement;

  onMount(() => pwInput?.focus());

  async function submit(e: SubmitEvent) {
    e.preventDefault();
    if (!password) return;
    busy = true;
    error = '';
    try {
      await api.auth.login(password);
      authStatus.set('in');
      const redirect = $page.url.searchParams.get('redirect') || '/';
      // Always go through the picker after a fresh sign-in so Mia knows who
      // she's talking to. The picker forwards on after a choice is made.
      toast('Welcome back', 'ok');
      goto(`/select-profile?redirect=${encodeURIComponent(redirect)}`);
    } catch (err) {
      error = err instanceof ApiError ? err.message : 'Login failed';
    } finally {
      busy = false;
    }
  }
</script>

<div class="grid h-full place-items-center px-4">
  <div class="card w-full max-w-sm p-6">
    <div class="mb-6 flex items-center gap-3">
      <span
        class="grid h-10 w-10 place-items-center rounded-xl bg-accent text-lg font-bold text-white"
        >O</span
      >
      <div>
        <h1 class="text-base font-semibold text-white">Openclaw</h1>
        <p class="text-xs text-slate-400">Internal command center</p>
      </div>
    </div>

    <form onsubmit={submit} class="space-y-3">
      <label class="block">
        <span class="mb-1 block text-xs font-medium text-slate-400">Admin password</span>
        <input
          bind:this={pwInput}
          type="password"
          class="input"
          bind:value={password}
          autocomplete="current-password"
          required
        />
      </label>

      {#if error}
        <p class="text-xs text-rose-300">{error}</p>
      {/if}

      <button class="btn-primary w-full" type="submit" disabled={busy || !password}>
        {busy ? 'Signing in…' : 'Sign in'}
      </button>
    </form>

    <p class="mt-6 text-center text-[11px] text-slate-500">
      Set <code class="text-slate-400">ADMIN_PASSWORD</code> in your env to change it.
    </p>
  </div>
</div>
