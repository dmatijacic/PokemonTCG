# backend/src/models/game_state.py
"""
Pokemon TCG Game State Management for LLM Education Platform
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from dataclasses import dataclass
import uuid
from datetime import datetime

from .pokemon_card import PokemonCard, PokemonType

class GamePhase(str, Enum):
    """Pokemon TCG game phases"""
    SETUP = "setup"
    PLAYING = "playing"
    FINISHED = "finished"

class TurnPhase(str, Enum):
    """Individual turn phases"""
    DRAW = "draw"
    MAIN = "main"
    ATTACK = "attack"
    END = "end"

class PlayerType(str, Enum):
    """Player types"""
    CHILD = "child"
    AI = "ai"

@dataclass
class GameAction:
    """Represents a game action taken by a player"""
    player_id: str
    action_type: str  # "play_pokemon", "attack", "retreat", "play_trainer", etc.
    card_id: Optional[str] = None
    target_id: Optional[str] = None
    additional_data: Optional[Dict] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class PlayerState(BaseModel):
    """Represents a player's current state in the Pokemon game"""
    
    player_id: str
    player_type: PlayerType
    name: str
    
    # Pokemon in play
    active_pokemon: Optional[PokemonCard] = None
    benched_pokemon: List[PokemonCard] = Field(default_factory=list)
    
    # Cards
    hand: List[PokemonCard] = Field(default_factory=list)
    deck: List[PokemonCard] = Field(default_factory=list)
    discard_pile: List[PokemonCard] = Field(default_factory=list)
    
    # Prize cards
    prize_cards: int = 6
    
    # Energy attached to Pokemon (simplified)
    energy_attachments: Dict[str, Dict[PokemonType, int]] = Field(default_factory=dict)
    
    # Game status
    has_drawn_card: bool = False
    has_attached_energy: bool = False
    
    def get_all_pokemon_in_play(self) -> List[PokemonCard]:
        """Get all Pokemon currently in play (active + bench)"""
        pokemon_in_play = []
        if self.active_pokemon:
            pokemon_in_play.append(self.active_pokemon)
        pokemon_in_play.extend(self.benched_pokemon)
        return pokemon_in_play
    
    def get_pokemon_energy(self, pokemon_id: str) -> Dict[PokemonType, int]:
        """Get energy attached to a specific Pokemon"""
        return self.energy_attachments.get(pokemon_id, {})
    
    def attach_energy(self, pokemon_id: str, energy_type: PokemonType, amount: int = 1):
        """Attach energy to a Pokemon"""
        if pokemon_id not in self.energy_attachments:
            self.energy_attachments[pokemon_id] = {}
        
        current = self.energy_attachments[pokemon_id].get(energy_type, 0)
        self.energy_attachments[pokemon_id][energy_type] = current + amount
    
    def can_retreat_active_pokemon(self) -> bool:
        """Check if active Pokemon can retreat"""
        if not self.active_pokemon or len(self.benched_pokemon) == 0:
            return False
        
        # Check if enough energy for retreat cost
        active_energy = self.get_pokemon_energy(self.active_pokemon.id)
        total_energy = sum(active_energy.values())
        
        return total_energy >= self.active_pokemon.retreat_cost
    
    def get_usable_pokemon_attacks(self, pokemon: PokemonCard) -> List:
        """Get attacks that Pokemon can currently use"""
        if not pokemon:
            return []
        
        available_energy = self.get_pokemon_energy(pokemon.id)
        return pokemon.get_usable_attacks(available_energy)
    
    def to_ai_summary(self) -> str:
        """Generate AI-readable summary of player state"""
        summary = f"{self.name} ({self.player_type}):\n"
        
        if self.active_pokemon:
            active_energy = self.get_pokemon_energy(self.active_pokemon.id)
            energy_desc = ", ".join([f"{count} {type}" for type, count in active_energy.items()])
            summary += f"  Active: {self.active_pokemon.name} ({self.active_pokemon.hp} HP, Energy: {energy_desc})\n"
        else:
            summary += "  Active: None\n"
        
        summary += f"  Bench: {len(self.benched_pokemon)} Pokemon\n"
        summary += f"  Hand: {len(self.hand)} cards\n"
        summary += f"  Prize Cards: {self.prize_cards}\n"
        summary += f"  Deck: {len(self.deck)} cards remaining\n"
        
        return summary

class PokemonGameState(BaseModel):
    """Complete Pokemon TCG game state"""
    
    # Game identification
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    
    # Game status
    game_phase: GamePhase = GamePhase.SETUP
    turn_phase: TurnPhase = TurnPhase.DRAW
    current_turn: PlayerType = PlayerType.CHILD
    turn_number: int = 1
    
    # Players
    child_player: PlayerState
    ai_player: PlayerState
    
    # Game history
    action_history: List[GameAction] = Field(default_factory=list)
    
    # Game metadata
    started_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    winner: Optional[PlayerType] = None
    
    # AI context for learning
    ai_decision_context: Dict[str, Any] = Field(default_factory=dict)
    
    def get_current_player(self) -> PlayerState:
        """Get the player whose turn it is"""
        return self.child_player if self.current_turn == PlayerType.CHILD else self.ai_player
    
    def get_opponent_player(self) -> PlayerState:
        """Get the opponent of the current player"""
        return self.ai_player if self.current_turn == PlayerType.CHILD else self.child_player
    
    def add_action(self, action: GameAction):
        """Add an action to the game history"""
        action.timestamp = datetime.now()
        self.action_history.append(action)
        self.last_updated = datetime.now()
    
    def switch_turns(self):
        """Switch to the other player's turn"""
        self.current_turn = PlayerType.AI if self.current_turn == PlayerType.CHILD else PlayerType.CHILD
        self.turn_phase = TurnPhase.DRAW
        
        if self.current_turn == PlayerType.CHILD:
            self.turn_number += 1
        
        # Reset turn-specific flags
        current_player = self.get_current_player()
        current_player.has_drawn_card = False
        current_player.has_attached_energy = False
        
        self.last_updated = datetime.now()
    
    def check_win_conditions(self) -> Optional[PlayerType]:
        """Check if any player has won the game"""
        
        # Win condition 1: Prize cards taken
        if self.child_player.prize_cards <= 0:
            self.winner = PlayerType.CHILD
            self.game_phase = GamePhase.FINISHED
            return PlayerType.CHILD
        
        if self.ai_player.prize_cards <= 0:
            self.winner = PlayerType.AI
            self.game_phase = GamePhase.FINISHED
            return PlayerType.AI
        
        # Win condition 2: No Pokemon in play
        child_has_pokemon = (self.child_player.active_pokemon is not None or 
                           len(self.child_player.benched_pokemon) > 0)
        ai_has_pokemon = (self.ai_player.active_pokemon is not None or 
                         len(self.ai_player.benched_pokemon) > 0)
        
        if not child_has_pokemon:
            self.winner = PlayerType.AI
            self.game_phase = GamePhase.FINISHED
            return PlayerType.AI
        
        if not ai_has_pokemon:
            self.winner = PlayerType.CHILD
            self.game_phase = GamePhase.FINISHED
            return PlayerType.CHILD
        
        # Win condition 3: Cannot draw cards (deck empty)
        if (self.current_turn == PlayerType.CHILD and 
            len(self.child_player.deck) == 0 and 
            not self.child_player.has_drawn_card):
            self.winner = PlayerType.AI
            self.game_phase = GamePhase.FINISHED
            return PlayerType.AI
        
        if (self.current_turn == PlayerType.AI and 
            len(self.ai_player.deck) == 0 and 
            not self.ai_player.has_drawn_card):
            self.winner = PlayerType.CHILD
            self.game_phase = GamePhase.FINISHED
            return PlayerType.CHILD
        
        return None
    
    def get_game_summary_for_ai(self) -> str:
        """Generate comprehensive game summary for AI agents"""
        summary = f"=== Pokemon TCG Game State ===\n"
        summary += f"Game Phase: {self.game_phase}\n"
        summary += f"Turn: {self.turn_number} ({self.current_turn} player, {self.turn_phase} phase)\n\n"
        
        # Child player summary
        summary += self.child_player.to_ai_summary()
        summary += "\n"
        
        # AI player summary  
        summary += self.ai_player.to_ai_summary()
        summary += "\n"
        
        # Recent actions (last 5)
        if self.action_history:
            summary += "Recent Actions:\n"
            for action in self.action_history[-5:]:
                summary += f"  {action.player_id}: {action.action_type}"
                if action.card_id:
                    summary += f" ({action.card_id})"
                summary += f" at {action.timestamp.strftime('%H:%M:%S')}\n"
        
        return summary
    
    def get_educational_context(self) -> Dict[str, Any]:
        """Get educational context for AI learning explanations"""
        current_player = self.get_current_player()
        opponent = self.get_opponent_player()
        
        context = {
            "game_situation": {
                "turn_player": self.current_turn.value,
                "phase": self.turn_phase.value,
                "turn_number": self.turn_number
            },
            "board_state": {
                "child_active": self.child_player.active_pokemon.name if self.child_player.active_pokemon else None,
                "child_bench_count": len(self.child_player.benched_pokemon),
                "ai_active": self.ai_player.active_pokemon.name if self.ai_player.active_pokemon else None,
                "ai_bench_count": len(self.ai_player.benched_pokemon)
            },
            "strategic_considerations": {
                "prize_difference": self.child_player.prize_cards - self.ai_player.prize_cards,
                "hand_sizes": {
                    "child": len(self.child_player.hand),
                    "ai": len(self.ai_player.hand)
                }
            }
        }
        
        # Type advantages if there's an active matchup
        if (self.child_player.active_pokemon and self.ai_player.active_pokemon):
            child_types = self.child_player.active_pokemon.types
            ai_types = self.ai_player.active_pokemon.types
            
            context["type_matchup"] = {
                "child_pokemon": self.child_player.active_pokemon.name,
                "child_types": [t.value for t in child_types],
                "ai_pokemon": self.ai_player.active_pokemon.name,
                "ai_types": [t.value for t in ai_types],
                "child_weaknesses": [w.type.value for w in self.child_player.active_pokemon.weaknesses],
                "ai_weaknesses": [w.type.value for w in self.ai_player.active_pokemon.weaknesses]
            }
        
        return context

# Helper functions for game state management
def create_new_pokemon_game(session_id: str, child_name: str = "trainer") -> PokemonGameState:
    """Create a new Pokemon TCG game state"""
    
    child_player = PlayerState(
        player_id="child",
        player_type=PlayerType.CHILD,
        name=child_name
    )
    
    ai_player = PlayerState(
        player_id="ai",
        player_type=PlayerType.AI,
        name="Pokemon AI"
    )
    
    game_state = PokemonGameState(
        session_id=session_id,
        child_player=child_player,
        ai_player=ai_player,
        current_turn=PlayerType.CHILD  # Child goes first for educational purposes
    )
    
    return game_state

def load_starter_deck(deck_name: str = "fire_starter") -> List[PokemonCard]:
    """Load a starter deck for the game"""
    # This would load from the starter_decks.json file
    # For now, return a simple deck
    from .pokemon_card import PokemonCard, CardCategory, PokemonType, PokemonStage, Attack
    
    deck = [
        # Basic Pokemon
        PokemonCard(
            id="charmander-1", name="Charmander", category=CardCategory.POKEMON,
            hp=50, types=[PokemonType.FIRE], stage=PokemonStage.BASIC,
            attacks=[Attack(name="Scratch", cost=[PokemonType.COLORLESS], damage=10)]
        ),
        PokemonCard(
            id="charmander-2", name="Charmander", category=CardCategory.POKEMON,
            hp=50, types=[PokemonType.FIRE], stage=PokemonStage.BASIC,
            attacks=[Attack(name="Scratch", cost=[PokemonType.COLORLESS], damage=10)]
        ),
        # Energy cards
        PokemonCard(
            id="fire-energy-1", name="Fire Energy", category=CardCategory.ENERGY,
            energy_type=PokemonType.FIRE
        ),
        PokemonCard(
            id="fire-energy-2", name="Fire Energy", category=CardCategory.ENERGY,
            energy_type=PokemonType.FIRE
        ),
    ]
    
    return deck

# Example usage
if __name__ == "__main__":
    # Create a new game
    game = create_new_pokemon_game("test_session", "Ash")
    
    print("New Pokemon game created:")
    print(game.get_game_summary_for_ai())
    
    # Add some sample actions
    game.add_action(GameAction(
        player_id="child",
        action_type="play_pokemon",
        card_id="charmander-1"
    ))
    
    # Check educational context
    context = game.get_educational_context()
    print("\nEducational context:", context)
    
    print("\n✅ Pokemon game state management working correctly!")