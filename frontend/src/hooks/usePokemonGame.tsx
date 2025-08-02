// frontend/src/hooks/usePokemonGame.ts
import { useState, useEffect, useCallback, useRef } from 'react';
import { PokemonWebSocketService, GameState, AIDecision, PokemonGameMessage } from '../services/PokemonWebSocketService';

export interface UsePokemonGameReturn {
  // Connection state
  isConnected: boolean;
  isConnecting: boolean;
  connectionError: string | null;

  // Game state
  gameState: GameState | null;
  aiThinking: boolean;
  aiDecision: AIDecision | null;
  gameLog: string[];

  // Actions
  connect: () => Promise<void>;
  disconnect: () => void;
  simulateAITurn: () => void;
  sendPlayerAction: (actionType: string, actionData?: any) => void;
  resetGame: () => void;
  requestTypeAdvice: (attackingType: string, defendingType: string) => void;
}

export const usePokemonGame = (sessionId?: string): UsePokemonGameReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [aiThinking, setAiThinking] = useState(false);
  const [aiDecision, setAiDecision] = useState<AIDecision | null>(null);
  const [gameLog, setGameLog] = useState<string[]>([
    '🎮 Welcome to Pokemon TCG AI Education!',
    '🤖 Connect to start playing with AI opponents...'
  ]);

  const wsService = useRef<PokemonWebSocketService | null>(null);

  // Initialize WebSocket service
  useEffect(() => {
    const session = sessionId || `session_${Date.now()}`;
    wsService.current = new PokemonWebSocketService(session);

    // Register event handlers
    wsService.current.on('connected', () => {
      setIsConnected(true);
      setIsConnecting(false);
      setConnectionError(null);
      addToGameLog('✅ Connected to Pokemon AI server!');
    });

    wsService.current.on('disconnected', () => {
      setIsConnected(false);
      setIsConnecting(false);
      addToGameLog('🔌 Disconnected from Pokemon server');
    });

    wsService.current.on('error', (data) => {
      setConnectionError(data.error?.message || 'Connection error');
      setIsConnecting(false);
      addToGameLog('❌ Connection error - check backend server');
    });

    wsService.current.on('game_state_update', (message: PokemonGameMessage) => {
      setGameState(message.game_state);
      addToGameLog('🎮 Game state updated');
    });

    wsService.current.on('ai_thinking_started', (message: PokemonGameMessage) => {
      setAiThinking(true);
      setAiDecision(null);
      addToGameLog(message.message || '🤖 AI is thinking...');
    });

    wsService.current.on('ai_decision_made', (message: PokemonGameMessage) => {
      setAiThinking(false);
      setAiDecision(message.ai_decision);
      setGameState(message.game_state);
      
      const decision = message.ai_decision;
      addToGameLog(`🤖 AI Decision: ${decision.explanation}`);
      
      if (decision.type_lesson) {
        addToGameLog(`🎓 ${decision.type_lesson}`);
      }
      
      if (decision.strategic_insight) {
        addToGameLog(`🎯 ${decision.strategic_insight}`);
      }
    });

    wsService.current.on('ai_error', (message: PokemonGameMessage) => {
      setAiThinking(false);
      addToGameLog(`❌ AI Error: ${message.message}`);
    });

    wsService.current.on('player_action_result', (message: PokemonGameMessage) => {
      setGameState(message.game_state);
      addToGameLog(`👤 ${message.result.message}`);
    });

    wsService.current.on('game_reset', (message: PokemonGameMessage) => {
      setGameState(message.game_state);
      setAiDecision(null);
      setGameLog(['🎮 New Pokemon battle started!', '🔥 Choose your first move!']);
    });

    wsService.current.on('type_advice', (message: PokemonGameMessage) => {
      addToGameLog(`🎓 Type Advice: ${message.explanation}`);
    });

    // Cleanup
    return () => {
      if (wsService.current) {
        wsService.current.disconnect();
      }
    };
  }, [sessionId]);

  const addToGameLog = useCallback((message: string) => {
    setGameLog(prev => [...prev.slice(-19), message]); // Keep last 20 messages
  }, []);

  const connect = useCallback(async () => {
    if (!wsService.current || isConnecting) return;
    
    setIsConnecting(true);
    setConnectionError(null);
    
    try {
      await wsService.current.connect();
    } catch (error) {
      setConnectionError(error instanceof Error ? error.message : 'Connection failed');
      setIsConnecting(false);
    }
  }, [isConnecting]);

  const disconnect = useCallback(() => {
    if (wsService.current) {
      wsService.current.disconnect();
    }
  }, []);

  const simulateAITurn = useCallback(() => {
    if (wsService.current && isConnected) {
      wsService.current.simulateAITurn();
    }
  }, [isConnected]);

  const sendPlayerAction = useCallback((actionType: string, actionData: any = {}) => {
    if (wsService.current && isConnected) {
      wsService.current.sendPlayerAction(actionType, actionData);
    }
  }, [isConnected]);

  const resetGame = useCallback(() => {
    if (wsService.current && isConnected) {
      wsService.current.resetGame();
    }
  }, [isConnected]);

  const requestTypeAdvice = useCallback((attackingType: string, defendingType: string) => {
    if (wsService.current && isConnected) {
      wsService.current.requestTypeAdvice(attackingType, defendingType);
    }
  }, [isConnected]);

  return {
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
  };
};