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
        background: '#1E1F22',
        surface: {
          50: '#F7F8FA',
          100: '#FFFFFF',
          200: '#EBECF0',
          700: '#43454A',
          750: '#393B40',
          800: '#393B40',
          850: '#2B2D30',
          900: '#1E1F22',
          950: '#191A1C',
        },
        brand: {
          primary: '#3574F0',
          hover: '#3064D0',
          selection: '#2E436E',
          success: '#5FAD65',
          warning: '#E3A83F',
          danger: '#FA5252',
          purple: '#C77DBB',
          cyan: '#3592C4',
          violet: '#7C3AED',
          indigo: '#6366F1',
          emerald: '#5FAD65',
          rose: '#FA5252',
        },
        ij: {
          canvas: '#1E1F22',
          panel: '#2B2D30',
          popup: '#393B40',
          border: '#393B40',
          borderLight: '#43454A',
          text: '#DFE1E5',
          textMuted: '#868A91',
          blue: '#3574F0',
          green: '#5FAD65',
          amber: '#E3A83F',
          red: '#FA5252',
          purple: '#C77DBB',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-blue': '0 0 25px -5px rgba(53, 116, 240, 0.45)',
        'glow-green': '0 0 25px -5px rgba(95, 173, 101, 0.45)',
        'glow-violet': '0 0 35px -5px rgba(124, 58, 237, 0.25)',
        'glow-cyan': '0 0 25px -5px rgba(6, 182, 212, 0.3)',
        'glow-emerald': '0 0 25px -5px rgba(95, 173, 101, 0.35)',
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
