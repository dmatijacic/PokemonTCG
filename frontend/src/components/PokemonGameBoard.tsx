// frontend/src/components/PokemonGameBoard.tsx
import React, { useState } from 'react';
import { 
  Grid, 
  Section, 
  LessonBox 
} from './ui';
import {
  PokemonCardDisplay,
  AIThoughtBubble,
  PlayerBoard,
  GameControls,
  TypeEffectivenessChart,
  BattleLog
} from './pokemon';

// Types
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

const PokemonGameBoard: React.FC = () => {
  // Initialize game state
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
    '🔥 Charmander vs 💧 Squirtle - Type matchup analysis loading...',
    '🤖 AI is ready to demonstrate strategic thinking!'
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
        // Analyze type advantage
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-purple-50 to-green-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Game Header */}
        <Section variant="game" className="text-center py-6">
          <h1 className="text-4xl font-bold text-purple-800 mb-2">
            🎮 Pokemon TCG AI Education Battle
          </h1>
          <p className="text-lg text-purple-700">
            Learn how AI thinks through Pokemon strategy!
          </p>
        </Section>

        {/* Main Game Board */}
        <Grid cols={3} gap="lg">
          
          {/* AI Player Side */}
          <PlayerBoard 
            player={gameState.aiPlayer}
            isAI={true}
          />

          {/* Center - AI Controls & Information */}
          <div className="space-y-4">
            <AIThoughtBubble 
              aiThought={aiThought}
            />
            
            <GameControls
              onSimulateAI={simulateAITurn}
              aiThinking={aiThought.thinking}
              currentTurn={gameState.currentTurn}
            />

            <TypeEffectivenessChart />
          </div>

          {/* Child Player Side */}
          <PlayerBoard 
            player={gameState.childPlayer}
            isAI={false}
          />
          
        </Grid>

        {/* Game Log */}
        <BattleLog gameLog={gameLog} />

        {/* Educational Footer */}
        <Section variant="default" className="text-center">
          <LessonBox type="tip" icon="🧠">
            <div>
              <strong>Watch how the AI analyzes Pokemon type advantages and makes strategic decisions!</strong>
            </div>
            <div className="mt-2 text-xs">
              This teaches pattern recognition, strategic thinking, and AI decision-making concepts.
            </div>
          </LessonBox>
        </Section>
        
      </div>
    </div>
  );
};

export default PokemonGameBoard;