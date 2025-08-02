import React, { useState, useEffect } from 'react';
import { usePokemonGame } from '../hooks/usePokemonGame';
import type { PokemonCard, Player, Attack } from '../services/PokemonWebSocketService';

// Enhanced Pokemon Game Board with Backend Integration
const EnhancedPokemonGameBoard = () => {
  const {
    isConnected,
    isConnecting,
    connectionError,
    gameState,
    aiThinking,
    aiDecision,
    gameLog,
    connect,
    disconnect,
    simulateAITurn,
    sendPlayerAction,
    resetGame,
    requestTypeAdvice
  } = usePokemonGame();

  const [selectedAction, setSelectedAction] = useState(null);
  const [showHandSelection, setShowHandSelection] = useState(false);
  const [showAttackSelection, setShowAttackSelection] = useState(false);

  // Auto-connect on component mount
  useEffect(() => {
    if (!isConnected && !isConnecting && !connectionError) {
      connect();
    }
  }, [isConnected, isConnecting, connectionError, connect]);

  // Connection Status Component
  const ConnectionStatus = () => (
    <div className="mb-6 p-4 rounded-lg border-2 bg-gradient-to-r from-purple-50 to-blue-50 border-purple-300">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-500 animate-pulse' : 
            isConnecting ? 'bg-yellow-500 animate-spin' : 
            'bg-red-500'
          }`} />
          <span className="font-semibold text-purple-800">
            {isConnected ? '🎮 Connected to Pokemon AI Server' :
             isConnecting ? '🔄 Connecting to Pokemon AI...' :
             connectionError ? `❌ ${connectionError}` :
             '🔌 Disconnected'}
          </span>
        </div>
        
        <div className="flex gap-2">
          {!isConnected && !isConnecting && (
            <button
              onClick={connect}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
            >
              Connect
            </button>
          )}
          {isConnected && (
            <button
              onClick={disconnect}
              className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 transition-colors"
            >
              Disconnect
            </button>
          )}
        </div>
      </div>
      
      {connectionError && (
        <div className="mt-2 text-sm text-red-700 bg-red-100 p-2 rounded">
          Make sure the backend server is running: <code>python backend/main.py</code>
        </div>
      )}
    </div>
  );

  // AI Thought Bubble Component
  const AIThoughtBubble = () => (
    <div className="mb-4 p-4 bg-blue-50 border-2 border-blue-300 rounded-lg relative">
      <div className="absolute -top-2 left-6 w-0 h-0 border-l-8 border-r-8 border-b-8 border-l-transparent border-r-transparent border-b-blue-300" />
      
      <h3 className="font-bold text-blue-800 mb-3 flex items-center gap-2">
        🤖 AI Thinking Process
      </h3>
      
      {aiThinking ? (
        <div className="flex items-center gap-3">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
          </div>
          <span className="text-blue-700">AI is analyzing Pokemon matchups and strategies...</span>
        </div>
      ) : aiDecision ? (
        <div className="space-y-3">
          <div className="text-blue-800 font-medium">{aiDecision.explanation}</div>
          
          {aiDecision.type_lesson && (
            <div className="bg-green-100 border border-green-300 rounded-lg p-3 text-green-800 text-sm">
              <div className="font-medium mb-1">🎓 AI Lesson:</div>
              {aiDecision.type_lesson}
            </div>
          )}
          
          {aiDecision.strategic_insight && (
            <div className="bg-purple-100 border border-purple-300 rounded-lg p-3 text-purple-800 text-sm">
              <div className="font-medium mb-1">🎯 Strategic Insight:</div>
              {aiDecision.strategic_insight}
            </div>
          )}
        </div>
      ) : (
        <div className="text-blue-700">
          Ready to demonstrate AI strategic thinking! Click "Simulate AI Turn" when it's the AI's turn.
        </div>
      )}
    </div>
  );

  // Pokemon Card Display Component
  const PokemonCardDisplay: React.FC<{
    pokemon: PokemonCard | null;
    variant?: 'active' | 'bench' | 'hand';
    isAI?: boolean;
    onClick?: () => void;
  }> = ({ pokemon, variant = 'bench', isAI = false, onClick }) => {
    if (!pokemon) {
      return (
        <div className="w-20 h-28 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
          <span className="text-gray-500 text-xs">Empty</span>
        </div>
      );
    }

    const cardVariant = isAI ? 'border-blue-300 bg-blue-50' : 'border-red-300 bg-red-50';
    const isActive = variant === 'active';

    return (
      <div
        className={`w-32 h-44 border-2 rounded-lg p-3 cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1 ${cardVariant} ${
          isActive ? 'ring-2 ring-yellow-400 bg-yellow-50' : ''
        }`}
        onClick={onClick}
      >
        <div className="text-center space-y-2">
          <h4 className="font-bold text-sm truncate">{pokemon.name}</h4>
          <div className="text-xs text-gray-600">HP: {pokemon.hp}</div>
          
          <div className="flex justify-center gap-1 flex-wrap">
            {pokemon.types.map((type: string) => (
              <span
                key={type}
                className={`px-2 py-1 rounded-full text-xs font-medium text-white ${
                  type === 'Fire' ? 'bg-red-500' :
                  type === 'Water' ? 'bg-blue-500' :
                  type === 'Grass' ? 'bg-green-500' :
                  type === 'Electric' ? 'bg-yellow-500' :
                  'bg-gray-500'
                }`}
              >
                {type}
              </span>
            ))}
          </div>
          
          {pokemon.attacks && pokemon.attacks.length > 0 && (
            <div className="space-y-1">
              {pokemon.attacks.slice(0, 2).map((attack: Attack, index: number) => (
                <div key={index} className="text-xs">
                  <div className="font-medium">{attack.name}</div>
                  <div className="text-gray-500">{attack.damage} damage</div>
                </div>
              ))}
            </div>
          )}

          {isActive && (
            <div className="text-xs font-bold text-yellow-700 bg-yellow-200 rounded px-2 py-1">
              ACTIVE
            </div>
          )}
        </div>
      </div>
    );
  };

  // Player Board Component
  const PlayerBoard: React.FC<{
    player: Player;
    isAI?: boolean;
  }> = ({ player, isAI = false }) => {
    const boardVariant = isAI ? 'bg-blue-50 border-blue-300' : 'bg-red-50 border-red-300';
    const titleColor = isAI ? 'text-blue-800' : 'text-red-800';
    const playerIcon = isAI ? '🤖' : '👤';

    return (
      <div className={`border-2 rounded-lg p-4 ${boardVariant}`}>
        <h2 className={`text-xl font-bold mb-4 ${titleColor}`}>
          {playerIcon} {player.name}
        </h2>
        
        <div className="mb-4">
          <h3 className="font-semibold mb-2">Active Pokemon:</h3>
          <PokemonCardDisplay
            pokemon={player.active_pokemon}
            variant="active"
            isAI={isAI}
          />
        </div>
        
        <div className="mb-4">
          <h3 className="font-semibold mb-2">Bench ({player.benched_pokemon?.length || 0}/5):</h3>
          <div className="flex gap-2 flex-wrap">
            {player.benched_pokemon?.map((pokemon: PokemonCard, index: number) => (
              <PokemonCardDisplay
                key={index}
                pokemon={pokemon}
                variant="bench"
                isAI={isAI}
              />
            ))}
            {Array.from({ length: 5 - (player.benched_pokemon?.length || 0) }).map((_, index) => (
              <PokemonCardDisplay 
                key={`empty-${index}`} 
                pokemon={null} 
                onClick={undefined}
              />
            ))}
          </div>
        </div>
        
        {!isAI && player.hand && (
          <div className="mb-4">
            <h3 className="font-semibold mb-2">Hand ({player.hand.length}):</h3>
            <div className="flex gap-2 flex-wrap">
              {player.hand.map((pokemon: PokemonCard, index: number) => (
                <div key={index} className="w-20 h-28">
                  <PokemonCardDisplay
                    pokemon={pokemon}
                    variant="hand"
                    onClick={() => handlePlayPokemon(pokemon)}
                  />
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="space-y-2">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${isAI ? 'bg-blue-600' : 'bg-red-600'}`}
              style={{ width: `${((6 - player.prize_cards) / 6) * 100}%` }}
            />
          </div>
          <div className="text-sm text-gray-600">
            Prize Cards Taken: {6 - player.prize_cards} / 6
          </div>
          {isAI && (
            <div className="text-sm text-gray-600">
              Cards in hand: {player.hand_count || 0}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Game Controls Component
  const GameControls = () => (
    <div className="space-y-4">
      <div className="border-2 border-purple-300 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4">
        <h3 className="font-bold mb-3 text-purple-800">🎮 Game Controls</h3>
        
        <div className="space-y-3">
          <button
            onClick={simulateAITurn}
            disabled={!isConnected || aiThinking || gameState?.current_turn !== 'ai'}
            className={`w-full px-4 py-2 rounded-lg font-medium transition-all ${
              !isConnected || aiThinking || gameState?.current_turn !== 'ai'
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white shadow-lg'
            }`}
          >
            {aiThinking ? (
              <div className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                AI Analyzing...
              </div>
            ) : (
              '🧠 Simulate AI Turn'
            )}
          </button>
          
          <div className="text-center text-sm text-gray-600">
            Current Turn: 
            <span className="font-semibold ml-1">
              {gameState?.current_turn === 'child' ? '👤 Your Turn' : '🤖 AI Turn'}
            </span>
          </div>
        </div>
      </div>

      <div className="border-2 border-red-300 bg-red-50 rounded-lg p-4">
        <h3 className="font-bold mb-3 text-red-800">👤 Your Actions</h3>
        
        <div className="grid grid-cols-2 gap-2 mb-3">
          {[
            { id: 'draw_card', name: 'Draw Card', icon: '🃏' },
            { id: 'attack', name: 'Attack', icon: '⚔️' },
            { id: 'end_turn', name: 'End Turn', icon: '🔄' },
            { id: 'reset_game', name: 'New Game', icon: '🎮' }
          ].map((action) => (
            <button
              key={action.id}
              onClick={() => handlePlayerAction(action.id)}
              disabled={!isConnected || gameState?.current_turn !== 'child'}
              className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                !isConnected || gameState?.current_turn !== 'child'
                  ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  : 'bg-white border border-gray-300 hover:bg-blue-50 hover:border-blue-400'
              }`}
            >
              <span className="mr-1">{action.icon}</span>
              {action.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  // Battle Log Component
  const BattleLog = () => (
    <div className="border-2 border-gray-300 bg-white rounded-lg p-4">
      <h3 className="font-bold mb-3 text-gray-800">📜 Battle Log</h3>
      <div className="h-32 overflow-y-auto space-y-1 text-sm">
        {gameLog.map((log, index) => (
          <div key={index} className="text-gray-800 leading-relaxed p-1 hover:bg-gray-50 rounded">
            {log}
          </div>
        ))}
      </div>
    </div>
  );

  // Handle player actions
  const handlePlayerAction = (actionType: string): void => {
    if (actionType === 'reset_game') {
      resetGame();
    } else {
      sendPlayerAction(actionType);
    }
  };

  const handlePlayPokemon = (pokemon: PokemonCard): void => {
    sendPlayerAction('play_pokemon', { pokemon_id: pokemon.id });
  };

  // Render loading state
  if (!gameState && isConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-100 via-purple-50 to-green-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🎮</div>
          <h2 className="text-2xl font-bold text-purple-800 mb-2">Loading Pokemon Game...</h2>
          <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-purple-50 to-green-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center py-6 border-2 border-purple-300 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg">
          <h1 className="text-4xl font-bold text-purple-800 mb-2">
            🎮 Pokemon TCG AI Education Platform
          </h1>
          <p className="text-lg text-purple-700">
            Learn artificial intelligence through Pokemon strategy!
          </p>
        </div>

        {/* Connection Status */}
        <ConnectionStatus />

        {/* Main Game Interface */}
        {isConnected && gameState && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Column - AI Player */}
            <div className="space-y-4">
              <PlayerBoard player={gameState.ai_player} isAI={true} />
            </div>

            {/* Center Column - Game Controls & AI Thinking */}
            <div className="space-y-4">
              <AIThoughtBubble />
              <GameControls />
              
              {/* Game Status */}
              <div className="border-2 border-purple-300 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4">
                <h3 className="font-bold mb-2 text-purple-800">🎯 Battle Status</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Turn:</span>
                    <span className="font-semibold">{gameState.turn_number}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Phase:</span>
                    <span className="font-semibold capitalize">{gameState.game_phase}</span>
                  </div>
                  <div className="pt-2 border-t">
                    <div className="text-xs text-gray-600">
                      {gameState.child_player.active_pokemon?.name || 'No Pokemon'} vs {gameState.ai_player.active_pokemon?.name || 'No Pokemon'}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column - Child Player & Battle Log */}
            <div className="space-y-4">
              <PlayerBoard player={gameState.child_player} isAI={false} />
              <BattleLog />
            </div>
            
          </div>
        )}

        {/* Footer */}
        <div className="text-center border-2 border-gray-300 bg-white rounded-lg p-4">
          <div className="bg-blue-100 border border-blue-300 rounded-lg p-3 text-blue-800 text-sm">
            <strong>🧠 Watch the AI think!</strong> Every move demonstrates artificial intelligence concepts: 
            pattern recognition, strategic planning, decision trees, and learning from outcomes.
            <div className="mt-2 text-xs opacity-75">
              This interactive Pokemon battle teaches AI fundamentals through gameplay.
            </div>
          </div>
        </div>
        
      </div>
    </div>
  );
};

export default EnhancedPokemonGameBoard;