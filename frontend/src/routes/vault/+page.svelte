<script lang="ts">
  import { onMount } from 'svelte';
  import { api, ApiError } from '$lib/api';
  import { formatBytes, formatRelative } from '$lib/format';
  import { toast } from '$lib/stores/toast';
  import type { VaultFile } from '$lib/types';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import ErrorState from '$lib/components/ErrorState.svelte';
  import LoadingSkeleton from '$lib/components/LoadingSkeleton.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import Modal from '$lib/components/Modal.svelte';

  let files: VaultFile[] = [];
  let loading = true;
  let error = '';
  let q = '';
  let uploading = false;
  let drag = false;
  let preview: VaultFile | null = null;
  let inputEl: HTMLInputElement;

  async function load() {
    loading = true;
    error = '';
    try {
      files = await api.vault.list(q || undefined);
    } catch (e) {
      error = e instanceof ApiError ? e.message : 'Failed to load files';
    } finally {
      loading = false;
    }
  }

  onMount(load);

  let searchTimer: ReturnType<typeof setTimeout> | null = null;
  $: if (q !== undefined) {
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(load, 250);
  }

  async function uploadFiles(list: FileList | File[]) {
    const items = Array.from(list);
    if (!items.length) return;
    uploading = true;
    try {
      for (const f of items) {
        try {
          await api.vault.upload(f);
          toast(`Uploaded ${f.name}`, 'ok');
        } catch (e) {
          toast(e instanceof ApiError ? `${f.name}: ${e.message}` : `${f.name} failed`, 'bad');
        }
      }
      await load();
    } finally {
      uploading = false;
    }
  }

  function onFileInput(e: Event) {
    const t = e.target as HTMLInputElement;
    if (t.files) uploadFiles(t.files);
    t.value = '';
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    drag = false;
    if (e.dataTransfer?.files) uploadFiles(e.dataTransfer.files);
  }

  async function remove(f: VaultFile) {
    if (!confirm(`Delete ${f.name}?`)) return;
    try {
      await api.vault.remove(f.id);
      toast('Deleted', 'ok');
      await load();
    } catch (e) {
      toast(e instanceof ApiError ? e.message : 'Delete failed', 'bad');
    }
  }

  function isPreviewable(f: VaultFile): boolean {
    return f.mime.startsWith('image/') || f.mime.startsWith('text/') || f.mime === 'application/pdf';
  }
</script>

<div class="space-y-6">
  <header class="flex flex-wrap items-end justify-between gap-3">
    <div>
      <h2 class="text-xl font-semibold text-white">Storage vault</h2>
      <p class="text-sm text-slate-400">Drop files to upload. Validated, deduped, secure.</p>
    </div>
    <button class="btn-primary" type="button" onclick={() => inputEl.click()}>
      <Icon name="upload" /> <span>Upload</span>
    </button>
    <input bind:this={inputEl} type="file" multiple class="hidden" onchange={onFileInput} />
  </header>

  <div
    class="rounded-xl border border-dashed transition-colors"
    class:border-border={!drag}
    class:bg-bg-subtle={!drag}
    class:border-accent={drag}
    class:bg-accent-muted={drag}
    role="region"
    aria-label="Upload drop zone"
    ondragover={(e) => {
      e.preventDefault();
      drag = true;
    }}
    ondragleave={() => (drag = false)}
    ondrop={onDrop}
  >
    <div class="flex items-center justify-between gap-3 p-4">
      <div class="flex items-center gap-3 text-sm text-slate-400">
        <Icon name="upload" />
        <span>{drag ? 'Drop to upload' : uploading ? 'Uploading…' : 'Drag files here or use Upload'}</span>
      </div>
      <div class="relative w-64 max-w-full">
        <input class="input pl-8" placeholder="Search files…" bind:value={q} />
        <span class="pointer-events-none absolute left-2 top-1/2 -translate-y-1/2 text-slate-500">
          <Icon name="search" size={14} />
        </span>
      </div>
    </div>
  </div>

  {#if error}<ErrorState message={error} onRetry={load} />{/if}

  {#if loading}
    <div class="card p-4"><LoadingSkeleton rows={6} /></div>
  {:else if files.length === 0}
    <EmptyState
      icon="folder"
      title={q ? 'No files match' : 'Vault is empty'}
      message={q ? 'Try a different search.' : 'Upload your first file using the button above.'}
    />
  {:else}
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-bg-subtle/60 text-left text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-4 py-2 font-medium">Name</th>
              <th class="px-4 py-2 font-medium">Type</th>
              <th class="px-4 py-2 font-medium">Size</th>
              <th class="px-4 py-2 font-medium">Uploaded</th>
              <th class="px-4 py-2 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each files as f (f.id)}
              <tr class="border-t border-border text-slate-200">
                <td class="px-4 py-2">
                  <div class="font-medium text-slate-100">{f.name}</div>
                  <div class="font-mono text-[11px] text-slate-500">{f.sha256.slice(0, 12)}…</div>
                </td>
                <td class="px-4 py-2 text-xs text-slate-400">{f.mime}</td>
                <td class="px-4 py-2 text-xs text-slate-400">{formatBytes(f.size)}</td>
                <td class="px-4 py-2 text-xs text-slate-400">{formatRelative(f.created_at)}</td>
                <td class="px-4 py-2">
                  <div class="flex justify-end gap-1">
                    {#if isPreviewable(f)}
                      <button
                        class="btn-ghost"
                        type="button"
                        aria-label="Preview"
                        onclick={() => (preview = f)}
                      >
                        <Icon name="search" size={14} />
                      </button>
                    {/if}
                    <a
                      class="btn-ghost"
                      href={api.vault.downloadUrl(f.id)}
                      aria-label="Download"
                    >
                      <Icon name="download" size={14} />
                    </a>
                    <button
                      class="btn-ghost text-rose-400 hover:text-rose-300"
                      type="button"
                      aria-label="Delete"
                      onclick={() => remove(f)}
                    >
                      <Icon name="trash" size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>

{#if preview}
  <Modal onClose={() => (preview = null)} labelledBy="preview-title">
    <div class="card w-full max-w-3xl overflow-hidden">
      <div class="flex items-center justify-between border-b border-border px-4 py-3">
        <div class="min-w-0">
          <p id="preview-title" class="truncate text-sm font-semibold text-slate-100">
            {preview.name}
          </p>
          <p class="text-xs text-slate-500">{preview.mime} · {formatBytes(preview.size)}</p>
        </div>
        <button class="btn-ghost" type="button" onclick={() => (preview = null)}>
          <Icon name="x" size={14} /><span>Close</span>
        </button>
      </div>
      <div class="max-h-[70vh] overflow-auto bg-bg-subtle p-3">
        {#if preview.mime.startsWith('image/')}
          <img src={api.vault.previewUrl(preview.id)} alt={preview.name} class="mx-auto max-h-[60vh]" />
        {:else if preview.mime === 'application/pdf'}
          <iframe
            src={api.vault.previewUrl(preview.id)}
            title={preview.name}
            class="h-[65vh] w-full bg-white"
          ></iframe>
        {:else}
          <iframe
            src={api.vault.previewUrl(preview.id)}
            title={preview.name}
            class="h-[60vh] w-full bg-bg"
          ></iframe>
        {/if}
      </div>
    </div>
  </Modal>
{/if}
