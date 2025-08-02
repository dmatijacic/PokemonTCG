// frontend/src/main.ts
import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';

// Import the enhanced Pokemon game board with backend integration
import EnhancedPokemonGameBoard from './components/EnhancedPokemonGameBoard';

console.log('🎮 Starting Pokemon TCG AI Education Platform...');
console.log('🤖 Enhanced version with backend AI integration');

const container = document.getElementById('app');
if (container) {
  const root = createRoot(container);
  
  // Use the enhanced component with backend integration
  root.render(React.createElement(EnhancedPokemonGameBoard));
  
  console.log('✅ Enhanced Pokemon game loaded successfully!');
  console.log('🔗 Connecting to backend AI server...');
} else {
  console.error('❌ Could not find app container element');
}

// Add global error handling for Pokemon game
window.addEventListener('error', (event) => {
  console.error('🎮 Pokemon Game Error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('🎮 Pokemon Game Promise Rejection:', event.reason);
});

// Log connection attempts for debugging
console.log('🌐 Backend should be running at: http://localhost:8000');
console.log('⚡ WebSocket endpoint: ws://localhost:8000/ws/pokemon-game/{session_id}');
console.log('🔧 Make sure to run: python backend/main.py');