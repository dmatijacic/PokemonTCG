// frontend/src/components/PokemonGameBoard.tsx
import React, { useState } from 'react';
import { Card, Button, Grid, Section, LessonBox, TypeBadge, ProgressBar } from './ui';

// TypeScript Interfaces
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
  turnNumber: number;
}

interface AIThought {
  thinking: boolean;
  message: string;
  explanation: string;
  typeLesson?: string;
  strategicInsight?: string;
}

interface PlayerAction {
  id: string;
  name: string;
  icon: string;
  disabled: boolean;
}

interface TypeAdvantage {
  beats?: string[];
  weak?: string[];
  immune?: string[];
}

interface TypeAdvantages {
  [key: string]: TypeAdvantage;
}

interface Filter {
  id: string;
  name: string;
  icon: string;
}

// Props interfaces
interface EnhancedGameControlsProps {
  onSimulateAI: () => void;
  aiThinking: boolean;
  currentTurn: 'child' | 'ai';
  gameState: GameState;
  onPlayerAction?: (actionId: string, pokemon?: any) => void;
  onEndTurn: () => void;
  onResetGame: () => void;
}

interface EnhancedBattleLogProps {
  gameLog: string[];
  className?: string;
}

// Enhanced Game Controls Component
const EnhancedGameControls: React.FC<EnhancedGameControlsProps> = ({ 
  onSimulateAI, 
  aiThinking, 
  currentTurn, 
  gameState,
  onPlayerAction,
  onEndTurn,
  onResetGame 
}) => {
  const [selectedAction, setSelectedAction] = useState<string | null>(null);
  const [selectedPokemon, setSelectedPokemon] = useState<PokemonCard | null>(null);
  const [showHandSelection, setShowHandSelection] = useState<boolean>(false);
  const [showBenchSelection, setShowBenchSelection] = useState<boolean>(false);
  const [showAttackSelection, setShowAttackSelection] = useState<boolean>(false);

  const playerActions: PlayerAction[] = [
    { id: 'draw_card', name: 'Draw Card', icon: '🃏', disabled: false },
    { id: 'play_pokemon', name: 'Play Pokemon', icon: '🎴', disabled: gameState?.childPlayer?.hand.length === 0 },
    { id: 'attach_energy', name: 'Attach Energy', icon: '⚡', disabled: false },
    { id: 'attack', name: 'Attack', icon: '⚔️', disabled: currentTurn !== 'child' || !gameState?.childPlayer?.activePokemon },
    { id: 'retreat', name: 'Retreat', icon: '🔄', disabled: !gameState?.childPlayer?.activePokemon || gameState?.childPlayer?.benchedPokemon.length === 0 },
    { id: 'use_trainer', name: 'Use Trainer', icon: '🎓', disabled: false }
  ];

  const handlePlayerAction = (actionId: string): void => {
    setSelectedAction(actionId);
    
    if (actionId === 'play_pokemon') {
      setShowHandSelection(true);
      setShowBenchSelection(false);
      setShowAttackSelection(false);
    } else if (actionId === 'retreat') {
      setShowBenchSelection(true);
      setShowHandSelection(false);
      setShowAttackSelection(false);
    } else if (actionId === 'attack') {
      setShowAttackSelection(true);
      setShowHandSelection(false);
      setShowBenchSelection(false);
    } else {
      setShowHandSelection(false);
      setShowBenchSelection(false);
      setShowAttackSelection(false);
      if (onPlayerAction) {
        onPlayerAction(actionId, selectedPokemon);
      }
    }
  };

  const handlePlayPokemon = (pokemon: PokemonCard): void => {
    setSelectedPokemon(pokemon);
    setShowHandSelection(false);
    setSelectedAction(null);
    if (onPlayerAction) {
      onPlayerAction('play_pokemon', pokemon);
    }
  };

  const handleRetreat = (pokemon: PokemonCard): void => {
    setSelectedPokemon(pokemon);
    setShowBenchSelection(false);
    setSelectedAction(null);
    if (onPlayerAction) {
      onPlayerAction('retreat', pokemon);
    }
  };

  const handleAttack = (attack: Attack): void => {
    setShowAttackSelection(false);
    setSelectedAction(null);
    if (onPlayerAction) {
      onPlayerAction('attack', attack);
    }
  };

  const cancelSelection = (): void => {
    setShowHandSelection(false);
    setShowBenchSelection(false);
    setShowAttackSelection(false);
    setSelectedAction(null);
  };

  return (
    <div className="space-y-4">
      {/* AI Control Section */}
      <Card variant="ai" className="p-4">
        <h3 className="font-bold mb-3 text-blue-800 flex items-center gap-2">
          🤖 AI Controls
        </h3>
        
        <div className="space-y-3">
          <Button
            variant="ai"
            onClick={onSimulateAI}
            disabled={aiThinking || currentTurn !== 'ai'}
            loading={aiThinking}
            className="w-full"
          >
            {aiThinking ? 'AI Analyzing...' : '🧠 Simulate AI Turn'}
          </Button>
          
          <div className="text-xs text-blue-600 bg-blue-50 p-2 rounded">
            {aiThinking ? (
              <div className="flex items-center gap-2">
                <div className="ai-thinking-dots">
                  <div></div>
                  <div></div>
                  <div></div>
                </div>
                <span>AI is thinking strategically...</span>
              </div>
            ) : (
              'Click to see how AI analyzes Pokemon matchups!'
            )}
          </div>
        </div>
      </Card>

      {/* Player Action Section */}
      <Card variant="child" className="p-4">
        <h3 className="font-bold mb-3 text-red-800 flex items-center gap-2">
          👤 Your Actions
        </h3>
        
        <Grid cols={2} gap="sm" className="mb-3">
          {playerActions.map((action) => (
            <Button
              key={action.id}
              variant={selectedAction === action.id ? 'pokemon' : 'secondary'}
              size="sm"
              disabled={action.disabled || currentTurn !== 'child'}
              onClick={() => handlePlayerAction(action.id)}
              className="text-xs"
            >
              <span className="mr-1">{action.icon}</span>
              {action.name}
            </Button>
          ))}
        </Grid>

        {/* Hand Selection for Playing Pokemon */}
        {showHandSelection && gameState?.childPlayer?.hand && (
          <div className="mb-3 p-3 bg-yellow-50 border border-yellow-300 rounded-lg">
            <h4 className="font-semibold text-sm mb-2">🎴 Choose a Pokemon to play:</h4>
            <div className="flex gap-2 flex-wrap">
              {gameState.childPlayer.hand.map((pokemon, index) => (
                <button
                  key={`hand-select-${pokemon.id}-${index}`}
                  onClick={() => handlePlayPokemon(pokemon)}
                  className="p-2 bg-white border border-gray-300 rounded hover:bg-blue-50 hover:border-blue-400 transition-colors"
                >
                  <div className="text-xs text-center">
                    <div className="font-semibold">{pokemon.name}</div>
                    <div className="text-gray-600">HP: {pokemon.hp}</div>
                    <div className="flex justify-center gap-1 mt-1">
                      {pokemon.types.map(type => (
                        <TypeBadge key={type} type={type} size="sm" />
                      ))}
                    </div>
                  </div>
                </button>
              ))}
            </div>
            <Button variant="secondary" size="sm" onClick={cancelSelection} className="mt-2 text-xs">
              Cancel
            </Button>
          </div>
        )}

        {/* Bench Selection for Retreat */}
        {showBenchSelection && gameState?.childPlayer?.benchedPokemon && (
          <div className="mb-3 p-3 bg-blue-50 border border-blue-300 rounded-lg">
            <h4 className="font-semibold text-sm mb-2">🔄 Choose a Pokemon to switch in:</h4>
            <div className="flex gap-2 flex-wrap">
              {gameState.childPlayer.benchedPokemon.map((pokemon, index) => (
                <button
                  key={`bench-select-${pokemon.id}-${index}`}
                  onClick={() => handleRetreat(pokemon)}
                  className="p-2 bg-white border border-gray-300 rounded hover:bg-green-50 hover:border-green-400 transition-colors"
                >
                  <div className="text-xs text-center">
                    <div className="font-semibold">{pokemon.name}</div>
                    <div className="text-gray-600">HP: {pokemon.hp}</div>
                    <div className="flex justify-center gap-1 mt-1">
                      {pokemon.types.map(type => (
                        <TypeBadge key={type} type={type} size="sm" />
                      ))}
                    </div>
                  </div>
                </button>
              ))}
            </div>
            <Button variant="secondary" size="sm" onClick={cancelSelection} className="mt-2 text-xs">
              Cancel
            </Button>
          </div>
        )}

        {/* Attack Selection */}
        {showAttackSelection && gameState?.childPlayer?.activePokemon?.attacks && (
          <div className="mb-3 p-3 bg-red-50 border border-red-300 rounded-lg">
            <h4 className="font-semibold text-sm mb-2">⚔️ Choose an attack:</h4>
            <div className="space-y-2">
              {gameState.childPlayer.activePokemon.attacks.map((attack, index) => (
                <button
                  key={`attack-${index}`}
                  onClick={() => handleAttack(attack)}
                  className="w-full p-2 bg-white border border-gray-300 rounded hover:bg-red-50 hover:border-red-400 transition-colors text-left"
                >
                  <div className="text-sm">
                    <div className="font-semibold">{attack.name}</div>
                    <div className="text-gray-600">
                      Damage: {attack.damage} | Cost: {attack.cost.join(', ')}
                    </div>
                    {attack.effect && (
                      <div className="text-xs text-gray-500 mt-1">{attack.effect}</div>
                    )}
                  </div>
                </button>
              ))}
            </div>
            <Button variant="secondary" size="sm" onClick={cancelSelection} className="mt-2 text-xs">
              Cancel
            </Button>
          </div>
        )}

        {selectedAction && !showHandSelection && !showBenchSelection && !showAttackSelection && (
          <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
            Selected: {playerActions.find(a => a.id === selectedAction)?.name}
            {selectedAction === 'draw_card' && ' - Draw a card from your deck!'}
            {selectedAction === 'attack' && ' - Choose your Pokemon\'s attack!'}
            {selectedAction === 'retreat' && ' - Switch to a benched Pokemon!'}
            {selectedAction === 'play_pokemon' && ' - Play a Pokemon from your hand!'}
            {selectedAction === 'attach_energy' && ' - Attach energy to power up attacks!'}
            {selectedAction === 'use_trainer' && ' - Use a trainer card for special effects!'}
          </div>
        )}
      </Card>

      {/* Game Flow Controls */}
      <Card variant="game" className="p-4">
        <h3 className="font-bold mb-3 text-purple-800">🎮 Game Flow</h3>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Current Turn:</span>
            <span className={`font-semibold ${currentTurn === 'child' ? 'text-red-600' : 'text-blue-600'}`}>
              {currentTurn === 'child' ? '👤 Your Turn' : '🤖 AI Turn'}
            </span>
          </div>
          
          <ProgressBar
            value={gameState?.turnNumber || 1}
            max={20}
            label="Turn Progress"
            color={currentTurn === 'child' ? 'red' : 'blue'}
          />
          
          <div className="flex gap-2 pt-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={onEndTurn}
              disabled={currentTurn !== 'child'}
              className="flex-1"
            >
              End Turn
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={onResetGame}
              className="flex-1"
            >
              New Game
            </Button>
          </div>
        </div>
      </Card>

      {/* Educational Tips */}
      <LessonBox type="tip" icon="🎓">
        <div className="text-xs">
          <strong>Learning Tip:</strong> Watch how the AI considers type advantages, energy costs, 
          and strategic positioning when making decisions. Each AI move teaches you about 
          artificial intelligence thinking patterns!
        </div>
      </LessonBox>
    </div>
  );
};

// Enhanced Type Effectiveness Reference
const EnhancedTypeChart: React.FC = () => {
  const [selectedType, setSelectedType] = useState<string | null>(null);
  
  const typeAdvantages: TypeAdvantages = {
    fire: { beats: ['grass', 'bug', 'steel', 'ice'], weak: ['water', 'ground', 'rock'] },
    water: { beats: ['fire', 'ground', 'rock'], weak: ['grass', 'electric'] },
    grass: { beats: ['water', 'ground', 'rock'], weak: ['fire', 'ice', 'poison', 'flying', 'bug'] },
    electric: { beats: ['water', 'flying'], weak: ['ground'], immune: ['ground'] },
    psychic: { beats: ['fighting', 'poison'], weak: ['ghost', 'dark'] },
    fighting: { beats: ['normal', 'rock', 'steel', 'ice', 'dark'], weak: ['flying', 'psychic', 'fairy'] }
  };

  const typeColors: { [key: string]: string } = {
    fire: 'bg-red-500', 
    water: 'bg-blue-500', 
    grass: 'bg-green-500',
    electric: 'bg-yellow-500', 
    psychic: 'bg-purple-500', 
    fighting: 'bg-red-700'
  };

  return (
    <Card variant="default" className="p-4">
      <h3 className="font-bold mb-3 text-gray-800 flex items-center gap-2">
        ⚡ Type Effectiveness Guide
      </h3>
      
      <div className="space-y-3">
        {/* Type Selection */}
        <div className="flex flex-wrap gap-1">
          {Object.keys(typeAdvantages).map((type: string) => (
            <button
              key={type}
              onClick={() => setSelectedType(selectedType === type ? null : type)}
              className={`px-2 py-1 rounded text-xs font-medium transition-all ${
                typeColors[type] || 'bg-gray-400'
              } ${
                selectedType === type ? 'ring-2 ring-offset-1 ring-gray-400' : ''
              } text-white hover:opacity-80`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>

        {/* Type Details */}
        {selectedType && typeAdvantages[selectedType] && (
          <div className="bg-gray-50 p-3 rounded-lg text-xs">
            <div className="font-semibold mb-2 capitalize">{selectedType} Type:</div>
            
            {typeAdvantages[selectedType].beats && typeAdvantages[selectedType].beats!.length > 0 && (
              <div className="mb-2">
                <span className="text-green-700 font-medium">Super Effective vs: </span>
                <span className="text-green-600">
                  {typeAdvantages[selectedType].beats!.join(', ')}
                </span>
              </div>
            )}
            
            {typeAdvantages[selectedType].weak && typeAdvantages[selectedType].weak!.length > 0 && (
              <div className="mb-2">
                <span className="text-red-700 font-medium">Weak to: </span>
                <span className="text-red-600">
                  {typeAdvantages[selectedType].weak!.join(', ')}
                </span>
              </div>
            )}
            
            {typeAdvantages[selectedType].immune && typeAdvantages[selectedType].immune!.length > 0 && (
              <div>
                <span className="text-gray-700 font-medium">No effect on: </span>
                <span className="text-gray-600">
                  {typeAdvantages[selectedType].immune!.join(', ')}
                </span>
              </div>
            )}
          </div>
        )}

        {!selectedType && (
          <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
            💡 Click a type above to see its advantages and weaknesses!
          </div>
        )}
      </div>
    </Card>
  );
};

// Pokemon Card Display Component
const PokemonCardDisplay: React.FC<{
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
      className={`${getSizeClasses(size)} p-3 ${onClick ? 'cursor-pointer hover:shadow-lg' : ''} ${isActive ? 'ring-2 ring-yellow-400' : ''}`}
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
        {size !== 'sm' && showStats && pokemon.attacks.length > 0 && (
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

// Player Board Component
const PlayerBoard: React.FC<{
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
          size="lg"
          isAI={isAI}
          onClick={onPokemonClick ? () => player.activePokemon && onPokemonClick(player.activePokemon) : undefined}
        />
      </div>
      
      {/* Bench */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Bench ({player.benchedPokemon.length}/5):</h3>
        <div className="flex gap-2 flex-wrap">
          {player.benchedPokemon.map((pokemon, index) => (
            <PokemonCardDisplay
              key={`${pokemon.id}-${index}`}
              pokemon={pokemon}
              variant="bench"
              size="sm"
              isAI={isAI}
              onClick={onPokemonClick ? () => onPokemonClick(pokemon) : undefined}
            />
          ))}
          {/* Empty bench slots */}
          {Array.from({ length: 5 - player.benchedPokemon.length }).map((_, index) => (
            <PokemonCardDisplay
              key={`empty-${index}`}
              pokemon={null}
              variant="bench"
              size="sm"
              isAI={isAI}
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
                key={`hand-${pokemon.id}-${index}`}
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
        <div className="text-sm text-gray-600">
          Deck remaining: {isAI ? '??' : '45'} cards
        </div>
      </div>
    </Card>
  );
};

// Enhanced Battle Log with Filtering
const EnhancedBattleLog: React.FC<EnhancedBattleLogProps> = ({ gameLog, className = '' }) => {
  const [filter, setFilter] = useState<string>('all');
  
  const filters: Filter[] = [
    { id: 'all', name: 'All', icon: '📜' },
    { id: 'ai', name: 'AI Moves', icon: '🤖' },
    { id: 'player', name: 'Your Moves', icon: '👤' },
    { id: 'damage', name: 'Damage', icon: '⚔️' },
    { id: 'lesson', name: 'Lessons', icon: '🎓' }
  ];

  const filteredLog = gameLog.filter((entry: string) => {
    if (filter === 'all') return true;
    if (filter === 'ai') return entry.toLowerCase().includes('ai') || entry.includes('🤖');
    if (filter === 'player') return entry.toLowerCase().includes('you') || entry.includes('👤');
    if (filter === 'damage') return entry.toLowerCase().includes('damage') || entry.includes('⚔️');
    if (filter === 'lesson') return entry.includes('🎓') || entry.toLowerCase().includes('lesson');
    return true;
  });

  return (
    <Card variant="default" className={`p-4 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-bold text-gray-800">📜 Battle Log</h3>
        <div className="text-xs text-gray-600">
          {filteredLog.length} / {gameLog.length} entries
        </div>
      </div>
      
      {/* Filter Buttons */}
      <div className="flex flex-wrap gap-1 mb-3">
        {filters.map((f: Filter) => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              filter === f.id 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {f.icon} {f.name}
          </button>
        ))}
      </div>
      
      {/* Log Entries */}
      <div className="h-32 overflow-y-auto space-y-1 battle-log">
        {filteredLog.length > 0 ? (
          filteredLog.map((log: string, index: number) => (
            <div key={index} className="text-sm text-gray-800 leading-relaxed p-1 hover:bg-gray-50 rounded">
              {log}
            </div>
          ))
        ) : (
          <div className="text-xs text-gray-500 italic text-center py-4">
            No entries match the selected filter
          </div>
        )}
      </div>
    </Card>
  );
};

// Complete Game Interface Demo
const PokemonGameBoard: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>({
    currentTurn: 'child',
    gamePhase: 'playing',
    turnNumber: 1,
    childPlayer: { 
      name: 'Ash',
      activePokemon: { 
        id: 'charmander-1', 
        name: 'Charmander', 
        hp: 50, 
        types: ['Fire'], 
        attacks: [
          { name: 'Scratch', damage: 10, cost: ['Colorless'], effect: '' },
          { name: 'Ember', damage: 30, cost: ['Fire', 'Colorless'], effect: 'Flip a coin. If tails, discard 1 Fire Energy.' }
        ]
      },
      benchedPokemon: [
        { 
          id: 'bulbasaur-1', 
          name: 'Bulbasaur', 
          hp: 50, 
          types: ['Grass'], 
          attacks: [
            { name: 'Tackle', damage: 10, cost: ['Colorless'], effect: '' }
          ]
        }
      ],
      hand: [
        { 
          id: 'pikachu-1', 
          name: 'Pikachu', 
          hp: 60, 
          types: ['Electric'], 
          attacks: [
            { name: 'Thunder Shock', damage: 20, cost: ['Electric'], effect: 'Flip a coin. If heads, the Defending Pokemon is now Paralyzed.' }
          ]
        }
      ],
      prizeCards: 6
    },
    aiPlayer: { 
      name: 'Pokemon AI',
      activePokemon: { 
        id: 'squirtle-1', 
        name: 'Squirtle', 
        hp: 50, 
        types: ['Water'], 
        attacks: [
          { name: 'Tackle', damage: 10, cost: ['Colorless'], effect: '' },
          { name: 'Water Gun', damage: 30, cost: ['Water', 'Colorless'], effect: '' }
        ]
      },
      benchedPokemon: [
        { 
          id: 'geodude-1', 
          name: 'Geodude', 
          hp: 70, 
          types: ['Fighting'], 
          attacks: [
            { name: 'Rock Throw', damage: 20, cost: ['Fighting'], effect: '' }
          ]
        }
      ],
      hand: [], // AI hand is hidden
      prizeCards: 6
    },
    winner: null
  });
  
  const [aiThinking, setAiThinking] = useState<boolean>(false);
  const [gameLog, setGameLog] = useState<string[]>([
    '🎮 Pokemon TCG AI Education Battle Started!',
    '🔥 Charmander vs 💧 Squirtle - Classic type matchup!',
    '🤖 AI is ready to demonstrate strategic thinking!',
    '👤 Your turn! Choose your first move.',
    '🎓 Lesson: Fire is weak to Water - plan accordingly!'
  ]);

  const handleSimulateAI = (): void => {
    setAiThinking(true);
    setGameLog(prev => [...prev, '🤖 AI is analyzing the battlefield...']);
    
    setTimeout(() => {
      setAiThinking(false);
      setGameState(prev => ({ 
        ...prev, 
        currentTurn: 'child',
        turnNumber: prev.turnNumber + 1
      }));
      setGameLog(prev => [...prev, 
        '🤖 AI Decision: Squirtle uses Water Gun!',
        '💧 Water beats Fire - Super effective damage!',
        '🎓 AI Lesson: Type advantages are key to victory!',
        '👤 Your turn - how will you respond?'
      ]);
    }, 2500);
  };

  const handlePlayerAction = (actionId: string, pokemon?: any): void => {
    const actionMessages: { [key: string]: string } = {
      draw_card: '👤 You drew a card from your deck!',
      attack: '👤 You used an attack!',
      retreat: '👤 You switched Pokemon!',
      play_pokemon: '👤 You played a Pokemon card!',
      attach_energy: '👤 You attached energy!',
      use_trainer: '👤 You used a trainer card!'
    };
    
    // Simulate drawing a card
    if (actionId === 'draw_card') {
      const newPokemon: PokemonCard = {
        id: `drawn-${Date.now()}`,
        name: ['Eevee', 'Psyduck', 'Magikarp', 'Caterpie'][Math.floor(Math.random() * 4)],
        hp: 40 + Math.floor(Math.random() * 30),
        types: [['Normal', 'Water', 'Water', 'Bug'][Math.floor(Math.random() * 4)]],
        attacks: [{ name: 'Tackle', damage: 10, cost: ['Colorless'], effect: '' }]
      };
      
      setGameState(prev => ({
        ...prev,
        childPlayer: {
          ...prev.childPlayer,
          hand: [...prev.childPlayer.hand, newPokemon]
        }
      }));
    }
    
    // Handle playing Pokemon from hand to bench
    if (actionId === 'play_pokemon' && pokemon) {
      setGameState(prev => {
        const newBenchPokemon = [...prev.childPlayer.benchedPokemon];
        const newHand = prev.childPlayer.hand.filter(p => p.id !== pokemon.id);
        
        // Add to bench if there's space (max 5)
        if (newBenchPokemon.length < 5) {
          newBenchPokemon.push(pokemon);
          
          return {
            ...prev,
            childPlayer: {
              ...prev.childPlayer,
              benchedPokemon: newBenchPokemon,
              hand: newHand
            }
          };
        }
        return prev; // No change if bench is full
      });
      
      setGameLog(prev => [...prev, 
        `👤 You played ${pokemon.name} to your bench!`,
        `🎴 ${pokemon.name} is now ready for battle!`
      ]);
      return;
    }
    
    // Handle retreat (switching active Pokemon)
    if (actionId === 'retreat' && pokemon) {
      setGameState(prev => {
        const currentActive = prev.childPlayer.activePokemon;
        const newBench = prev.childPlayer.benchedPokemon.filter(p => p.id !== pokemon.id);
        
        // Add current active to bench if it exists
        if (currentActive) {
          newBench.push(currentActive);
        }
        
        return {
          ...prev,
          childPlayer: {
            ...prev.childPlayer,
            activePokemon: pokemon,
            benchedPokemon: newBench
          }
        };
      });
      
      setGameLog(prev => [...prev, 
        `👤 You switched ${pokemon.name} to the active position!`,
        `🔄 ${pokemon.name} is now ready to battle!`
      ]);
      return;
    }
    
    // Handle attack
    if (actionId === 'attack' && pokemon) {
      const attack = pokemon as Attack;
      const aiPokemon = gameState.aiPlayer.activePokemon;
      
      // Calculate damage (simplified)
      let damage = attack.damage;
      const childPokemon = gameState.childPlayer.activePokemon;
      
      if (childPokemon && aiPokemon) {
        // Simple type effectiveness calculation
        const childType = childPokemon.types[0];
        const aiType = aiPokemon.types[0];
        
        if ((childType === 'Fire' && aiType === 'Grass') ||
            (childType === 'Water' && aiType === 'Fire') ||
            (childType === 'Grass' && aiType === 'Water') ||
            (childType === 'Electric' && aiType === 'Water')) {
          damage *= 2;
        }
      }
      
      // Apply damage to AI Pokemon
      setGameState(prev => {
        if (prev.aiPlayer.activePokemon) {
          const newAiPokemon = {
            ...prev.aiPlayer.activePokemon,
            hp: Math.max(0, prev.aiPlayer.activePokemon.hp - damage)
          };
          
          return {
            ...prev,
            aiPlayer: {
              ...prev.aiPlayer,
              activePokemon: newAiPokemon
            }
          };
        }
        return prev;
      });
      
      setGameLog(prev => [...prev, 
        `👤 ${childPokemon?.name} used ${attack.name}!`,
        `⚔️ Dealt ${damage} damage to ${aiPokemon?.name}!`,
        damage > attack.damage ? '🔥 It\'s super effective!' : '',
        aiPokemon && (aiPokemon.hp - damage) <= 0 ? `💥 ${aiPokemon.name} was knocked out!` : ''
      ].filter(Boolean));
      return;
    }
    
    setGameLog(prev => [...prev, 
      actionMessages[actionId] || `👤 You performed: ${actionId}`,
      actionId === 'draw_card' ? '🃏 New card added to your hand!' : '🎯 Strategic thinking - just like an AI would do!'
    ]);
  };

  const handleEndTurn = (): void => {
    setGameState(prev => ({ ...prev, currentTurn: 'ai' }));
    setGameLog(prev => [...prev, '🔄 Turn ended - AI\'s turn now!']);
  };

  const handleResetGame = (): void => {
    setGameState({
      currentTurn: 'child',
      gamePhase: 'playing',
      turnNumber: 1,
      childPlayer: { 
        name: 'Ash',
        activePokemon: { 
          id: 'charmander-1', 
          name: 'Charmander', 
          hp: 50, 
          types: ['Fire'], 
          attacks: [
            { name: 'Scratch', damage: 10, cost: ['Colorless'], effect: '' },
            { name: 'Ember', damage: 30, cost: ['Fire', 'Colorless'], effect: 'Flip a coin. If tails, discard 1 Fire Energy.' }
          ]
        },
        benchedPokemon: [
          { 
            id: 'bulbasaur-1', 
            name: 'Bulbasaur', 
            hp: 50, 
            types: ['Grass'], 
            attacks: [
              { name: 'Tackle', damage: 10, cost: ['Colorless'], effect: '' }
            ]
          }
        ],
        hand: [
          { 
            id: 'pikachu-1', 
            name: 'Pikachu', 
            hp: 60, 
            types: ['Electric'], 
            attacks: [
              { name: 'Thunder Shock', damage: 20, cost: ['Electric'], effect: 'Flip a coin. If heads, the Defending Pokemon is now Paralyzed.' }
            ]
          }
        ],
        prizeCards: 6
      },
      aiPlayer: { 
        name: 'Pokemon AI',
        activePokemon: { 
          id: 'squirtle-1', 
          name: 'Squirtle', 
          hp: 50, 
          types: ['Water'], 
          attacks: [
            { name: 'Tackle', damage: 10, cost: ['Colorless'], effect: '' },
            { name: 'Water Gun', damage: 30, cost: ['Water', 'Colorless'], effect: '' }
          ]
        },
        benchedPokemon: [
          { 
            id: 'geodude-1', 
            name: 'Geodude', 
            hp: 70, 
            types: ['Fighting'], 
            attacks: [
              { name: 'Rock Throw', damage: 20, cost: ['Fighting'], effect: '' }
            ]
          }
        ],
        hand: [], // AI hand is hidden
        prizeCards: 6
      },
      winner: null
    });
    setGameLog([
      '🎮 New Pokemon battle started!',
      '🔄 Game reset - ready for more AI learning!',
      '🎓 Remember: Watch how AI thinks strategically!'
    ]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-purple-50 to-green-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <Section variant="game" className="text-center py-6">
          <h1 className="text-4xl font-bold text-purple-800 mb-2">
            🎮 Pokemon TCG AI Education Platform
          </h1>
          <p className="text-lg text-purple-700">
            Learn artificial intelligence through Pokemon strategy!
          </p>
        </Section>

        {/* Main Interface */}
        <Grid cols={3} gap="lg">
          
          {/* Left Column - AI Player Board */}
          <div className="space-y-4">
            <PlayerBoard 
              player={gameState.aiPlayer}
              isAI={true}
            />
          </div>

          {/* Center Column - Game Controls & Type Chart */}
          <div className="space-y-4">
            <EnhancedGameControls
              onSimulateAI={handleSimulateAI}
              aiThinking={aiThinking}
              currentTurn={gameState.currentTurn}
              gameState={gameState}
              onPlayerAction={handlePlayerAction}
              onEndTurn={handleEndTurn}
              onResetGame={handleResetGame}
            />
            
            <EnhancedTypeChart />
            
            {/* Game Status */}
            <Card variant="pokemon" className="p-4">
              <h3 className="font-bold mb-2 text-purple-800">🎯 Battle Status</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Turn:</span>
                  <span className="font-semibold">{gameState.turnNumber}</span>
                </div>
                <div className="flex justify-between">
                  <span>Active Turn:</span>
                  <span className={`font-semibold ${
                    gameState.currentTurn === 'child' ? 'text-red-600' : 'text-blue-600'
                  }`}>
                    {gameState.currentTurn === 'child' ? '👤 You' : '🤖 AI'}
                  </span>
                </div>
                <div className="pt-2 border-t">
                  <div className="text-xs text-gray-600">
                    🔥 {gameState.childPlayer.activePokemon?.name || 'No Pokemon'} vs 💧 {gameState.aiPlayer.activePokemon?.name || 'No Pokemon'}
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Right Column - Child Player Board & Battle Log */}
          <div className="space-y-4">
            <PlayerBoard 
              player={gameState.childPlayer}
              isAI={false}
              onPokemonClick={(pokemon) => console.log('Selected Pokemon:', pokemon)}
            />
            
            <EnhancedBattleLog gameLog={gameLog} />
            
            {/* Quick Tips */}
            <LessonBox type="strategy" icon="🧠">
              <div className="text-xs space-y-1">
                <div><strong>AI Strategy Tips:</strong></div>
                <div>• Type advantages = 2x damage</div>
                <div>• Energy management is crucial</div>
                <div>• AI considers 3+ moves ahead</div>
                <div>• Pattern recognition drives decisions</div>
              </div>
            </LessonBox>
          </div>
          
        </Grid>

        {/* Footer */}
        <Section variant="default" className="text-center">
          <LessonBox type="lesson" icon="🎓">
            <div>
              <strong>🧠 Watch the AI think!</strong> Every move demonstrates artificial intelligence concepts: 
              pattern recognition, strategic planning, decision trees, and learning from outcomes.
            </div>
            <div className="mt-2 text-xs opacity-75">
              This interactive Pokemon battle teaches AI fundamentals through gameplay.
            </div>
          </LessonBox>
        </Section>
        
      </div>
    </div>
  );
};

export default PokemonGameBoard;