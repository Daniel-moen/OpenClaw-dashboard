<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { api, ApiError } from '$lib/api';
  import { activeProfile } from '$lib/stores/profile';
  import { toast } from '$lib/stores/toast';
  import { formatRelative } from '$lib/format';
  import type { ChatMessage, ChatStatus } from '$lib/types';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import ErrorState from '$lib/components/ErrorState.svelte';
  import LoadingSkeleton from '$lib/components/LoadingSkeleton.svelte';
  import Icon from '$lib/components/Icon.svelte';

  let messages: ChatMessage[] = [];
  let status: ChatStatus | null = null;
  let loading = true;
  let sending = false;
  let error = '';
  let input = '';
  let scrollEl: HTMLDivElement | undefined;
  let textareaEl: HTMLTextAreaElement | undefined;

  const PROMPTS = [
    "Plan my week",
    "What did I do yesterday?",
    "Summarise JobCarver today",
    "Search the vault for invoices"
  ];

  async function load() {
    loading = true;
    error = '';
    try {
      const [s, msgs] = await Promise.all([api.chat.status(), api.chat.list()]);
      status = s;
      messages = msgs;
      await scrollToBottom();
    } catch (e) {
      error = e instanceof ApiError ? e.message : 'Failed to load chat';
    } finally {
      loading = false;
    }
  }

  async function scrollToBottom() {
    await tick();
    if (scrollEl) scrollEl.scrollTop = scrollEl.scrollHeight;
  }

  // Temp ids are negative so they can't collide with server ids.
  let tempIdCounter = -1;

  async function send() {
    const content = input.trim();
    if (!content || sending) return;
    sending = true;
    input = '';
    autoSize();

    // Optimistically show the user's message right away.
    const tempId = tempIdCounter--;
    const optimistic: ChatMessage = {
      id: tempId,
      role: 'user',
      content,
      profile_key: $activeProfile?.key ?? null,
      profile_name: $activeProfile?.name ?? null,
      created_at: new Date().toISOString()
    };
    messages = [...messages, optimistic];
    await scrollToBottom();

    try {
      const r = await api.chat.send(content);
      // Replace the optimistic message with the server version and append reply.
      messages = [...messages.filter((m) => m.id !== tempId), r.user, r.reply];
      if (status) status.online = r.online;
      await scrollToBottom();
    } catch (e) {
      // Roll back the optimistic message so the user can retry / edit.
      messages = messages.filter((m) => m.id !== tempId);
      toast(e instanceof ApiError ? e.message : 'Send failed', 'bad');
      input = content;
      autoSize();
    } finally {
      sending = false;
      textareaEl?.focus();
    }
  }

  async function clearAll() {
    if (!confirm('Clear the entire chat history?')) return;
    try {
      await api.chat.clear();
      messages = [];
      toast('Chat cleared', 'ok');
    } catch (e) {
      toast(e instanceof ApiError ? e.message : 'Clear failed', 'bad');
    }
  }

  function pickPrompt(p: string) {
    input = input ? `${input.trim()} ${p}` : p;
    textareaEl?.focus();
    autoSize();
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  function autoSize() {
    if (!textareaEl) return;
    textareaEl.style.height = 'auto';
    textareaEl.style.height = Math.min(textareaEl.scrollHeight, 200) + 'px';
  }

  onMount(load);
</script>

<div class="chat-shell flex flex-col gap-3">
  <header class="flex flex-wrap items-center justify-between gap-2">
    <div>
      <h2 class="text-xl font-semibold text-white">
        {status?.assistant_name ?? 'Mia'}
      </h2>
      <p class="text-xs text-slate-400">
        {#if status?.online}
          <span class="inline-flex items-center gap-1">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
            Online · {status.model}
          </span>
        {:else}
          <span class="inline-flex items-center gap-1">
            <span class="h-1.5 w-1.5 rounded-full bg-slate-500"></span>
            Offline · set <code class="text-slate-300">OPENAI_API_KEY</code> to enable replies
          </span>
        {/if}
      </p>
    </div>
    <div class="flex gap-2">
      <button class="btn-ghost" type="button" onclick={load} aria-label="Refresh">
        <Icon name="refresh" size={14} />
      </button>
      {#if messages.length > 0}
        <button class="btn-ghost" type="button" onclick={clearAll}>
          <Icon name="trash" size={14} /><span>Clear</span>
        </button>
      {/if}
    </div>
  </header>

  {#if error}<ErrorState message={error} onRetry={load} />{/if}

  <div
    bind:this={scrollEl}
    class="card flex-1 overflow-y-auto p-3 sm:p-4"
    aria-live="polite"
    aria-label="Conversation"
  >
    {#if loading && messages.length === 0}
      <LoadingSkeleton rows={4} />
    {:else if messages.length === 0}
      <div class="grid h-full place-items-center">
        <div class="max-w-md text-center">
          <span
            class="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-2xl bg-accent/15 text-lg font-bold text-accent-soft"
          >
            M
          </span>
          <h3 class="text-base font-semibold text-white">
            Hi{$activeProfile ? `, ${$activeProfile.name}` : ''}. What are we working on?
          </h3>
          <p class="mt-1 text-sm text-slate-400">
            Ask anything about JobCarver, the calendar, the vault, or your plan for the day.
          </p>
          <div class="mt-4 flex flex-wrap justify-center gap-2">
            {#each PROMPTS as p (p)}
              <button
                type="button"
                class="rounded-full border border-border bg-bg-subtle px-3 py-1 text-xs text-slate-300 hover:border-accent/50 hover:text-white"
                onclick={() => pickPrompt(p)}
              >
                {p}
              </button>
            {/each}
          </div>
        </div>
      </div>
    {:else}
      <ul class="space-y-3">
        {#each messages as m (m.id)}
          {@const isUser = m.role === 'user'}
          <li class="flex gap-2.5" class:flex-row-reverse={isUser}>
            <span
              class="grid h-7 w-7 shrink-0 place-items-center rounded-full text-[11px] font-bold"
              class:bg-accent={isUser}
              class:text-white={isUser}
              class:bg-bg-subtle={!isUser}
              class:text-accent-soft={!isUser}
              class:border={!isUser}
              class:border-border={!isUser}
              title={isUser ? (m.profile_name ?? 'You') : (status?.assistant_name ?? 'Mia')}
            >
              {#if isUser}
                {(m.profile_name ?? '?').charAt(0).toUpperCase()}
              {:else}
                M
              {/if}
            </span>
            <div
              class="max-w-[85%] rounded-2xl px-3 py-2 text-sm leading-relaxed sm:max-w-[75%]"
              class:bg-accent-muted={isUser}
              class:text-white={isUser}
              class:bg-bg-subtle={!isUser}
              class:text-slate-200={!isUser}
              class:border={!isUser}
              class:border-border={!isUser}
            >
              <p class="whitespace-pre-wrap break-words">{m.content}</p>
              <p
                class="mt-1 text-[10px] uppercase tracking-wide opacity-60"
                class:text-white={isUser}
                class:text-slate-400={!isUser}
              >
                {isUser
                  ? (m.profile_name ?? 'You')
                  : (status?.assistant_name ?? 'Mia')}
                · {formatRelative(m.created_at)}
              </p>
            </div>
          </li>
        {/each}
        {#if sending}
          <li class="flex gap-2.5">
            <span
              class="grid h-7 w-7 shrink-0 place-items-center rounded-full border border-border bg-bg-subtle text-[11px] font-bold text-accent-soft"
            >
              M
            </span>
            <div
              class="rounded-2xl border border-border bg-bg-subtle px-3 py-2 text-sm text-slate-400"
            >
              <span class="inline-flex items-center gap-1">
                <span class="dot"></span><span class="dot delay-150"></span><span
                  class="dot delay-300"
                ></span>
              </span>
            </div>
          </li>
        {/if}
      </ul>
    {/if}
  </div>

  <form
    onsubmit={(e) => {
      e.preventDefault();
      send();
    }}
    class="card flex items-end gap-2 p-2"
  >
    <textarea
      bind:this={textareaEl}
      bind:value={input}
      oninput={autoSize}
      onkeydown={onKey}
      rows="1"
      placeholder={status?.online
        ? `Message ${status.assistant_name}…`
        : 'Type a note (offline)'}
      class="min-h-[40px] flex-1 resize-none border-0 bg-transparent px-2 py-2 text-base leading-snug text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-0 sm:text-sm"
      maxlength="4000"
      aria-label="Message"
      autocapitalize="sentences"
      autocomplete="off"
    ></textarea>
    <button
      class="btn-primary"
      type="submit"
      disabled={sending || !input.trim()}
      aria-label="Send"
    >
      <Icon name="send" size={14} /><span class="hidden sm:inline">Send</span>
    </button>
  </form>
</div>

<style>
  /* Chat fills the viewport minus chrome. Topbar ~3.5rem, mobile nav ~3.5rem,
     plus main padding and safe-area insets. */
  .chat-shell {
    height: calc(
      100dvh - 3.5rem - 3.5rem - env(safe-area-inset-top) - env(safe-area-inset-bottom) - 1.5rem
    );
  }
  @media (min-width: 640px) {
    .chat-shell {
      height: calc(100dvh - 3.5rem - 3.5rem - env(safe-area-inset-bottom) - 2rem);
    }
  }
  @media (min-width: 768px) {
    .chat-shell {
      /* Desktop: sidebar visible, no bottom nav. */
      height: calc(100dvh - 3.5rem - 3rem);
    }
  }

  .dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 9999px;
    background-color: rgb(148 163 184);
    animation: pulse-dot 1.2s ease-in-out infinite;
  }
  .delay-150 {
    animation-delay: 0.15s;
  }
  .delay-300 {
    animation-delay: 0.3s;
  }
  @keyframes pulse-dot {
    0%,
    80%,
    100% {
      opacity: 0.2;
      transform: translateY(0);
    }
    40% {
      opacity: 1;
      transform: translateY(-2px);
    }
  }
</style>
