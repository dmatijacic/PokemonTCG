# model.py
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Pydantic Models ---
# These define the data structures for communication.

class Player(str, Enum):
    PLAYER = "player"
    OPPONENT = "opponent"

class GameState(BaseModel):
    turn_player: Player
    player_card: Optional[str] = None
    player_hand: List[str]
    opponent_hand: List[str]
    player_battle_zone: List[str]
    opponent_battle_zone: List[str]
    actions_taken_this_turn: int = 0


class Action(BaseModel):
    action_type: str
    card_name: Optional[str] = None
    target: Optional[str] = None

# New model to represent the full payload from the client
class ToolInput(BaseModel):
    game_state: GameState
    proposed_action: Action
