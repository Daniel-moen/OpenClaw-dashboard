<script lang="ts">
  import { onMount } from 'svelte';
  import { api, ApiError } from '$lib/api';
  import { formatDate, formatDateTime } from '$lib/format';
  import { toast } from '$lib/stores/toast';
  import type { CalendarEvent } from '$lib/types';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import ErrorState from '$lib/components/ErrorState.svelte';
  import LoadingSkeleton from '$lib/components/LoadingSkeleton.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import Modal from '$lib/components/Modal.svelte';

  let events: CalendarEvent[] = [];
  let loading = true;
  let error = '';

  let cursor = startOfMonth(new Date());
  let selected: string | null = null;
  let modalOpen = false;
  let busy = false;
  let form = { title: '', date: today(), time: '09:00', location: '', notes: '' };

  function today(): string {
    return new Date().toISOString().slice(0, 10);
  }
  function startOfMonth(d: Date): Date {
    return new Date(d.getFullYear(), d.getMonth(), 1);
  }
  function isoDate(d: Date): string {
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  }

  async function load() {
    loading = true;
    error = '';
    try {
      events = await api.calendar.list();
    } catch (e) {
      error = e instanceof ApiError ? e.message : 'Failed to load events';
    } finally {
      loading = false;
    }
  }

  onMount(load);

  $: monthDays = (() => {
    const first = startOfMonth(cursor);
    const start = new Date(first);
    start.setDate(1 - first.getDay());
    return Array.from({ length: 42 }, (_, i) => {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      return d;
    });
  })();

  $: byDay = (() => {
    const map = new Map<string, CalendarEvent[]>();
    for (const ev of events) {
      const key = ev.starts_at.slice(0, 10);
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(ev);
    }
    return map;
  })();

  $: agenda = (() => {
    const now = new Date().toISOString();
    if (selected) return (byDay.get(selected) ?? []).slice().sort(by);
    return events.filter((e) => e.starts_at >= now).slice(0, 30).sort(by);
  })();

  function by(a: CalendarEvent, b: CalendarEvent): number {
    return a.starts_at.localeCompare(b.starts_at);
  }

  function shiftMonth(n: number) {
    cursor = new Date(cursor.getFullYear(), cursor.getMonth() + n, 1);
  }

  function openNew(date?: string) {
    form = { title: '', date: date ?? today(), time: '09:00', location: '', notes: '' };
    modalOpen = true;
  }

  async function submit(e: SubmitEvent) {
    e.preventDefault();
    if (!form.title || !form.date) return;
    busy = true;
    try {
      const starts = new Date(`${form.date}T${form.time || '09:00'}:00`);
      await api.calendar.create({
        title: form.title,
        starts_at: starts.toISOString(),
        location: form.location || undefined,
        notes: form.notes || undefined
      });
      toast('Event added', 'ok');
      modalOpen = false;
      await load();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Could not add event', 'bad');
    } finally {
      busy = false;
    }
  }

  async function remove(id: number) {
    if (!confirm('Delete this event?')) return;
    try {
      await api.calendar.remove(id);
      toast('Event deleted', 'ok');
      await load();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Delete failed', 'bad');
    }
  }
</script>

<div class="space-y-6">
  <header class="flex flex-wrap items-end justify-between gap-3">
    <div>
      <h2 class="text-xl font-semibold text-white">Calendar</h2>
      <p class="text-sm text-slate-400">Plan your week. Tap a day to filter the agenda.</p>
    </div>
    <button class="btn-primary" type="button" onclick={() => openNew(selected ?? undefined)}>
      <Icon name="plus" /> <span>New event</span>
    </button>
  </header>

  {#if error}<ErrorState message={error} onRetry={load} />{/if}

  <div class="grid gap-4 lg:grid-cols-3">
    <div class="card p-4 lg:col-span-2">
      <div class="mb-3 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <button class="btn-ghost" type="button" onclick={() => shiftMonth(-1)} aria-label="Prev"
            >‹</button
          >
          <h3 class="text-sm font-semibold text-slate-200">
            {cursor.toLocaleString(undefined, { month: 'long', year: 'numeric' })}
          </h3>
          <button class="btn-ghost" type="button" onclick={() => shiftMonth(1)} aria-label="Next"
            >›</button
          >
        </div>
        <button
          class="text-xs text-slate-400 hover:text-white"
          type="button"
          onclick={() => {
            cursor = startOfMonth(new Date());
            selected = null;
          }}>Today</button
        >
      </div>

      <div class="grid grid-cols-7 gap-1 text-center text-[10px] uppercase tracking-wide text-slate-500">
        {#each ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] as d (d)}
          <div class="py-1">{d}</div>
        {/each}
      </div>
      <div class="grid grid-cols-7 gap-1">
        {#each monthDays as d, i (i)}
          {@const key = isoDate(d)}
          {@const inMonth = d.getMonth() === cursor.getMonth()}
          {@const isToday = key === today()}
          {@const isSel = key === selected}
          {@const dayEvents = byDay.get(key) ?? []}
          <button
            type="button"
            class="flex aspect-square min-h-[60px] flex-col items-stretch rounded-md border p-1 text-left text-xs transition-colors"
            class:border-border={!isSel && !isToday}
            class:bg-bg-subtle={inMonth && !isSel}
            class:opacity-50={!inMonth}
            class:border-accent={isSel}
            class:bg-accent-muted={isSel}
            class:ring-1={isToday && !isSel}
            class:ring-accent={isToday && !isSel}
            onclick={() => (selected = isSel ? null : key)}
            ondblclick={() => openNew(key)}
            aria-pressed={isSel}
            aria-current={isToday ? 'date' : undefined}
          >
            <span
              class="inline-flex items-center gap-1 font-medium"
              class:text-white={isToday || isSel}
              class:text-slate-300={!(isToday || isSel)}
            >
              {d.getDate()}
              {#if isToday}
                <span class="h-1.5 w-1.5 rounded-full bg-accent"></span>
              {/if}
            </span>
            <div class="mt-auto space-y-0.5 overflow-hidden">
              {#each dayEvents.slice(0, 2) as ev (ev.id)}
                <div class="truncate rounded bg-accent/20 px-1 text-[10px] text-accent-soft">
                  {ev.title}
                </div>
              {/each}
              {#if dayEvents.length > 2}
                <div class="text-[10px] text-slate-500">+{dayEvents.length - 2} more</div>
              {/if}
            </div>
          </button>
        {/each}
      </div>
    </div>

    <div class="card p-4">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-200">
          {selected ? formatDate(selected + 'T00:00:00') : 'Upcoming'}
        </h3>
        {#if selected}
          <button class="text-xs text-slate-400 hover:text-white" onclick={() => (selected = null)}
            >Clear</button
          >
        {/if}
      </div>
      {#if loading}
        <LoadingSkeleton rows={5} />
      {:else if agenda.length === 0}
        <EmptyState
          icon="calendar"
          title={selected ? 'No events that day' : 'Nothing upcoming'}
          message="Add an event to get started."
        />
      {:else}
        <ul class="divide-y divide-border">
          {#each agenda as ev (ev.id)}
            <li class="flex items-start justify-between gap-3 py-3">
              <div class="min-w-0">
                <p class="truncate text-sm font-medium text-slate-100">{ev.title}</p>
                <p class="text-xs text-slate-500">{formatDateTime(ev.starts_at)}</p>
                {#if ev.location}
                  <p class="text-xs text-slate-500">{ev.location}</p>
                {/if}
              </div>
              <button
                class="text-slate-500 hover:text-rose-400"
                type="button"
                aria-label="Delete event"
                onclick={() => remove(ev.id)}
              >
                <Icon name="trash" size={16} />
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  </div>
</div>

{#if modalOpen}
  <Modal onClose={() => (modalOpen = false)} labelledBy="newevent-title">
    <form class="card w-full max-w-md p-5" onsubmit={submit}>
      <h3 id="newevent-title" class="mb-4 text-base font-semibold text-white">New event</h3>
      <div class="space-y-3">
        <label class="block">
          <span class="mb-1 block text-xs text-slate-400">Title</span>
          <input class="input" bind:value={form.title} required maxlength="200" />
        </label>
        <div class="grid grid-cols-2 gap-3">
          <label class="block">
            <span class="mb-1 block text-xs text-slate-400">Date</span>
            <input class="input" type="date" bind:value={form.date} required />
          </label>
          <label class="block">
            <span class="mb-1 block text-xs text-slate-400">Time</span>
            <input class="input" type="time" bind:value={form.time} />
          </label>
        </div>
        <label class="block">
          <span class="mb-1 block text-xs text-slate-400">Location</span>
          <input class="input" bind:value={form.location} maxlength="200" />
        </label>
        <label class="block">
          <span class="mb-1 block text-xs text-slate-400">Notes</span>
          <textarea class="input" rows="3" bind:value={form.notes} maxlength="2000"></textarea>
        </label>
      </div>
      <div class="mt-4 flex justify-end gap-2">
        <button class="btn-ghost" type="button" onclick={() => (modalOpen = false)}>Cancel</button>
        <button class="btn-primary" type="submit" disabled={busy}>
          {busy ? 'Saving…' : 'Add event'}
        </button>
      </div>
    </form>
  </Modal>
{/if}
