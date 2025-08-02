# backend/src/websocket/pokemon_game_handler.py
"""
Pokemon TCG Game WebSocket Handler - Connects frontend to AI agents
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime

from ..ai_agents.opponent_ai import PokemonOpponentAI
from ..models.game_state import PokemonGameState, create_new_pokemon_game
from ..game.type_advantages import PokemonTypeCalculator

class PokemonGameWebSocketHandler:
    """
    Handles real-time Pokemon game communication between frontend and AI
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.type_calc = PokemonTypeCalculator()
    
    async def handle_connection(self, websocket: WebSocket, session_id: str):
        """Handle new Pokemon game connection"""
        await websocket.accept()
        
        # Initialize game session
        game_state = create_new_pokemon_game(session_id, "Ash")
        ai_opponent = PokemonOpponentAI(session_id, "Ash", "easy")
        
        self.active_sessions[session_id] = {
            "websocket": websocket,
            "game_state": game_state,
            "ai_opponent": ai_opponent,
            "connected_at": datetime.now()
        }
        
        print(f"🎮 Pokemon session {session_id} connected - sending initial state")
        
        # Send initial game state
        await self._send_game_state_update(session_id)
        
        try:
            while True:
                # Receive message from frontend
                data = await websocket.receive_text()
                message = json.loads(data)
                
                print(f"📥 Received from {session_id}: {message.get('type', 'unknown')}")
                
                # Route message to appropriate handler
                await self._handle_game_message(session_id, message)
                
        except WebSocketDisconnect:
            print(f"🔌 Pokemon session {session_id} disconnected")
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
        except Exception as e:
            print(f"❌ Error in Pokemon session {session_id}: {e}")
            await self._send_error(session_id, str(e))
    
    async def _handle_game_message(self, session_id: str, message: Dict[str, Any]):
        """Route game messages to appropriate handlers"""
        message_type = message.get("type")
        
        handlers = {
            "simulate_ai_turn": self._handle_ai_turn_simulation,
            "player_action": self._handle_player_action,
            "get_game_state": self._handle_get_game_state,
            "reset_game": self._handle_reset_game,
            "get_type_advice": self._handle_type_advice_request
        }
        
        handler = handlers.get(message_type)
        if handler:
            await handler(session_id, message)
        else:
            await self._send_error(session_id, f"Unknown message type: {message_type}")
    
    async def _handle_ai_turn_simulation(self, session_id: str, message: Dict[str, Any]):
        """Handle AI turn simulation request"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        game_state = session["game_state"]
        ai_opponent = session["ai_opponent"]
        
        # Send "AI thinking" status
        await self._send_message(session_id, {
            "type": "ai_thinking_started",
            "message": "🤖 AI is analyzing Pokemon matchups and strategies..."
        })
        
        # Simulate AI processing time (2 seconds)
        await asyncio.sleep(2)
        
        try:
            # Get AI decision
            ai_decision = await ai_opponent.make_move(game_state)
            
            # Update game state based on AI decision
            self._apply_ai_decision(game_state, ai_decision)
            
            # Send AI decision to frontend
            await self._send_message(session_id, {
                "type": "ai_decision_made",
                "ai_decision": ai_decision,
                "game_state": self._serialize_game_state(game_state),
                "educational_context": {
                    "type_lesson": ai_decision.get("type_lesson"),
                    "strategic_insight": ai_decision.get("strategic_insight"),
                    "ai_thinking": ai_decision.get("ai_thinking")
                }
            })
            
            # Switch turn back to child
            game_state.switch_turns()
            await self._send_game_state_update(session_id)
            
        except Exception as e:
            print(f"❌ AI decision error: {e}")
            await self._send_message(session_id, {
                "type": "ai_error",
                "message": "AI encountered an error while thinking. Try again!",
                "error": str(e)
            })
    
    async def _handle_player_action(self, session_id: str, message: Dict[str, Any]):
        """Handle player action (draw card, attack, etc.)"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        game_state = session["game_state"]
        
        action_type = message.get("action_type")
        action_data = message.get("action_data", {})
        
        print(f"🎮 Player action: {action_type} with data: {action_data}")
        
        try:
            # Process player action
            result = self._process_player_action(game_state, action_type, action_data)
            
            # Send result back to frontend
            await self._send_message(session_id, {
                "type": "player_action_result",
                "action_type": action_type,
                "result": result,
                "game_state": self._serialize_game_state(game_state)
            })
            
            # Check if it's now AI's turn
            if game_state.current_turn.value == "ai":
                await self._send_message(session_id, {
                    "type": "ai_turn_ready",
                    "message": "🤖 It's AI's turn now! Click 'Simulate AI Turn' to see what the AI does."
                })
            
        except Exception as e:
            print(f"❌ Player action error: {e}")
            await self._send_error(session_id, f"Action failed: {str(e)}")
    
    async def _handle_get_game_state(self, session_id: str, message: Dict[str, Any]):
        """Send current game state to frontend"""
        await self._send_game_state_update(session_id)
    
    async def _handle_reset_game(self, session_id: str, message: Dict[str, Any]):
        """Reset game to initial state"""
        if session_id not in self.active_sessions:
            return
        
        # Create new game state
        new_game_state = create_new_pokemon_game(session_id, "Ash")
        self.active_sessions[session_id]["game_state"] = new_game_state
        
        await self._send_message(session_id, {
            "type": "game_reset",
            "message": "🔄 New Pokemon battle started!",
            "game_state": self._serialize_game_state(new_game_state)
        })
    
    async def _handle_type_advice_request(self, session_id: str, message: Dict[str, Any]):
        """Provide type effectiveness advice"""
        attacking_type = message.get("attacking_type")
        defending_type = message.get("defending_type")
        
        if not (attacking_type and defending_type):
            await self._send_error(session_id, "Missing type information for advice")
            return
        
        try:
            from ..models.pokemon_card import PokemonType
            attack_type_enum = PokemonType(attacking_type.lower())
            defend_type_enum = PokemonType(defending_type.lower())
            
            effectiveness = self.type_calc.get_effectiveness(attack_type_enum, defend_type_enum)
            explanation = self.type_calc.get_ai_explanation(attack_type_enum, defend_type_enum)
            
            await self._send_message(session_id, {
                "type": "type_advice",
                "attacking_type": attacking_type,
                "defending_type": defending_type,
                "effectiveness": effectiveness,
                "explanation": explanation
            })
            
        except Exception as e:
            await self._send_error(session_id, f"Type advice error: {str(e)}")
    
    def _apply_ai_decision(self, game_state: PokemonGameState, ai_decision: Dict[str, Any]):
        """Apply AI decision to game state"""
        action = ai_decision.get("action")
        
        if action == "attack":
            # AI attacks - simulate damage
            child_pokemon = game_state.child_player.active_pokemon
            if child_pokemon and child_pokemon.hp:
                damage = 30  # Simplified damage
                child_pokemon.hp = max(0, child_pokemon.hp - damage)
        
        elif action == "switch":
            # AI switches Pokemon (simplified)
            ai_bench = game_state.ai_player.benched_pokemon
            if ai_bench:
                # Switch first benched Pokemon to active
                new_active = ai_bench.pop(0)
                if game_state.ai_player.active_pokemon:
                    ai_bench.append(game_state.ai_player.active_pokemon)
                game_state.ai_player.active_pokemon = new_active
        
        # Add action to game history
        from ..models.game_state import GameAction
        game_state.add_action(GameAction(
            player_id="ai",
            action_type=action,
            additional_data={"explanation": ai_decision.get("explanation")}
        ))
    
    def _process_player_action(self, game_state: PokemonGameState, action_type: str, action_data: Dict):
        """Process player action and update game state"""
        if action_type == "draw_card":
            # Simulate drawing a card
            from ..models.pokemon_card import PokemonCard, CardCategory, PokemonType
            new_card = PokemonCard(
                id=f"drawn-{datetime.now().timestamp()}",
                name="Potion",
                category=CardCategory.TRAINER,
                effect="Heal 20 damage from your Pokemon"
            )
            game_state.child_player.hand.append(new_card)
            return {"message": "Drew a Potion card!", "card": new_card.name}
        
        elif action_type == "attack":
            # Player attacks AI
            ai_pokemon = game_state.ai_player.active_pokemon
            if ai_pokemon and ai_pokemon.hp:
                damage = action_data.get("damage", 20)
                ai_pokemon.hp = max(0, ai_pokemon.hp - damage)
                game_state.switch_turns()  # Switch to AI turn
                return {"message": f"Dealt {damage} damage to {ai_pokemon.name}!", "damage": damage}
        
        elif action_type == "end_turn":
            game_state.switch_turns()
            return {"message": "Turn ended - AI's turn now!"}
        
        return {"message": f"Processed {action_type} action"}
    
    def _serialize_game_state(self, game_state: PokemonGameState) -> Dict[str, Any]:
        """Convert game state to JSON-serializable format"""
        return {
            "current_turn": game_state.current_turn.value,
            "turn_number": game_state.turn_number,
            "game_phase": game_state.game_phase.value,
            "child_player": {
                "name": game_state.child_player.name,
                "active_pokemon": self._serialize_pokemon(game_state.child_player.active_pokemon),
                "benched_pokemon": [self._serialize_pokemon(p) for p in game_state.child_player.benched_pokemon],
                "hand": [self._serialize_pokemon(p) for p in game_state.child_player.hand],
                "prize_cards": game_state.child_player.prize_cards
            },
            "ai_player": {
                "name": game_state.ai_player.name,
                "active_pokemon": self._serialize_pokemon(game_state.ai_player.active_pokemon),
                "benched_pokemon": [self._serialize_pokemon(p) for p in game_state.ai_player.benched_pokemon],
                "hand_count": len(game_state.ai_player.hand),  # Hide AI hand
                "prize_cards": game_state.ai_player.prize_cards
            },
            "winner": game_state.winner.value if game_state.winner else None
        }
    
    def _serialize_pokemon(self, pokemon) -> Optional[Dict[str, Any]]:
        """Convert Pokemon card to JSON format"""
        if not pokemon:
            return None
        
        return {
            "id": pokemon.id,
            "name": pokemon.name,
            "hp": pokemon.hp,
            "types": [t.value for t in pokemon.types] if pokemon.types else [],
            "attacks": [
                {
                    "name": attack.name,
                    "damage": attack.get_damage_value(),
                    "cost": [str(c) for c in attack.cost],
                    "effect": attack.effect
                }
                for attack in pokemon.attacks
            ] if pokemon.attacks else []
        }
    
    async def _send_game_state_update(self, session_id: str):
        """Send complete game state update"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        game_state = session["game_state"]
        
        await self._send_message(session_id, {
            "type": "game_state_update",
            "game_state": self._serialize_game_state(game_state),
            "educational_context": game_state.get_educational_context()
        })
    
    async def _send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific session"""
        if session_id not in self.active_sessions:
            return
        
        websocket = self.active_sessions[session_id]["websocket"]
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"❌ Failed to send message to {session_id}: {e}")
    
    async def _send_error(self, session_id: str, error_message: str):
        """Send error message to frontend"""
        await self._send_message(session_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })

# Update main.py to use the WebSocket handler
from fastapi import FastAPI

app = FastAPI()
pokemon_ws_handler = PokemonGameWebSocketHandler()

@app.websocket("/ws/pokemon-game/{session_id}")
async def pokemon_game_websocket(websocket: WebSocket, session_id: str):
    """Enhanced WebSocket endpoint for Pokemon game"""
    await pokemon_ws_handler.handle_connection(websocket, session_id)