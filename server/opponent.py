from fastmcp import FastMCP
from model import Action, GameState, Player

# --- Opponent Protocol (Placeholder) ---
# This server will eventually contain the AI logic for the opponent's turn.
opponent_protocol = FastMCP(name="Opponent")

@opponent_protocol.tool
def get_opponent_move(game_state: GameState) -> str:
    """Determines the opponent's next best move based on the game state."""
    print("[Opponent] Calculating next move...")
    # Placeholder logic
    return "Opponent plays Charizard and ends their turn."