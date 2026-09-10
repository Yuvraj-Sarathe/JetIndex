/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Rubik', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        canvas: '#150f23',
        card: {
          DEFAULT: '#1f1633',
          elevated: '#261b40',
          hover: '#2d1f4d',
        },
        ink: {
          deep: '#1f1633',
          night: '#150f23',
          border: '#362d59',
          borderLight: '#4a3b75',
          muted: '#b3a8c9',
          faint: '#786c91',
        },
        accent: {
          lime: '#c2ef4e',
          pink: '#fa7faa',
          violet: '#6a5fc1',
          violetDeep: '#422082',
          cyan: '#4ecdc4',
        },
      },
    },
  },
  plugins: [],
}
