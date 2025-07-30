import React, { useState, useEffect } from 'react';

// Pokemon game state types
interface PokemonCard {
  id: string;
  name: string;
  hp: number;
  types: string[];
  attacks: Attack[];
  image?: string;
}

interface Attack {
  name: string;
  damage: number;
  cost: string[];
  effect?: string;
}

interface Player {
  name: string;
  activePokemon: PokemonCard | null;
  benchedPokemon: PokemonCard[];
  hand: PokemonCard[];
  prizeCards: number;
}

interface GameState {
  currentTurn: 'child' | 'ai';
  gamePhase: 'setup' | 'playing' | 'finished';
  childPlayer: Player;
  aiPlayer: Player;
  winner: string | null;
}

interface AIThought {
  thinking: boolean;
  message: string;
  explanation: string;
  typeLesson?: string;
  strategicInsight?: string;
}

// Sample Pokemon data
const samplePokemon: PokemonCard[] = [
  {
    id: 'charmander-1',
    name: 'Charmander',
    hp: 50,
    types: ['Fire'],
    attacks: [
      { name: 'Scratch', damage: 10, cost: ['Colorless'] },
      { name: 'Ember', damage: 30, cost: ['Fire', 'Colorless'] }
    ]
  },
  {
    id: 'squirtle-1',
    name: 'Squirtle',
    hp: 50,
    types: ['Water'],
    attacks: [
      { name: 'Tackle', damage: 10, cost: ['Colorless'] },
      { name: 'Water Gun', damage: 30, cost: ['Water', 'Colorless'] }
    ]
  },
  {
    id: 'bulbasaur-1',
    name: 'Bulbasaur',
    hp: 50,
    types: ['Grass'],
    attacks: [
      { name: 'Tackle', damage: 10, cost: ['Colorless'] },
      { name: 'Vine Whip', damage: 30, cost: ['Grass', 'Colorless'] }
    ]
  },
  {
    id: 'pikachu-1',
    name: 'Pikachu',
    hp: 60,
    types: ['Electric'],
    attacks: [
      { name: 'Thunder Shock', damage: 20, cost: ['Electric'] },
      { name: 'Thunderbolt', damage: 40, cost: ['Electric', 'Electric'] }
    ]
  }
];

const PokemonGameBoard: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>({
    currentTurn: 'child',
    gamePhase: 'playing',
    childPlayer: {
      name: 'Ash',
      activePokemon: samplePokemon[0], // Charmander
      benchedPokemon: [samplePokemon[2]], // Bulbasaur
      hand: [samplePokemon[3]], // Pikachu
      prizeCards: 6
    },
    aiPlayer: {
      name: 'Pokemon AI',
      activePokemon: samplePokemon[1], // Squirtle
      benchedPokemon: [samplePokemon[3]], // Pikachu
      hand: [],
      prizeCards: 6
    },
    winner: null
  });

  const [aiThought, setAiThought] = useState<AIThought>({
    thinking: false,
    message: '',
    explanation: '',
    typeLesson: '',
    strategicInsight: ''
  });

  const [gameLog, setGameLog] = useState<string[]>([
    '🎮 Pokemon TCG AI Education Battle Started!',
    '🔥 Charmander vs 💧 Squirtle - Type matchup analysis loading...'
  ]);

  // Simulate AI thinking and decision making
  const simulateAITurn = () => {
    setAiThought({
      thinking: true,
      message: '🤖 AI is analyzing the battlefield...',
      explanation: '',
      typeLesson: '',
      strategicInsight: ''
    });

    // Simulate AI analysis delay
    setTimeout(() => {
      const childPokemon = gameState.childPlayer.activePokemon;
      const aiPokemon = gameState.aiPlayer.activePokemon;
      
      if (childPokemon && aiPokemon) {
        // Simulate type advantage analysis
        const typeAdvantage = getTypeAdvantage(aiPokemon.types[0], childPokemon.types[0]);
        
        let aiDecision = '';
        let explanation = '';
        let typeLesson = '';
        let strategicInsight = '';
        
        if (typeAdvantage === 'super_effective') {
          aiDecision = `Perfect! My ${aiPokemon.name} has type advantage!`;
          explanation = `🧠 My AI remembered that ${aiPokemon.types[0]} beats ${childPokemon.types[0]}!`;
          typeLesson = `🎓 AI Lesson: ${aiPokemon.types[0]} attacks do 2x damage to ${childPokemon.types[0]} Pokemon!`;
          strategicInsight = '🎯 My AI chooses to attack when it has type advantage!';
        } else if (typeAdvantage === 'not_very_effective') {
          aiDecision = `My AI detects type disadvantage. Time to think strategically!`;
          explanation = `🧠 My AI calculated that ${aiPokemon.types[0]} is weak against ${childPokemon.types[0]}`;
          typeLesson = `🎓 AI Lesson: When at disadvantage, consider switching Pokemon!`;
          strategicInsight = '🎯 Strategic AI: Sometimes retreating is the smart move!';
        } else {
          aiDecision = `Neutral matchup. My AI will focus on damage output!`;
          explanation = `🧠 My AI sees equal type matchup, so I'll use my strongest attack!`;
          typeLesson = `🎓 AI Lesson: When types are neutral, Pokemon stats matter most!`;
          strategicInsight = '🎯 AI Strategy: Maximize damage when no type advantage exists!';
        }

        setAiThought({
          thinking: false,
          message: aiDecision,
          explanation: explanation,
          typeLesson: typeLesson,
          strategicInsight: strategicInsight
        });

        // Add to game log
        setGameLog(prev => [...prev, 
          `🤖 AI Turn: ${aiDecision}`,
          `   ${explanation}`,
          `   ${typeLesson}`
        ]);
      }
    }, 2000);
  };

  // Get type advantage
  const getTypeAdvantage = (attackingType: string, defendingType: string): string => {
    const typeChart: Record<string, string[]> = {
      'Fire': ['Grass'],
      'Water': ['Fire'],
      'Grass': ['Water'],
      'Electric': ['Water']
    };

    if (typeChart[attackingType]?.includes(defendingType)) {
      return 'super_effective';
    }
    
    if (typeChart[defendingType]?.includes(attackingType)) {
      return 'not_very_effective';
    }
    
    return 'neutral';
  };

  // Get type color
  const getTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      'Fire': 'bg-red-500',
      'Water': 'bg-blue-500',
      'Grass': 'bg-green-500',
      'Electric': 'bg-yellow-500',
      'Normal': 'bg-gray-500'
    };
    return colors[type] || 'bg-gray-500';
  };

  // Pokemon Card Component
  const PokemonCardDisplay: React.FC<{ 
    pokemon: PokemonCard | null; 
    isActive?: boolean; 
    isAI?: boolean;
    onClick?: () => void;
  }> = ({ pokemon, isActive = false, isAI = false, onClick }) => {
    if (!pokemon) {
      return (
        <div className="w-32 h-44 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
          <span className="text-gray-500 text-sm">No Pokemon</span>
        </div>
      );
    }

    return (
      <div 
        className={`w-32 h-44 border-2 rounded-lg p-2 cursor-pointer transition-all
          ${isActive ? 'border-yellow-500 bg-yellow-50' : 'border-gray-300 bg-white'}
          ${isAI ? 'bg-blue-50' : 'bg-red-50'}
          hover:shadow-lg`}
        onClick={onClick}
      >
        <div className="text-center">
          <h3 className="font-bold text-sm truncate">{pokemon.name}</h3>
          <div className="text-xs text-gray-600">HP: {pokemon.hp}</div>
          
          {/* Pokemon Types */}
          <div className="flex justify-center gap-1 mt-1">
            {pokemon.types.map(type => (
              <span 
                key={type}
                className={`px-2 py-1 rounded text-xs text-white ${getTypeColor(type)}`}
              >
                {type}
              </span>
            ))}
          </div>
          
          {/* Attacks */}
          <div className="mt-2 space-y-1">
            {pokemon.attacks.slice(0, 2).map(attack => (
              <div key={attack.name} className="text-xs">
                <div className="font-medium">{attack.name}</div>
                <div className="text-gray-500">{attack.damage} damage</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // AI Thought Bubble Component
  const AIThoughtBubble: React.FC = () => {
    return (
      <div className="bg-blue-100 border-2 border-blue-300 rounded-lg p-4 relative">
        <div className="absolute -top-2 left-6 w-0 h-0 border-l-8 border-r-8 border-b-8 border-l-transparent border-r-transparent border-b-blue-300"></div>
        
        <h3 className="font-bold text-blue-800 mb-2">🤖 AI Thinking Process</h3>
        
        {aiThought.thinking ? (
          <div className="flex items-center gap-2">
            <div className="animate-spin h-4 w-4 border-2 border-blue-600 rounded-full border-t-transparent"></div>
            <span className="text-blue-700">{aiThought.message}</span>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-blue-800 font-medium">{aiThought.message}</div>
            {aiThought.explanation && (
              <div className="text-blue-700 text-sm">{aiThought.explanation}</div>
            )}
            {aiThought.typeLesson && (
              <div className="bg-green-100 border border-green-300 rounded p-2 text-green-800 text-sm">
                {aiThought.typeLesson}
              </div>
            )}
            {aiThought.strategicInsight && (
              <div className="bg-purple-100 border border-purple-300 rounded p-2 text-purple-800 text-sm">
                {aiThought.strategicInsight}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-200 to-green-200 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Game Header */}
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🎮 Pokemon TCG AI Education Battle
          </h1>
          <div className="text-lg text-gray-700">
            Learn how AI thinks through Pokemon strategy!
          </div>
        </div>

        {/* Game Board */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* AI Player Side */}
          <div className="bg-blue-50 rounded-lg p-4 border-2 border-blue-300">
            <h2 className="text-xl font-bold text-blue-800 mb-4">🤖 AI Player</h2>
            
            {/* AI Active Pokemon */}
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Active Pokemon:</h3>
              <PokemonCardDisplay 
                pokemon={gameState.aiPlayer.activePokemon} 
                isActive={true}
                isAI={true}
              />
            </div>
            
            {/* AI Bench */}
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Bench ({gameState.aiPlayer.benchedPokemon.length}):</h3>
              <div className="flex gap-2">
                {gameState.aiPlayer.benchedPokemon.map((pokemon, index) => (
                  <PokemonCardDisplay 
                    key={index} 
                    pokemon={pokemon} 
                    isAI={true}
                  />
                ))}
              </div>
            </div>
            
            {/* AI Stats */}
            <div className="text-sm text-blue-700">
              <div>Prize Cards: {gameState.aiPlayer.prizeCards}</div>
              <div>Hand: {gameState.aiPlayer.hand.length} cards</div>
            </div>
          </div>

          {/* Center - AI Thought Bubble & Controls */}
          <div className="space-y-4">
            <AIThoughtBubble />
            
            {/* Game Controls */}
            <div className="bg-white rounded-lg p-4 border-2 border-gray-300">
              <h3 className="font-bold mb-3">🎮 Game Controls</h3>
              
              <div className="space-y-2">
                <button 
                  onClick={simulateAITurn}
                  className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition-colors"
                  disabled={aiThought.thinking}
                >
                  {aiThought.thinking ? 'AI Thinking...' : '🤖 Simulate AI Turn'}
                </button>
                
                <div className="text-center text-sm text-gray-600">
                  Current Turn: <span className="font-semibold">
                    {gameState.currentTurn === 'child' ? '👤 Your Turn' : '🤖 AI Turn'}
                  </span>
                </div>
              </div>
            </div>

            {/* Type Effectiveness Chart */}
            <div className="bg-white rounded-lg p-4 border-2 border-gray-300">
              <h3 className="font-bold mb-3">⚡ Type Effectiveness</h3>
              <div className="text-xs space-y-1">
                <div>🔥 Fire → 🌱 Grass: Super Effective (2x)</div>
                <div>💧 Water → 🔥 Fire: Super Effective (2x)</div>
                <div>🌱 Grass → 💧 Water: Super Effective (2x)</div>
                <div>⚡ Electric → 💧 Water: Super Effective (2x)</div>
              </div>
            </div>
          </div>

          {/* Child Player Side */}
          <div className="bg-red-50 rounded-lg p-4 border-2 border-red-300">
            <h2 className="text-xl font-bold text-red-800 mb-4">👤 {gameState.childPlayer.name}</h2>
            
            {/* Child Active Pokemon */}
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Active Pokemon:</h3>
              <PokemonCardDisplay 
                pokemon={gameState.childPlayer.activePokemon} 
                isActive={true}
              />
            </div>
            
            {/* Child Bench */}
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Bench ({gameState.childPlayer.benchedPokemon.length}):</h3>
              <div className="flex gap-2">
                {gameState.childPlayer.benchedPokemon.map((pokemon, index) => (
                  <PokemonCardDisplay 
                    key={index} 
                    pokemon={pokemon}
                  />
                ))}
              </div>
            </div>
            
            {/* Child Hand */}
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Hand ({gameState.childPlayer.hand.length}):</h3>
              <div className="flex gap-2">
                {gameState.childPlayer.hand.map((pokemon, index) => (
                  <PokemonCardDisplay 
                    key={index} 
                    pokemon={pokemon}
                  />
                ))}
              </div>
            </div>
            
            {/* Child Stats */}
            <div className="text-sm text-red-700">
              <div>Prize Cards: {gameState.childPlayer.prizeCards}</div>
            </div>
          </div>
        </div>

        {/* Game Log */}
        <div className="mt-6 bg-gray-100 rounded-lg p-4 border-2 border-gray-300">
          <h3 className="font-bold mb-3">📜 Battle Log</h3>
          <div className="h-32 overflow-y-auto space-y-1">
            {gameLog.map((log, index) => (
              <div key={index} className="text-sm text-gray-800">
                {log}
              </div>
            ))}
          </div>
        </div>

        {/* Educational Footer */}
        <div className="mt-6 text-center text-gray-700">
          <p className="text-sm">
            🧠 Watch how the AI analyzes Pokemon type advantages and makes strategic decisions!
          </p>
          <p className="text-xs mt-1">
            This teaches pattern recognition, strategic thinking, and AI decision-making concepts.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PokemonGameBoard;