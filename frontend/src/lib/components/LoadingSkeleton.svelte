<script lang="ts">
  export let rows = 3;
  export let height = 16;
</script>

<div class="space-y-2">
  {#each Array(rows) as _, i (i)}
    <div
      class="animate-pulse rounded-md bg-bg-elevated"
      style="height: {height}px; width: {Math.round(60 + Math.random() * 40)}%;"
    ></div>
  {/each}
</div>
