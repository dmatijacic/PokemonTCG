# server/mcp_tools_server.py
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP


@tool()
def is_card_in_hand(card_name: str, hand: list[str]) -> str:
    """
    Checks if a specific card exists in the player's hand.
    Returns 'VALID' if the card is in hand, otherwise 'INVALID'.
    """
    print(f"[MCP-TOOL] Checking if '{card_name}' is in hand: {hand}")
    if card_name in hand:
        return "VALID"
    return f"INVALID: Card '{card_name}' is not in your hand."

@tool()
def is_first_action_of_turn(actions_taken_this_turn: int) -> bool:
    """Checks if this is the first action of the turn."""
    # Pretpostavljamo da klijent šalje broj akcija poduzetih u ovom potezu.
    return actions_taken_this_turn == 0

@tool()
def is_bench_full(bench: list[str]) -> bool:
    """
    Checks if the bench is full (has 5 or more Pokémon).
    """
    return len(bench) >= 5

# Kreiramo FastMCP objekt. On je sam po sebi ASGI aplikacija.
mcp_app = FastMCP(
    "GameStateValidator",
    title="Pokemon TCG Tools Server",
    description="Provides tools to validate game state.",
    tools=[
        to_fastmcp(is_card_in_hand),
        to_fastmcp(is_first_action_of_turn),
        to_fastmcp(is_bench_full),
    ],
)

mcp_app.settings.host = "0.0.0.0"
mcp_app.settings.port = 8001
mcp_app.settings.log_level = "trace"
if __name__ == "__main__":
    mcp_app.run(transport="streamable-http")

