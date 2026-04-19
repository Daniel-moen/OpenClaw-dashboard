import type { Config } from 'tailwindcss';
import forms from '@tailwindcss/forms';

export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: '#0a0a0b',
          subtle: '#101013',
          elevated: '#16161a'
        },
        border: {
          DEFAULT: '#1f1f24',
          strong: '#2a2a31'
        },
        accent: {
          DEFAULT: '#c9a35b',
          soft: '#e3c389',
          muted: '#3a2f1c'
        },
        ok: '#7fb98b',
        warn: '#d6a85a',
        bad: '#d68a8a'
      },
      fontFamily: {
        display: [
          'Fraunces',
          'ui-serif',
          'Georgia',
          'Cambria',
          'Times New Roman',
          'serif'
        ],
        sans: [
          'Inter Tight',
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
        card: '0 1px 0 rgba(255,255,255,0.02), 0 12px 32px -20px rgba(0,0,0,0.7)',
        chrome: '0 1px 0 rgba(255,255,255,0.02), 0 1px 24px -8px rgba(0,0,0,0.6)'
      }
    }
  },
  plugins: [forms]
} satisfies Config;
