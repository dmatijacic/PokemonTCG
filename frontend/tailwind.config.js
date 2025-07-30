// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pokemon: {
          fire: '#FF6B35',
          water: '#3B82F6',
          grass: '#10B981',
          electric: '#FCD34D',
          psychic: '#8B5CF6',
          fighting: '#EF4444',
          dark: '#374151',
          steel: '#6B7280'
        }
      },
      animation: {
        'bounce-slow': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s infinite'
      }
    },
  },
  plugins: [],
}