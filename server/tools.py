from langchain_core.tools import tool
from typing import List

def is_card_in_hand(card_name: str, hand: list[str]) -> bool:
    """
    Checks if a specific card exists in the player's hand.
    """
    return card_name in hand

@tool("deck_size")
def deck_size(deck: List[str]) -> int:
    """
    Returns number of cards in a deck.
    Returns True if the deck has 0 cards, False otherwise.
    """
    print(f"[Tool] Deck: {deck}")
    print(f"[Tool] Checking if deck is empty. Card count: {len(deck)}")
    return len(deck)

def is_first_action_of_turn(actions_taken_this_turn: int) -> bool:
    """Checks if this is the first action of the turn."""
    # Pretpostavljamo da klijent šalje broj akcija poduzetih u ovom potezu.
    return actions_taken_this_turn == 0

def is_bench_full(bench: list[str]) -> bool:
    """
    Checks if the bench is full (has 5 or more Pokémon).
    """
    return len(bench) >= 5