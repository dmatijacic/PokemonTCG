# judge.py

import requests
import json
from fastapi import APIRouter
from model import ToolInput
from pathlib import Path

# --- Judge Protocol Router ---
judge_router = APIRouter()
OLLAMA_URL = "http://host.docker.internal:11434/api/generate" 

def load_rules():
    rules_path = Path(__file__).parent / "rules.md"
    with open(rules_path, "r") as f:
        return f.read()

@judge_router.post("/tools/validate_move")
def validate_move(tool_input: ToolInput) -> dict:
    
    # --- KEY CHANGE: HYBRID LOGIC ---
    # 1. Handle simple, deterministic rules with Python first.
    bench_count = len(tool_input.game_state.player_battle_zone)

    # Rule #3 Check: Is the bench full?
    # This assumes playing a card adds a Pokémon. We can make this smarter later.
    if tool_input.proposed_action.action_type == "play_card":
        if bench_count >= 5:
            print("[Judge] Move invalidated by Python logic: Bench is full.")
            return {"result": "INVALID: The bench is full (5 Pokémon limit)."}

    # 2. If the move passes the simple checks, then ask the LLM for more complex validation.
    print("[Judge] Move passed initial Python checks. Forwarding to LLM...")
    
    rules = load_rules()
    known_cards = tool_input.game_state.player_hand

    prompt = f"""
    {rules}

    === Known Playable Cards ===
    The only cards currently in play are: {known_cards}

    === Current Game State ===
    - Player's Hand: {tool_input.game_state.player_hand}
    - Player's Battle Zone (Bench): {tool_input.game_state.player_battle_zone} (Current Count: {bench_count})
    - The current turn player is: {tool_input.game_state.turn_player.value}

    === Proposed Action ===
    - Action Type: {tool_input.proposed_action.action_type}
    - Card Name: {tool_input.proposed_action.card_name}

    Your Task: Examine the 'Proposed Action'. Does it break any of the 'Pokémon TCG Core Rules' listed above?
    - If the action breaks a rule, respond with 'INVALID:' and state the rule number that was broken.
    - If the action does not break any rules, respond with ONLY the single word 'VALID'.
    """
    
    print(f"[Judge] Sending prompt to LLM...")
    print(f"[Judge] Prompt: {prompt}")

    payload = {
        "model": "pokemon-judge",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120) 
        response.raise_for_status()
        llm_response_text = response.json().get("response", "").strip()
        print(f"[Judge] LLM responded: '{llm_response_text}'")
        return {"result": llm_response_text}
    except requests.exceptions.RequestException as e:
        print(f"[Judge] Error communicating with Ollama: {e}")
        return {"result": f"INVALID: Could not contact the game judge. Error: {e}"}