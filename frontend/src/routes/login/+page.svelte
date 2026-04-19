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
  <div class="w-full max-w-sm">
    <div class="card p-7">
      <div class="mb-6 flex items-center gap-3">
        <span class="brand-mark h-10 w-10 text-lg">O</span>
        <div class="leading-tight">
          <h1 class="font-display text-lg font-semibold tracking-tight text-zinc-100">Openclaw</h1>
          <p class="font-mono text-[10px] uppercase tracking-[0.22em] text-zinc-500">
            Internal · v0.2
          </p>
        </div>
      </div>

      <div class="divider-hair mb-5"></div>

      <form onsubmit={submit} class="space-y-4">
        <label class="block">
          <span class="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-zinc-400">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="11"
              height="11"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <rect x="3" y="11" width="18" height="11" rx="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
            Admin password
          </span>
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
          <p class="rounded-md border border-rose-500/20 bg-rose-500/5 px-3 py-2 text-xs text-rose-300">
            {error}
          </p>
        {/if}

        <button class="btn-primary w-full" type="submit" disabled={busy || !password}>
          {busy ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>

    <div class="mt-5 flex items-center justify-center gap-2 font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-600">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="9"
        height="9"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <rect x="3" y="11" width="18" height="11" rx="2" />
        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
      </svg>
      <span>Session-cookie auth · TLS required</span>
    </div>
  </div>
</div>
