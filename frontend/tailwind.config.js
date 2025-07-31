// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Pokemon-themed color extensions
      colors: {
        pokemon: {
          fire: '#EF4444',
          water: '#3B82F6',
          grass: '#10B981',
          electric: '#EAB308',
          psychic: '#8B5CF6',
          fighting: '#DC2626',
          poison: '#A855F7',
          ground: '#F59E0B',
          rock: '#78716C',
          bug: '#84CC16',
          ghost: '#6366F1',
          steel: '#6B7280',
          ice: '#60A5FA',
          dragon: '#4F46E5',
          dark: '#374151',
          fairy: '#EC4899',
          normal: '#9CA3AF',
          flying: '#93C5FD'
        }
      },
      
      // Custom animations for Pokemon theme
      animation: {
        'bounce-slow': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s infinite',
        'pokemon-float': 'pokemon-float 3s ease-in-out infinite',
        'type-glow': 'type-glow 2s ease-in-out infinite alternate',
        'ai-thinking': 'bounce 1.4s ease-in-out infinite both'
      },
      
      // Custom keyframes
      keyframes: {
        'pokemon-float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' }
        },
        'type-glow': {
          '0%': { boxShadow: '0 0 5px rgba(34, 197, 94, 0.3)' },
          '100%': { boxShadow: '0 0 15px rgba(34, 197, 94, 0.6)' }
        }
      },
      
      // Custom spacing for Pokemon cards
      spacing: {
        'card-sm': '5rem',
        'card-md': '8rem', 
        'card-lg': '10rem',
        'card-height-sm': '7rem',
        'card-height-md': '11rem',
        'card-height-lg': '14rem'
      },
      
      // Custom box shadows
      boxShadow: {
        'pokemon': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'pokemon-hover': '0 8px 25px rgba(0, 0, 0, 0.15)',
        'ai-glow': '0 0 20px rgba(59, 130, 246, 0.3)',
        'type-effective': '0 0 15px rgba(34, 197, 94, 0.4)'
      },
      
      // Custom gradients
      backgroundImage: {
        'pokemon-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'fire-gradient': 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)',
        'water-gradient': 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)',
        'grass-gradient': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        'electric-gradient': 'linear-gradient(135deg, #eab308 0%, #f59e0b 100%)',
        'game-board': 'linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 50%, #ddd6fe 100%)'
      }
    },
  },
  plugins: [],
}