# model.py
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Pydantic Modeli (ostaju isti) ---
class Player(str, Enum):
    PLAYER = "player"
    OPPONENT = "opponent"

            # turn_player: gameState.turn_player,

            # player_hand: gameState.player_hand.map((c) => c.name),
            # player_deck: gameState.player_deck.map((c) => c.name),
            # player_bench: gameState.player_bench.map((c) => c.name),

            # opponent_hand: gameState.opponent_hand.map((c) => c.name),
            # opponent_deck: gameState.opponent_deck.map((c) => c.name),
            # opponent_bench: gameState.opponent_bench.map((c) => c.name),
            # turn_count: gameState.turn_count,
            # actions_taken_this_turn: gameState.actions_taken_this_turn++,
    
class GameState(BaseModel):
    turn_player: Player

    player_hand: list[str] = []
    player_deck: list[str] = []
    player_bench: list[str] = []

    opponent_hand: list[str] = []
    opponent_deck: list[str] = []
    opponent_bench: list[str] = []
    
    turn_count: int
    actions_taken_this_turn: int = 0

class ProposedAction(BaseModel):
    action_type: str
    card_name: str | None = None
    target: str | None = None

class ToolInput(BaseModel):
    game_state: GameState
    proposed_action: ProposedAction