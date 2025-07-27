# server/tools.py

def is_card_in_hand(card_name: str, hand: list[str]) -> bool:
    """Provjerava nalazi li se tražena karta u igračevoj ruci."""
    return card_name in hand

def is_first_action_of_turn(actions_taken_this_turn: int) -> bool:
    """Provjerava je li ovo prva akcija u potezu."""
    # Pretpostavljamo da klijent šalje broj akcija poduzetih u ovom potezu.
    return actions_taken_this_turn == 0

def is_bench_full(bench: list[str]) -> bool:
    """Provjerava ima li na klupi 5 Pokémona."""
    return len(bench) >= 5