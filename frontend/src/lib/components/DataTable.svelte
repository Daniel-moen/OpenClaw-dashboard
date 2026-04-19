<script lang="ts">
  type Column = { key: string; label?: string; format?: (v: unknown) => string };

  export let title: string | undefined = undefined;
  export let rows: Record<string, unknown>[] = [];
  export let columns: Column[] | null = null;

  $: cols = (columns ??
    (rows[0]
      ? Object.keys(rows[0]).map((k) => ({ key: k, label: k.replace(/_/g, ' ') }))
      : [])) as Column[];

  function fmt(col: Column, v: unknown): string {
    if (col.format) return col.format(v);
    if (v === null || v === undefined) return '—';
    if (typeof v === 'number') return v.toLocaleString();
    return String(v);
  }
</script>

<div class="card overflow-hidden">
  {#if title}
    <div class="border-b border-border px-4 py-3 text-sm font-semibold text-slate-200">
      {title}
    </div>
  {/if}
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead class="bg-bg-subtle/60 text-left text-xs uppercase tracking-wide text-slate-400">
        <tr>
          {#each cols as c (c.key)}
            <th class="px-4 py-2 font-medium">{c.label ?? c.key}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each rows as row, i (i)}
          <tr class="border-t border-border text-slate-200">
            {#each cols as c (c.key)}
              <td class="px-4 py-2">{fmt(c, row[c.key])}</td>
            {/each}
          </tr>
        {:else}
          <tr>
            <td class="px-4 py-6 text-center text-sm text-slate-500" colspan={cols.length || 1}
              >No rows.</td
            >
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
