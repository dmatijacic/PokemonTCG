# server/tools.py

from langchain.tools import tool
from typing import List

@tool
def is_card_in_hand(card_name: str, player_hand: List[str]) -> bool:
    """Checks if a specific card is present in the player's hand. Input should be the card name."""
    return card_name in player_hand

@tool
def is_first_action_of_turn(actions_taken_this_turn: int) -> bool:
    """Checks if this is the first action of the current turn."""
    return actions_taken_this_turn == 0

@tool
def is_bench_full(player_bench: List[str]) -> bool:
    """Checks if the player's bench has reached its maximum capacity of 5 Pokémon."""
    return len(player_bench) >= 5

@tool
def deck_size(deck: List[str]) -> int:
    """Returns the number of cards remaining in the player's deck."""
    return len(deck)

# This list now contains fully-formed Tool objects thanks to the decorator
tools = [
    is_card_in_hand,
    is_first_action_of_turn,
    is_bench_full,
    deck_size,
]