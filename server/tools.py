from langchain_core.tools import tool
from typing import List

@tool("check_hand_size")
def check_hand_size(player: str) -> str:
    """
    Returns information about starting hand size for validation.
    
    Args:
        player: Either "player" or "opponent"
        
    Returns:
        Information about the starting hand size rules
    """
    print(f"[Tool] Checking hand size rules for {player}")
    return "In Pokemon TCG, each player draws 7 cards to start the game. Both players should have 7 cards in hand at game start."

@tool("check_deck_size")
def check_deck_size(player: str) -> str:
    """
    Returns information about deck size for validation.
    
    Args:
        player: Either "player" or "opponent"
        
    Returns:
        Information about the deck size
    """
    print(f"[Tool] Checking deck size for {player}")
    # This is a simplified tool that returns general deck validation info
    return "Standard Pokemon TCG decks must contain exactly 60 cards. Player decks should start with 60 cards and opponent decks should start with 60 cards."

@tool("check_turn_rules")
def check_turn_rules(turn_count: int) -> str:
    """
    Returns information about turn rules for validation.
    
    Args:
        turn_count: Current turn number
        
    Returns:
        Information about turn rules
    """
    print(f"[Tool] Checking turn rules for turn {turn_count}")
    if turn_count == 0:
        return "Turn 0 indicates game setup phase. Game should start with turn 1 after setup is complete."
    return f"Turn {turn_count} - normal gameplay rules apply."

@tool("check_bench_rules")
def check_bench_rules(bench_size: int) -> str:
    """
    Returns information about bench rules for validation.
    
    Args:
        bench_size: Current number of Pokemon on the bench
        
    Returns:
        Information about bench size rules
    """
    print(f"[Tool] Checking bench rules for bench size {bench_size}")
    if bench_size > 5:
        return "INVALID: Bench cannot have more than 5 Pokemon."
    return f"Bench has {bench_size} Pokemon. Maximum allowed is 5."