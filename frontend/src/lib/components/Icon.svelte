<script lang="ts">
  export let name: string;
  export let size = 18;

  const paths: Record<string, string> = {
    grid: 'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z',
    chart: 'M4 20V10m6 10V4m6 16v-7m6 7V8',
    calendar:
      'M7 3v3M17 3v3M3 9h18M5 5h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z',
    sparkle:
      'M12 3l1.8 4.5L18 9l-4.2 1.5L12 15l-1.8-4.5L6 9l4.2-1.5zM19 14l.9 2.2L22 17l-2.1.8L19 20l-.9-2.2L16 17l2.1-.8z',
    folder: 'M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z',
    bolt: 'M13 2L4 14h7l-1 8 9-12h-7z',
    plus: 'M12 5v14M5 12h14',
    search: 'M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm10 2-4.35-4.35',
    upload: 'M12 16V4m0 0-4 4m4-4 4 4M4 20h16',
    download: 'M12 4v12m0 0 4-4m-4 4-4-4M4 20h16',
    trash: 'M4 7h16M9 7V4h6v3M6 7l1 13a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-13',
    logout: 'M15 12H3m0 0 4-4m-4 4 4 4M21 12V6a2 2 0 0 0-2-2h-6m8 14v-2a2 2 0 0 0-2-2h-6',
    check: 'M5 13l4 4L19 7',
    x: 'M6 6l12 12M6 18 18 6',
    refresh: 'M21 12a9 9 0 1 1-3-6.7L21 8m0 0V3m0 5h-5',
    copy: 'M9 9h10v10H9zM5 15V5h10',
    edit: 'M4 20h4l10-10-4-4L4 16zM14 6l4 4',
    'chevron-down': 'M6 9l6 6 6-6',
    user: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0',
    chat: 'M21 12a8 8 0 0 1-11.6 7.1L4 21l1.9-5.4A8 8 0 1 1 21 12z',
    send: 'M22 2 11 13M22 2l-7 20-4-9-9-4z'
  };
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="1.8"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
>
  <path d={paths[name] ?? paths.grid} />
</svg>
