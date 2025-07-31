// frontend/src/components/pokemon/index.tsx
// Pokemon-specific reusable components

import React from 'react';
import { Card, TypeBadge, Button, ProgressBar } from '../ui';

// ===========================================
// POKEMON CARD COMPONENTS
// ===========================================

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

export const PokemonCardDisplay: React.FC<{
  pokemon: PokemonCard | null;
  variant?: 'active' | 'bench' | 'hand';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  showStats?: boolean;
  isAI?: boolean;
}> = ({ 
  pokemon, 
  variant = 'bench', 
  size = 'md', 
  onClick, 
  showStats = true,
  isAI = false 
}) => {
  if (!pokemon) {
    return (
      <Card 
        className={`${getSizeClasses(size)} border-dashed flex items-center justify-center`}
        hover={false}
      >
        <span className="text-gray-500 text-sm">No Pokemon</span>
      </Card>
    );
  }

  const isActive = variant === 'active';
  const cardVariant = isAI ? 'ai' : 'child';

  return (
    <Card
      variant={cardVariant}
      hover={!!onClick}
      active={isActive}
      className={`${getSizeClasses(size)} p-3 ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
    >
      <div className="text-center space-y-2">
        {/* Pokemon Name */}
        <h4 className={`font-bold truncate ${getTextSizeClasses(size)}`}>
          {pokemon.name}
        </h4>
        
        {/* HP */}
        {showStats && (
          <div className="text-sm text-gray-600">
            HP: {pokemon.hp}
          </div>
        )}
        
        {/* Types */}
        <div className="flex justify-center gap-1 flex-wrap">
          {pokemon.types.map(type => (
            <TypeBadge key={type} type={type} size={size === 'lg' ? 'md' : 'sm'} />
          ))}
        </div>
        
        {/* Attacks (for larger cards) */}
        {size !== 'sm' && showStats && (
          <div className="space-y-1">
            {pokemon.attacks.slice(0, 2).map((attack, index) => (
              <div key={index} className="text-xs">
                <div className="font-medium">{attack.name}</div>
                <div className="text-gray-500">{attack.damage} damage</div>
              </div>
            ))}
          </div>
        )}
        
        {/* Active Pokemon indicator */}
        {isActive && (
          <div className="text-xs font-bold text-yellow-700 bg-yellow-200 rounded px-2 py-1">
            ACTIVE
          </div>
        )}
      </div>
    </Card>
  );
};

const getSizeClasses = (size: 'sm' | 'md' | 'lg'): string => {
  const sizeClasses = {
    sm: 'w-20 h-28',
    md: 'w-32 h-44',
    lg: 'w-40 h-56'
  };
  return sizeClasses[size];
};

const getTextSizeClasses = (size: 'sm' | 'md' | 'lg'): string => {
  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };
  return textSizes[size];
};

// ===========================================
// AI COMPONENTS
// ===========================================

interface AIThought {
  thinking: boolean;
  message: string;
  explanation: string;
  typeLesson?: string;
  strategicInsight?: string;
}

export const AIThoughtBubble: React.FC<{
  aiThought: AIThought;
  className?: string;
}> = ({ aiThought, className = '' }) => {
  return (
    <Card variant="ai" className={`p-4 relative ${className}`}>
      {/* Thought bubble pointer */}
      <div className="absolute -top-2 left-6 w-0 h-0 border-l-8 border-r-8 border-b-8 border-l-transparent border-r-transparent border-b-blue-300" />
      
      <div className="space-y-3">
        <h3 className="font-bold text-blue-800 flex items-center gap-2">
          🤖 AI Thinking Process
        </h3>
        
        {aiThought.thinking ? (
          <AIThinkingAnimation message={aiThought.message} />
        ) : (
          <AIDecisionExplanation aiThought={aiThought} />
        )}
      </div>
    </Card>
  );
};

const AIThinkingAnimation: React.FC<{ message: string }> = ({ message }) => (
  <div className="flex items-center gap-3">
    <div className="flex space-x-1">
      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
      <div 
        className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" 
        style={{ animationDelay: '0.1s' }} 
      />
      <div 
        className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" 
        style={{ animationDelay: '0.2s' }} 
      />
    </div>
    <span className="text-blue-700">{message}</span>
  </div>
);

const AIDecisionExplanation: React.FC<{ aiThought: AIThought }> = ({ aiThought }) => (
  <div className="space-y-3">
    <div className="text-blue-800 font-medium">{aiThought.message}</div>
    
    {aiThought.explanation && (
      <div className="text-blue-700 text-sm">{aiThought.explanation}</div>
    )}
    
    {aiThought.typeLesson && (
      <div className="bg-green-100 border border-green-300 rounded-lg p-3 text-green-800 text-sm">
        <div className="font-medium mb-1">🎓 AI Lesson:</div>
        {aiThought.typeLesson}
      </div>
    )}
    
    {aiThought.strategicInsight && (
      <div className="bg-purple-100 border border-purple-300 rounded-lg p-3 text-purple-800 text-sm">
        <div className="font-medium mb-1">🎯 Strategic Insight:</div>
        {aiThought.strategicInsight}
      </div>
    )}
  </div>
);

// ===========================================
// GAME BOARD COMPONENTS
// ===========================================

interface Player {
  name: string;
  activePokemon: PokemonCard | null;
  benchedPokemon: PokemonCard[];
  hand: PokemonCard[];
  prizeCards: number;
}

export const PlayerBoard: React.FC<{
  player: Player;
  isAI?: boolean;
  onPokemonClick?: (pokemon: PokemonCard) => void;
}> = ({ player, isAI = false, onPokemonClick }) => {
  const boardVariant = isAI ? 'ai' : 'child';
  const titleColor = isAI ? 'text-blue-800' : 'text-red-800';
  const playerIcon = isAI ? '🤖' : '👤';

  return (
    <Card variant={boardVariant} className="p-4">
      <h2 className={`text-xl font-bold mb-4 ${titleColor}`}>
        {playerIcon} {player.name}
      </h2>
      
      {/* Active Pokemon */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Active Pokemon:</h3>
        <PokemonCardDisplay
          pokemon={player.activePokemon}
          variant="active"
          isAI={isAI}
          onClick={onPokemonClick ? () => player.activePokemon && onPokemonClick(player.activePokemon) : undefined}
        />
      </div>
      
      {/* Bench */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Bench ({player.benchedPokemon.length}):</h3>
        <div className="flex gap-2 flex-wrap">
          {player.benchedPokemon.map((pokemon, index) => (
            <PokemonCardDisplay
              key={index}
              pokemon={pokemon}
              variant="bench"
              size="sm"
              isAI={isAI}
              onClick={onPokemonClick ? () => onPokemonClick(pokemon) : undefined}
            />
          ))}
        </div>
      </div>
      
      {/* Hand (for child player) */}
      {!isAI && player.hand.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold mb-2">Hand ({player.hand.length}):</h3>
          <div className="flex gap-2 flex-wrap">
            {player.hand.map((pokemon, index) => (
              <PokemonCardDisplay
                key={index}
                pokemon={pokemon}
                variant="hand"
                size="sm"
                onClick={onPokemonClick ? () => onPokemonClick(pokemon) : undefined}
              />
            ))}
          </div>
        </div>
      )}
      
      {/* Player Stats */}
      <div className="space-y-2">
        <ProgressBar
          value={6 - player.prizeCards}
          max={6}
          label="Prize Cards Taken"
          color={isAI ? 'blue' : 'red'}
        />
        {!isAI && (
          <div className="text-sm text-gray-600">
            Cards in hand: {player.hand.length}
          </div>
        )}
      </div>
    </Card>
  );
};

// ===========================================
// GAME CONTROLS
// ===========================================

export const GameControls: React.FC<{
  onSimulateAI: () => void;
  aiThinking: boolean;
  currentTurn: 'child' | 'ai';
}> = ({ onSimulateAI, aiThinking, currentTurn }) => {
  return (
    <Card variant="game" className="p-4">
      <h3 className="font-bold mb-3 text-purple-800">🎮 Game Controls</h3>
      
      <div className="space-y-3">
        <Button
          variant="ai"
          onClick={onSimulateAI}
          disabled={aiThinking}
          loading={aiThinking}
          className="w-full"
        >
          {aiThinking ? 'AI Thinking...' : '🤖 Simulate AI Turn'}
        </Button>
        
        <div className="text-center text-sm text-gray-600">
          Current Turn:
          <span className="font-semibold ml-1">
            {currentTurn === 'child' ? '👤 Your Turn' : '🤖 AI Turn'}
          </span>
        </div>
      </div>
    </Card>
  );
};

// ===========================================
// TYPE EFFECTIVENESS REFERENCE
// ===========================================

export const TypeEffectivenessChart: React.FC = () => {
  const effectiveness = [
    {
      attacking: 'Fire',
      defending: 'Grass',
      result: 'Super Effective (2x)',
      icon: '🔥→🌱'
    },
    {
      attacking: 'Water',
      defending: 'Fire',
      result: 'Super Effective (2x)',
      icon: '💧→🔥'
    },
    {
      attacking: 'Grass',
      defending: 'Water',
      result: 'Super Effective (2x)',
      icon: '🌱→💧'
    },
    {
      attacking: 'Electric',
      defending: 'Water',
      result: 'Super Effective (2x)',
      icon: '⚡→💧'
    }
  ];

  return (
    <Card variant="default" className="p-4">
      <h3 className="font-bold mb-3 text-gray-800">⚡ Type Effectiveness</h3>
      <div className="space-y-2">
        {effectiveness.map((item, index) => (
          <div key={index} className="text-xs flex items-center justify-between">
            <span className="font-mono">{item.icon}</span>
            <span className="text-green-700">{item.result}</span>
          </div>
        ))}
      </div>
    </Card>
  );
};

// ===========================================
// BATTLE LOG
// ===========================================

export const BattleLog: React.FC<{
  gameLog: string[];
  className?: string;
}> = ({ gameLog, className = '' }) => {
  return (
    <Card variant="default" className={`p-4 ${className}`}>
      <h3 className="font-bold mb-3 text-gray-800">📜 Battle Log</h3>
      <div className="h-32 overflow-y-auto space-y-1 battle-log">
        {gameLog.map((log, index) => (
          <div key={index} className="text-sm text-gray-800 leading-relaxed">
            {log}
          </div>
        ))}
      </div>
    </Card>
  );
};