import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import PokemonGameBoard from './components/PokemonGameBoard';

console.log('🎮 Starting Pokemon TCG AI Education Platform...');

const container = document.getElementById('app');
if (container) {
  const root = createRoot(container);
  root.render(React.createElement(PokemonGameBoard));
  console.log('✅ Pokemon game loaded successfully!');
} else {
  console.error('❌ Could not find app container element');
}
