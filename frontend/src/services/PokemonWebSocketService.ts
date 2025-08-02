// frontend/src/services/PokemonWebSocketService.ts
/**
 * WebSocket service for real-time Pokemon game communication with backend AI
 */

export interface PokemonGameMessage {
  type: string;
  [key: string]: any;
}

export interface GameState {
  current_turn: 'child' | 'ai';
  turn_number: number;
  game_phase: 'setup' | 'playing' | 'finished';
  child_player: Player;
  ai_player: Player;
  winner: string | null;
}

export interface Player {
  name: string;
  active_pokemon: PokemonCard | null;
  benched_pokemon: PokemonCard[];
  hand?: PokemonCard[];
  hand_count?: number;
  prize_cards: number;
}

export interface PokemonCard {
  id: string;
  name: string;
  hp: number;
  types: string[];
  attacks: Attack[];
}

export interface Attack {
  name: string;
  damage: number;
  cost: string[];
  effect?: string;
}

export interface AIDecision {
  action: string;
  explanation: string;
  type_lesson?: string;
  strategic_insight?: string;
  ai_thinking?: string;
}

export type GameEventHandler = (message: PokemonGameMessage) => void;

export class PokemonWebSocketService {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private eventHandlers: Map<string, GameEventHandler[]> = new Map();
  private isConnecting = false;

  constructor(sessionId: string = 'default_session') {
    this.sessionId = sessionId;
  }

  /**
   * Connect to Pokemon game WebSocket server
   */
  async connect(): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;

    return new Promise((resolve, reject) => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/pokemon-game/${this.sessionId}`;
        
        console.log('🎮 Connecting to Pokemon game server:', wsUrl);
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('✅ Connected to Pokemon game server');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.emit('connected', { sessionId: this.sessionId });
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: PokemonGameMessage = JSON.parse(event.data);
            console.log('📥 Received:', message.type, message);
            this.handleMessage(message);
          } catch (error) {
            console.error('❌ Failed to parse message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('🔌 Pokemon game connection closed:', event.code, event.reason);
          this.isConnecting = false;
          this.ws = null;
          
          this.emit('disconnected', { code: event.code, reason: event.reason });
          
          // Auto-reconnect logic
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Reconnecting to Pokemon game (attempt ${this.reconnectAttempts})...`);
            setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ Pokemon game WebSocket error:', error);
          this.isConnecting = false;
          this.emit('error', { error: error });
          reject(error);
        };

        // Connection timeout
        setTimeout(() => {
          if (this.isConnecting) {
            this.isConnecting = false;
            reject(new Error('Connection timeout'));
          }
        }, 10000);

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * Disconnect from Pokemon game server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  /**
   * Send message to Pokemon game server
   */
  private send(message: PokemonGameMessage): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('❌ Pokemon game not connected');
      return;
    }

    console.log('📤 Sending:', message.type, message);
    this.ws.send(JSON.stringify(message));
  }

  /**
   * Request AI turn simulation
   */
  simulateAITurn(): void {
    this.send({
      type: 'simulate_ai_turn',
      timestamp: Date.now()
    });
  }

  /**
   * Send player action to backend
   */
  sendPlayerAction(actionType: string, actionData: any = {}): void {
    this.send({
      type: 'player_action',
      action_type: actionType,
      action_data: actionData,
      timestamp: Date.now()
    });
  }

  /**
   * Request current game state
   */
  requestGameState(): void {
    this.send({
      type: 'get_game_state'
    });
  }

  /**
   * Reset game to initial state
   */
  resetGame(): void {
    this.send({
      type: 'reset_game',
      timestamp: Date.now()
    });
  }

  /**
   * Request type effectiveness advice
   */
  requestTypeAdvice(attackingType: string, defendingType: string): void {
    this.send({
      type: 'get_type_advice',
      attacking_type: attackingType,
      defending_type: defendingType
    });
  }

  /**
   * Handle incoming messages from server
   */
  private handleMessage(message: PokemonGameMessage): void {
    this.emit(message.type, message);
    this.emit('message', message); // Generic message handler
  }

  /**
   * Register event handler
   */
  on(eventType: string, handler: GameEventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }

  /**
   * Remove event handler
   */
  off(eventType: string, handler: GameEventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Emit event to registered handlers
   */
  private emit(eventType: string, data: any): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`❌ Error in ${eventType} handler:`, error);
        }
      });
    }
  }

  /**
   * Get connection status
   */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get session ID
   */
  get getSessionId(): string {
    return this.sessionId;
  }
}