# model.py
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Pydantic Modeli (ostaju isti) ---
class Player(str, Enum):
    PLAYER = "player"
    OPPONENT = "opponent"

class GameZone(str, Enum):
    HAND = "hand"
    BENCH = "bench"
    DECK = "deck"
    CARD = "card"

class Action(str, Enum):
    PLAY = "play"
    ATTACK = "attack"
    SWITCH = "switch"
    DRAW = "draw"
    DISCARD = "discard"

class GameState(BaseModel):
    turn_player: Player

    player_hand: list[str] = []
    player_deck: list[str] = []
    player_bench: list[str] = []
    player_active_pokemon: Optional[str] = None

    opponent_hand: list[str] = []
    opponent_deck: list[str] = []
    opponent_bench: list[str] = []
    opponent_active_pokemon: Optional[str] = None
    
    turn_count: int
    actions_taken_this_turn: int = 0

class ProposedAction(BaseModel):
    action: Action
    source: GameZone | None = None
    target: GameZone | None = None
    context: dict = Field(default_factory=dict)

class ToolInput(BaseModel):
    game_state: GameState
    proposed_action: ProposedAction