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
        canvas: '#0a0a0a',
        primary: {
          DEFAULT: '#faff69',
          active: '#e6eb52',
          disabled: '#3a3a1f',
        },
        card: {
          DEFAULT: '#141414',
          soft: '#121212',
          card: '#1a1a1a',
          elevated: '#242424',
          hover: '#2a2a2a',
        },
        hairline: {
          DEFAULT: '#2a2a2a',
          strong: '#3a3a3a',
        },
        ink: {
          DEFAULT: '#ffffff',
          body: '#cccccc',
          strong: '#e6e6e6',
          muted: '#888888',
          faint: '#5a5a5a',
          border: '#2a2a2a',
          borderLight: '#3a3a3a',
          night: '#0a0a0a',
          deep: '#141414',
        },
        accent: {
          yellow: '#faff69',
          lime: '#faff69',
          emerald: '#22c55e',
          rose: '#ef4444',
          blue: '#3b82f6',
          cyan: '#38bdf8',
          pink: '#ef4444',
          violet: '#3b82f6',
          violetDeep: '#141414',
        },
      },
    },
  },
  plugins: [],
}
