/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          bg: '#0a0a0f',
          DEFAULT: '#1e1e24',
          light: '#2a2a35',
        },
        accent: {
          gold: '#fbbf24',
          'gold-dim': 'rgba(251, 191, 36, 0.5)',
          'gold-light': 'rgba(251, 191, 36, 0.2)',
          blue: '#3b82f6',
          green: '#48bb78',
          red: '#f56565',
        },
        text: {
          primary: '#ffffff',
          secondary: '#a0aec0',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-glow': 'pulse-glow 3s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
        'marquee': 'marquee 30s linear infinite',
        'neon-flicker': 'neon-flicker 3s infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': {
            filter: 'drop-shadow(0 0 10px rgba(251, 191, 36, 0.2))',
            transform: 'scale(1)',
          },
          '50%': {
            filter: 'drop-shadow(0 0 25px rgba(251, 191, 36, 0.5))',
            transform: 'scale(1.05)',
          },
        },
        'spin': {
          '0%': {
            transform: 'rotate(0deg)',
          },
          '100%': {
            transform: 'rotate(360deg)',
          },
        },
        'marquee': {
          '0%': {
            transform: 'translate(100%)',
          },
          '100%': {
            transform: 'translate(-100%)',
          },
        },
        'neon-flicker': {
          '0%, 19%, 21%, 23%, 25%, 54%, 56%, 100%': {
            'text-shadow': '0 0 4px #fff, 0 0 11px #fff, 0 0 19px #fff, 0 0 40px #f00, 0 0 80px #f00',
            'color': '#fff',
            'opacity': '1',
          },
          '20%, 22%, 24%, 55%': {
            'text-shadow': 'none',
            'color': '#444',
            'opacity': '.5',
          },
        },
      },
    },
  },
  plugins: [],
}