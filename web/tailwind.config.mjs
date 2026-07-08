/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        graphite: {
          950: '#0C0D0E', // Darkest background
          900: '#121416', // Slate dark body background
          800: '#1C1F22', // Card & Panel Backgrounds
          700: '#2C3035', // Borders, gridlines
          600: '#495057', // Accent labels
          400: '#ADB5BD', // Body text
          100: '#E9ECEF', // Highlight text
          50: '#F8F9FA',  // Bright headings
        },
        caution: {
          yellow: '#FFC107',  // Interactive highlights / warnings
          orange: '#F97316',  // Secondary accents / high relevance
        },
        steel: {
          border: '#373B40',
          glare: '#4E545C'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'SF Mono', 'Menlo', 'monospace'],
        sans: ['Inter', 'SF Pro Display', 'system-ui', 'sans-serif'],
      },
      spacing: {
        'grid-xs': '4px',
        'grid-sm': '8px',
        'grid-md': '12px',
        'grid-lg': '16px',
        'grid-xl': '24px',
      },
      borderRadius: {
        'none': '0px',
        'sm': '2px',
        'DEFAULT': '4px',
      },
      boxShadow: {
        'flat-sm': '1px 1px 0px 0px #000000',
        'flat-md': '3px 3px 0px 0px #000000',
        'flat-lg': '5px 5px 0px 0px #000000',
        'flat-caution': '3px 3px 0px 0px #FFC107',
      }
    },
  },
  plugins: [],
}
