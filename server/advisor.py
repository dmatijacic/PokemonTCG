from fastmcp import FastMCP
from model import Action, GameState, Player

# --- Advisor Protocol (Placeholder) ---
# This server will provide hints to the player.
advisor_protocol = FastMCP(name="Advisor")

@advisor_protocol.tool
def get_advice(game_state: GameState) -> str:
    """Analyzes the game state and suggests a move for the current player."""
    print("[Advisor] Analyzing board for advice...")
    # Placeholder logic
    if "Pikachu" in game_state.player_hand:
        return "Playing Pikachu seems like a strong move right now."
    return "Consider drawing a card to see what you get."
