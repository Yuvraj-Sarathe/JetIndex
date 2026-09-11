/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        canvas: '#000000',
        primary: {
          DEFAULT: '#faff69',
          active: '#e6eb52',
          disabled: '#3a3a1f',
        },
        card: {
          DEFAULT: '#0d0d0d',
          soft: '#080808',
          card: '#121212',
          elevated: '#1a1a1a',
          hover: '#222222',
        },
        surface: {
          DEFAULT: '#0d0d0d',
          soft: '#080808',
          card: '#121212',
          elevated: '#1a1a1a',
        },
        hairline: {
          DEFAULT: '#222222',
          strong: '#333333',
        },
        ink: {
          DEFAULT: '#ffffff',
          body: '#cccccc',
          strong: '#e6e6e6',
          muted: '#888888',
          faint: '#5a5a5a',
          border: '#222222',
          borderLight: '#333333',
          night: '#000000',
          deep: '#0a0a0a',
        },
        accent: {
          yellow: '#faff69',
          lime: '#faff69',
          emerald: '#22c55e',
          rose: '#ef4444',
          blue: '#3b82f6',
          cyan: '#38bdf8',
        },
      },
    },
  },
  plugins: [],
}
