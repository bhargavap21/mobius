/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0a0a0a',
          surface: '#1a1a1a',
          border: '#2a2a2a',
          hover: '#252525',
        },
        accent: {
          DEFAULT: '#7c3aed',
          primary: '#7c3aed',
          light: '#8b5cf6',
          dark: '#5b21b6',
          600: '#9333ea',
          400: '#c084fc',
          success: '#10b981',
          warning: '#f59e0b',
          danger: '#ef4444',
        },
        fg: {
          DEFAULT: '#e5e7eb',
          muted: '#9ca3af',
        },
        line: '#23262f',
      },
      animation: {
        'spin-slow': 'spin 8s linear infinite',
        'spin-reverse': 'spin 10s linear infinite reverse',
      }
    },
  },
  plugins: [],
}

