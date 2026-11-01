/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#090A0F',
        surface: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          800: '#1A1C28',
          850: '#141622',
          900: '#0E1017',
          950: '#090A0F',
        },
        brand: {
          violet: '#7C3AED',
          indigo: '#6366F1',
          cyan: '#06B6D4',
          emerald: '#10B981',
          rose: '#F43F5E',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-violet': '0 0 35px -5px rgba(124, 58, 237, 0.25)',
        'glow-cyan': '0 0 25px -5px rgba(6, 182, 212, 0.3)',
      },
      transitionTimingFunction: {
        'spring-smooth': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'spring-bouncy': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'pop-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'pop': {
          '0%': { transform: 'scale(0.95)' },
          '100%': { transform: 'scale(1)' },
        },
        'message-enter': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'shimmer-wave': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'fade-in': 'fade-in 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-up': 'slide-up 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'pop-in': 'pop-in 180ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'pop': 'pop 180ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'message-enter': 'message-enter 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'shimmer-wave': 'shimmer-wave 2.5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
