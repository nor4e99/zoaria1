/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './hooks/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        /* ZOARIA Brand Palette */
        brand: {
          50:  '#f0fdf9',
          100: '#ccfbef',
          200: '#99f6e0',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',  // primary teal
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
          950: '#042f2e',
        },
        sage: {
          50:  '#f4f9f4',
          100: '#e5f2e5',
          200: '#cce5cc',
          300: '#a3cfa3',
          400: '#74b274',
          500: '#4d944d',
          600: '#3a7a3a',
          700: '#2e5e2e',
          800: '#274d27',
          900: '#1f3d1f',
        },
        cream: {
          50:  '#fdfcf8',
          100: '#faf7ed',
          200: '#f4eed8',
          300: '#ecdeba',
          400: '#e0c98e',
          500: '#d4b062',
        },
        obsidian: {
          50:  '#f6f7f7',
          100: '#e1e4e4',
          200: '#c3c9c9',
          300: '#9aa3a3',
          400: '#6f7c7c',
          500: '#546161',
          600: '#404d4d',
          700: '#303b3b',
          800: '#1e2828',  // dark background
          900: '#111818',
          950: '#080e0e',
        },
        status: {
          healthy:     '#22c55e',
          overweight:  '#f59e0b',
          underweight: '#ef4444',
          danger:      '#dc2626',
        },
      },
      fontFamily: {
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        body:    ['"DM Sans"', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      boxShadow: {
        'card':  '0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.10), 0 16px 40px rgba(0,0,0,0.08)',
        'glow':  '0 0 20px rgba(20, 184, 166, 0.25)',
        'glow-lg': '0 0 40px rgba(20, 184, 166, 0.35)',
      },
      animation: {
        'fade-in':    'fadeIn 0.4s ease-out',
        'slide-up':   'slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-right':'slideRight 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'scale-in':   'scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'needle':     'needleSwing 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'shimmer':    'shimmer 2s linear infinite',
      },
      keyframes: {
        fadeIn:    { from: { opacity: '0' },                   to: { opacity: '1' } },
        slideUp:   { from: { opacity: '0', transform: 'translateY(20px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        slideRight:{ from: { opacity: '0', transform: 'translateX(-20px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
        scaleIn:   { from: { opacity: '0', transform: 'scale(0.92)' }, to: { opacity: '1', transform: 'scale(1)' } },
        needleSwing:{ from: { transform: 'rotate(-90deg)' },   to: { transform: 'rotate(var(--needle-angle))' } },
        pulseSoft: { '0%,100%': { opacity: '1' },              '50%': { opacity: '0.6' } },
        shimmer:   { from: { backgroundPosition: '-200% 0' },  to: { backgroundPosition: '200% 0' } },
      },
    },
  },
  plugins: [],
};
