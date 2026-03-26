/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          base: '#080808', // The absolute background
          container: '#111111', // Main window background
          panel: '#161616', // Inner panels like the recommendation box
          card: '#1c1c1c', // Card backgrounds inside panels
        },
        accent: {
          cyan: '#00e5ff',
          fuchsia: '#e056fd',
          red: '#ff5e5e',
          green: '#4ade80',
        },
        text: {
          primary: '#ffffff',
          secondary: '#8a8a93',
          tertiary: '#52525b',
        },
        border: {
          light: 'rgba(255, 255, 255, 0.08)',
          glow: 'rgba(138, 43, 226, 0.4)', // Purple-ish glow for the main window framing
        }
      },
      fontFamily: {
        sans: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
        display: ['"Space Grotesk"', 'sans-serif'], // For big headers if needed
      },
      backgroundImage: {
        'dots': 'radial-gradient(rgba(255, 255, 255, 0.15) 1px, transparent 1px)',
      },
      boxShadow: {
        'glow-cyan': '0 0 15px rgba(0, 229, 255, 0.3)',
        'glow-fuchsia': '0 0 15px rgba(224, 86, 253, 0.3)',
      }
    },
  },
  plugins: [],
}
