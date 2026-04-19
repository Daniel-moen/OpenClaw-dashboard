import type { Config } from 'tailwindcss';
import forms from '@tailwindcss/forms';

export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: '#0b0d12',
          subtle: '#11141b',
          elevated: '#161a23'
        },
        border: {
          DEFAULT: '#222732',
          strong: '#2d3340'
        },
        accent: {
          DEFAULT: '#7c5cff',
          soft: '#a18fff',
          muted: '#3b3270'
        },
        ok: '#34d399',
        warn: '#f59e0b',
        bad: '#f87171'
      },
      fontFamily: {
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'Segoe UI',
          'sans-serif'
        ],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace']
      },
      boxShadow: {
        card: '0 1px 0 rgba(255,255,255,0.03), 0 8px 24px -12px rgba(0,0,0,0.6)'
      }
    }
  },
  plugins: [forms]
} satisfies Config;
