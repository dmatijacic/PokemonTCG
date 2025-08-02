# backend/main.py
"""
Pokemon TCG LLM Education Platform - Enhanced Main FastAPI Server with GPT Integration
"""

# CRITICAL: Load environment FIRST before any other imports
import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file immediately
    print("✅ Environment variables loaded from .env")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment")

# Now check if OpenAI API key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
    print(f"🔑 OpenAI API Key loaded: {OPENAI_API_KEY[:15]}...{OPENAI_API_KEY[-4:]}")
    OPENAI_AVAILABLE = True
else:
    print("⚠️  OpenAI API Key not found - will run in demo mode")
    OPENAI_AVAILABLE = False

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import json
from typing import Dict, Any
import asyncio

# Add backend to Python path for imports
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

# Import Pokemon components
AI_COMPONENTS_LOADED = False
try:
    from src.models.pokemon_card import PokemonCard, CardCategory, PokemonType, Attack
    from src.models.game_state import PokemonGameState, PlayerState, PlayerType, GameAction, create_new_pokemon_game
    from src.ai_agents.opponent_ai import PokemonOpponentAI
    from src.game.type_advantages import PokemonTypeCalculator
    print("✅ Successfully imported Pokemon AI components")
    AI_COMPONENTS_LOADED = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import AI components: {e}")
    print("🔧 Running in demo mode without full AI")
    AI_COMPONENTS_LOADED = False

# Import OpenAI for real GPT integration
if OPENAI_AVAILABLE:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Test OpenAI connection
        test_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Pokemon AI Ready'"}],
            max_tokens=10
        )
        print(f"🤖 OpenAI GPT-4o-mini connected: {test_response.choices[0].message.content}")
        OPENAI_WORKING = True
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        OPENAI_WORKING = False
        openai_client = None
else:
    OPENAI_WORKING = False
    openai_client = None

# Initialize FastAPI app
app = FastAPI(
    title="Pokemon TCG LLM Education Platform",
    description="Teaching AI through Pokemon TCG gameplay with real GPT integration",
    version="1.0.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if frontend dist directory exists
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
    print("✅ Serving frontend assets from dist/")

# Global game sessions storage
active_sessions: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def get_pokemon_game():
    """Serve Pokemon TCG game interface"""
    if frontend_dist.exists() and (frontend_dist / "index.html").exists():
        with open("frontend/dist/index.html") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        ai_status = "🤖 Real GPT AI" if OPENAI_WORKING else "🎮 Demo Mode"
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pokemon TCG AI - Backend Running</title>
            <style>
                body{{font-family:Arial;margin:40px;background:#1a1a2e;color:white;text-align:center;}}
                .status{{background:#2a2a4e;padding:20px;border-radius:10px;margin:20px 0;}}
                .success{{background:#2a4e2a;}}
                .warning{{background:#4e4e2a;}}
                code{{background:#444;padding:2px 6px;border-radius:4px;}}
            </style>
        </head>
        <body>
            <h1>🎮 Pokemon TCG AI Education Platform</h1>
            <div class="status {'success' if OPENAI_WORKING else 'warning'}">
                <h2>Backend Server Running ✅</h2>
                <p><strong>AI Status:</strong> {ai_status}</p>
                <p><strong>OpenAI API:</strong> {'✅ Connected' if OPENAI_WORKING else '❌ Not Connected'}</p>
                <p><strong>Pokemon Components:</strong> {'✅ Loaded' if AI_COMPONENTS_LOADED else '⚠️ Demo Mode'}</p>
                <p><strong>WebSocket:</strong> /ws/pokemon-game/{{session_id}}</p>
            </div>
            
            <h3>🚀 Quick Start</h3>
            <p>1. Build frontend: <code>cd frontend && npm run build</code></p>
            <p>2. Or run dev server: <code>cd frontend && npm run dev</code></p>
            <p>3. Then visit: <a href="http://localhost:5173">http://localhost:5173</a></p>
            
            <div class="status">
                <h3>🤖 AI Features Available</h3>
                <ul style="text-align:left;display:inline-block;">
                    <li>{'✅' if OPENAI_WORKING else '⚠️'} Real GPT-4o-mini Pokemon AI opponent</li>
                    <li>✅ Pokemon type effectiveness calculations</li>
                    <li>✅ Strategic AI decision-making {'(GPT-powered)' if OPENAI_WORKING else '(Demo mode)'}</li>
                    <li>✅ Educational AI explanations</li>
                    <li>✅ Real-time game state management</li>
                    <li>✅ WebSocket communication with frontend</li>
                </ul>
            </div>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check for Pokemon game server"""
    return {
        "status": "healthy",
        "service": "pokemon-tcg-llm-education",
        "ai_components": AI_COMPONENTS_LOADED,
        "openai_available": OPENAI_AVAILABLE,
        "openai_working": OPENAI_WORKING,
        "active_sessions": len(active_sessions),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

async def get_gpt_pokemon_decision(game_state, ai_opponent) -> Dict[str, Any]:
    """Get real GPT-powered Pokemon AI decision"""
    if not OPENAI_WORKING:
        return None
    
    try:
        # Create detailed prompt for GPT
        my_pokemon = game_state.ai_player.active_pokemon
        opponent_pokemon = game_state.child_player.active_pokemon
        
        system_prompt = f"""You are a strategic Pokemon TCG AI opponent playing against a 9-year-old child.

Your role:
- Play Pokemon strategically but fairly
- Explain moves in simple, educational terms  
- Teach about type advantages through gameplay
- Be encouraging and show how AI thinks

Current situation:
- Your Pokemon: {my_pokemon.name if my_pokemon else 'None'} ({my_pokemon.hp if my_pokemon else 0} HP)
- Opponent Pokemon: {opponent_pokemon.name if opponent_pokemon else 'None'} ({opponent_pokemon.hp if opponent_pokemon else 0} HP)
- Turn: {game_state.turn_number}

Respond with JSON containing:
{{"action": "attack", "explanation": "Why you chose this move", "type_lesson": "Educational point about Pokemon types", "strategic_insight": "How AI thinks about this situation"}}"""

        user_prompt = game_state.get_game_summary_for_ai()

        # Get GPT response
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.8
        )
        
        gpt_text = response.choices[0].message.content
        
        # Calculate cost
        usage = response.usage
        cost = (usage.prompt_tokens * 0.00015 + usage.completion_tokens * 0.0006) / 1000
        
        print(f"🤖 GPT Pokemon Decision: {gpt_text[:100]}...")
        print(f"💰 Cost: ${cost:.6f}, Tokens: {usage.total_tokens}")
        
        # Parse JSON response
        try:
            if "{" in gpt_text and "}" in gpt_text:
                start = gpt_text.find("{")
                end = gpt_text.rfind("}") + 1
                json_str = gpt_text[start:end]
                decision = json.loads(json_str)
            else:
                # Fallback if no JSON
                decision = {
                    "action": "attack",
                    "explanation": gpt_text[:200],
                    "type_lesson": "🎓 AI analyzes multiple factors to make optimal decisions!",
                    "strategic_insight": "🎯 This demonstrates how AI processes information!"
                }
        except:
            decision = {
                "action": "attack", 
                "explanation": "AI is making a strategic Pokemon move!",
                "type_lesson": "🎓 AI considers type advantages when choosing moves!",
                "strategic_insight": "🎯 This shows how AI makes decisions!"
            }
        
        # Add metadata
        decision["gpt_used"] = True
        decision["gpt_cost"] = cost
        decision["gpt_tokens"] = usage.total_tokens
        
        return decision
        
    except Exception as e:
        print(f"❌ GPT decision error: {e}")
        return None

async def handle_ai_turn_simulation(session_id: str, websocket: WebSocket):
    """Handle AI turn simulation with real GPT when available"""
    
    # Send thinking status
    await websocket.send_text(json.dumps({
        "type": "ai_thinking_started",
        "message": f"🤖 {'GPT AI' if OPENAI_WORKING else 'Demo AI'} is analyzing Pokemon strategies..."
    }))
    
    # Simulate AI thinking time
    await asyncio.sleep(2)
    
    try:
        if session_id in active_sessions and active_sessions[session_id]["type"] == "full_ai":
            # Try to use real GPT
            session = active_sessions[session_id]
            game_state = session["game_state"]
            ai_opponent = session["ai_opponent"]
            
            # Try GPT first
            if OPENAI_WORKING:
                gpt_decision = await get_gpt_pokemon_decision(game_state, ai_opponent)
                if gpt_decision:
                    # Apply GPT decision to game state
                    apply_ai_decision_to_game_state(game_state, gpt_decision)
                    game_state.switch_turns()
                    
                    await websocket.send_text(json.dumps({
                        "type": "ai_decision_made",
                        "ai_decision": gpt_decision,
                        "game_state": serialize_game_state(game_state),
                        "educational_context": {
                            "type_lesson": gpt_decision.get("type_lesson"),
                            "strategic_insight": gpt_decision.get("strategic_insight"),
                            "ai_thinking": f"🤖 Real GPT AI analyzed this situation and chose strategically!"
                        },
                        "ai_type": "gpt"
                    }))
                    return
            
            # Fallback to base AI if GPT fails
            print("⚠️  Falling back to base AI logic")
            ai_decision = await ai_opponent.make_move(game_state)
            apply_ai_decision_to_game_state(game_state, ai_decision)
            game_state.switch_turns()
            
            await websocket.send_text(json.dumps({
                "type": "ai_decision_made",
                "ai_decision": ai_decision,
                "game_state": serialize_game_state(game_state),
                "educational_context": {
                    "type_lesson": ai_decision.get("type_lesson"),
                    "strategic_insight": ai_decision.get("strategic_insight"),
                    "ai_thinking": ai_decision.get("ai_thinking")
                },
                "ai_type": "base"
            }))
            
        else:
            # Demo mode
            demo_decision = {
                "action": "attack",
                "explanation": f"{'GPT' if OPENAI_WORKING else 'Demo'} AI chose Water Gun for type advantage!",
                "type_lesson": "🎓 Water beats Fire - Water attacks do 2x damage!",
                "strategic_insight": "🎯 AI calculated that type advantage gives the best chance of victory!",
                "ai_thinking": f"My {'GPT' if OPENAI_WORKING else 'demo'} AI analyzed type effectiveness!"
            }
            
            # Update demo state
            if session_id in active_sessions:
                demo_state = active_sessions[session_id]["demo_state"]
                child_pokemon = demo_state["child_player"]["active_pokemon"]
                if child_pokemon:
                    damage = 60  # Type advantage
                    child_pokemon["hp"] = max(0, child_pokemon["hp"] - damage)
                demo_state["current_turn"] = "child"
                demo_state["turn_number"] += 1
            
            await websocket.send_text(json.dumps({
                "type": "ai_decision_made",
                "ai_decision": demo_decision,
                "game_state": active_sessions[session_id]["demo_state"] if session_id in active_sessions else create_demo_game_state(session_id),
                "educational_context": {
                    "type_lesson": demo_decision["type_lesson"],
                    "strategic_insight": demo_decision["strategic_insight"],
                    "ai_thinking": demo_decision["ai_thinking"]
                },
                "ai_type": "demo"
            }))
            
    except Exception as e:
        print(f"❌ AI simulation error: {e}")
        await websocket.send_text(json.dumps({
            "type": "ai_error",
            "message": "AI encountered an error while thinking. Try again!",
            "error": str(e)
        }))

def create_demo_game_state(session_id: str) -> Dict[str, Any]:
    """Create demo game state when AI components aren't loaded"""
    return {
        "current_turn": "child",
        "turn_number": 1,
        "game_phase": "playing",
        "child_player": {
            "name": "Ash",
            "active_pokemon": {
                "id": "demo-charmander",
                "name": "Charmander",
                "hp": 50,
                "types": ["Fire"],
                "attacks": [
                    {"name": "Scratch", "damage": 10, "cost": ["Colorless"], "effect": ""},
                    {"name": "Ember", "damage": 30, "cost": ["Fire"], "effect": ""}
                ]
            },
            "benched_pokemon": [
                {
                    "id": "demo-bulbasaur",
                    "name": "Bulbasaur",
                    "hp": 50,
                    "types": ["Grass"],
                    "attacks": [{"name": "Tackle", "damage": 10, "cost": ["Colorless"], "effect": ""}]
                }
            ],
            "hand": [
                {
                    "id": "demo-pikachu",
                    "name": "Pikachu", 
                    "hp": 60,
                    "types": ["Electric"],
                    "attacks": [{"name": "Thunder Shock", "damage": 20, "cost": ["Electric"], "effect": ""}]
                }
            ],
            "prize_cards": 6
        },
        "ai_player": {
            "name": f"{'GPT' if OPENAI_WORKING else 'Demo'} Pokemon AI",
            "active_pokemon": {
                "id": "demo-squirtle", 
                "name": "Squirtle",
                "hp": 50,
                "types": ["Water"],
                "attacks": [
                    {"name": "Tackle", "damage": 10, "cost": ["Colorless"], "effect": ""},
                    {"name": "Water Gun", "damage": 30, "cost": ["Water"], "effect": ""}
                ]
            },
            "benched_pokemon": [
                {
                    "id": "demo-geodude",
                    "name": "Geodude",
                    "hp": 70, 
                    "types": ["Fighting"],
                    "attacks": [{"name": "Rock Throw", "damage": 20, "cost": ["Fighting"], "effect": ""}]
                }
            ],
            "hand_count": 7,
            "prize_cards": 6
        },
        "winner": None
    }

def apply_ai_decision_to_game_state(game_state, ai_decision):
    """Apply AI decision to the actual game state"""
    action = ai_decision.get("action")
    
    if action == "attack":
        child_pokemon = game_state.child_player.active_pokemon
        if child_pokemon and child_pokemon.hp:
            damage = 30  # Simplified damage
            child_pokemon.hp = max(0, child_pokemon.hp - damage)
    
    elif action == "switch":
        ai_bench = game_state.ai_player.benched_pokemon
        if ai_bench:
            new_active = ai_bench.pop(0)
            if game_state.ai_player.active_pokemon:
                ai_bench.append(game_state.ai_player.active_pokemon)
            game_state.ai_player.active_pokemon = new_active
    
    game_state.add_action(GameAction(
        player_id="ai",
        action_type=action,
        additional_data={"explanation": ai_decision.get("explanation")}
    ))

def serialize_game_state(game_state):
    """Convert game state to JSON-serializable format"""
    if not game_state:
        return create_demo_game_state("demo")
    
    return {
        "current_turn": game_state.current_turn.value,
        "turn_number": game_state.turn_number,
        "game_phase": game_state.game_phase.value,
        "child_player": serialize_player(game_state.child_player, hide_hand=False),
        "ai_player": serialize_player(game_state.ai_player, hide_hand=True),
        "winner": game_state.winner.value if game_state.winner else None
    }

def serialize_player(player, hide_hand=False):
    """Serialize player state"""
    return {
        "name": player.name,
        "active_pokemon": serialize_pokemon(player.active_pokemon),
        "benched_pokemon": [serialize_pokemon(p) for p in player.benched_pokemon],
        "hand": [serialize_pokemon(p) for p in player.hand] if not hide_hand else None,
        "hand_count": len(player.hand) if hide_hand else None,
        "prize_cards": player.prize_cards
    }

def serialize_pokemon(pokemon):
    """Serialize Pokemon card"""
    if not pokemon:
        return None
        
    return {
        "id": pokemon.id,
        "name": pokemon.name,
        "hp": pokemon.hp,
        "types": [t.value for t in pokemon.types] if hasattr(pokemon, 'types') and pokemon.types else [],
        "attacks": [
            {
                "name": attack.name,
                "damage": attack.get_damage_value() if hasattr(attack, 'get_damage_value') else getattr(attack, 'damage', 0),
                "cost": [str(c) for c in getattr(attack, 'cost', [])],
                "effect": getattr(attack, 'effect', "")
            }
            for attack in getattr(pokemon, 'attacks', [])
        ]
    }

# Additional handler functions would continue here...
# (Keeping the essential parts for space, but you'd include all the WebSocket handlers)

# @app.websocket("/ws/pokemon-game/{session_id}")
# async def pokemon_game_websocket(websocket: WebSocket, session_id: str):
#     """Enhanced WebSocket with real GPT integration"""
#     await websocket.accept()
#     print(f"🎮 Pokemon session {session_id} connected")
    
#     # Initialize session with GPT support
#     if AI_COMPONENTS_LOADED:
#         try:
#             game_state = create_new_pokemon_game(session_id, "Ash")
#             ai_opponent = PokemonOpponentAI(session_id, "Ash", "easy")
            
#             active_sessions[session_id] = {
#                 "websocket": websocket,
#                 "game_state": game_state,
#                 "ai_opponent": ai_opponent,
#                 "type": "full_ai"
#             }
            
#             ai_type = "🤖 Real GPT AI" if OPENAI_WORKING else "🎮 Strategic AI"
#             await websocket.send_text(json.dumps({
#                 "type": "game_state_update",
#                 "game_state": serialize_game_state(game_state),
#                 "message": f"Connected to {ai_type} system!"
#             }))
            
#         except Exception as e:
#             print(f"❌ Failed to initialize AI: {e}")
#             demo_state = create_demo_game_state(session_id)
#             active_sessions[session_id] = {
#                 "websocket": websocket,
#                 "demo_state": demo_state,
#                 "type": "demo"
#             }
#     else:
#         demo_state = create_demo_game_state(session_id)
#         active_sessions[session_id] = {
#             "websocket": websocket,
#             "demo_state": demo_state,
#             "type": "demo"
#         }
        
#         ai_type = "🤖 GPT Demo AI" if OPENAI_WORKING else "🎮 Demo AI"
#         await websocket.send_text(json.dumps({
#             "type": "game_state_update",
#             "game_state": demo_state,
#             "message": f"Connected to {ai_type} - basic Pokemon simulation ready!"
#         }))
    
#     try:
#         while True:
#             data = await websocket.receive_text()
#             message = json.loads(data)
#             message_type = message.get("type")
            
#             if message_type == "simulate_ai_turn":
#                 await handle_ai_turn_simulation(session_id, websocket)
#             # Add other message handlers here...
                
#     except WebSocketDisconnect:
#         print(f"🔌 Pokemon session {session_id} disconnected")
#         if session_id in active_sessions:
#             del active_sessions[session_id]
#     except Exception as e:
#         print(f"❌ Error in session {session_id}: {e}")
#         if session_id in active_sessions:
#             del active_sessions[session_id]

async def handle_player_action(session_id: str, websocket: WebSocket, message: Dict[str, Any]):
    """Handle player actions like draw card, attack, etc."""
    global AI_COMPONENTS_LOADED
    
    action_type = message.get("action_type")
    action_data = message.get("action_data", {})
    
    print(f"🎮 Player action: {action_type}")
    
    try:
        if session_id in active_sessions and active_sessions[session_id]["type"] == "full_ai":
            # Use real game state
            game_state = active_sessions[session_id]["game_state"]
            result = process_real_player_action(game_state, action_type, action_data)
            
            await websocket.send_text(json.dumps({
                "type": "player_action_result",
                "action_type": action_type,
                "result": result,
                "game_state": serialize_game_state(game_state)
            }))
            
        else:
            # Demo mode
            if session_id in active_sessions:
                demo_state = active_sessions[session_id]["demo_state"]
                result = process_demo_player_action(demo_state, action_type, action_data)
                
                await websocket.send_text(json.dumps({
                    "type": "player_action_result", 
                    "action_type": action_type,
                    "result": result,
                    "game_state": demo_state
                }))
            
        # Check if it's now AI's turn
        current_turn = None
        if session_id in active_sessions:
            session = active_sessions[session_id]
            if session["type"] == "full_ai":
                current_turn = session["game_state"].current_turn.value
            else:
                current_turn = session["demo_state"]["current_turn"]
            
        if current_turn == "ai":
            await websocket.send_text(json.dumps({
                "type": "ai_turn_ready",
                "message": "🤖 It's AI's turn now! Click 'Simulate AI Turn' to see what the AI does."
            }))
            
    except Exception as e:
        print(f"❌ Player action error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Action failed: {str(e)}"
        }))

def process_real_player_action(game_state, action_type: str, action_data: Dict):
    """Process player action with real game state"""
    if action_type == "draw_card":
        # Add a card to hand (simplified)
        if AI_COMPONENTS_LOADED:
            new_card = PokemonCard(
                id=f"drawn-{len(game_state.child_player.hand)}",
                name="Energy Card",
                category=CardCategory.ENERGY
            )
            game_state.child_player.hand.append(new_card)
            return {"message": "Drew an Energy card!", "card": "Energy Card"}
        else:
            return {"message": "Drew a card!", "card": "Mystery Card"}
    
    elif action_type == "attack":
        # Player attacks
        ai_pokemon = game_state.ai_player.active_pokemon
        if ai_pokemon and ai_pokemon.hp:
            damage = 25
            ai_pokemon.hp = max(0, ai_pokemon.hp - damage)
            game_state.switch_turns()
            return {"message": f"Dealt {damage} damage to {ai_pokemon.name}!", "damage": damage}
    
    elif action_type == "end_turn":
        game_state.switch_turns()
        return {"message": "Turn ended - AI's turn now!"}
    
    return {"message": f"Processed {action_type} action"}

def process_demo_player_action(demo_state: Dict, action_type: str, action_data: Dict):
    """Process player action in demo mode"""
    if action_type == "draw_card":
        # Simulate drawing a card
        new_card = {
            "id": f"drawn-{len(demo_state['child_player']['hand'])}",
            "name": "Potion",
            "hp": None,
            "types": [],
            "attacks": []
        }
        demo_state["child_player"]["hand"].append(new_card)
        return {"message": "Drew a Potion card!", "card": "Potion"}
    
    elif action_type == "attack":
        # Player attacks AI
        ai_pokemon = demo_state["ai_player"]["active_pokemon"]
        if ai_pokemon:
            damage = 20
            ai_pokemon["hp"] = max(0, ai_pokemon["hp"] - damage)
            demo_state["current_turn"] = "ai"
            return {"message": f"Dealt {damage} damage to {ai_pokemon['name']}!", "damage": damage}
    
    elif action_type == "end_turn":
        demo_state["current_turn"] = "ai"
        return {"message": "Turn ended - AI's turn now!"}
    
    return {"message": f"Processed {action_type} action"}

# Now update the WebSocket handler to include all message types
@app.websocket("/ws/pokemon-game/{session_id}")
async def pokemon_game_websocket(websocket: WebSocket, session_id: str):
    """Enhanced WebSocket with real GPT integration and complete message handling"""
    await websocket.accept()
    print(f"🎮 Pokemon session {session_id} connected")
    
    # Initialize session with GPT support
    if AI_COMPONENTS_LOADED:
        try:
            game_state = create_new_pokemon_game(session_id, "Ash")
            ai_opponent = PokemonOpponentAI(session_id, "Ash", "easy")
            
            active_sessions[session_id] = {
                "websocket": websocket,
                "game_state": game_state,
                "ai_opponent": ai_opponent,
                "type": "full_ai"
            }
            
            ai_type = "🤖 Real GPT AI" if OPENAI_WORKING else "🎮 Strategic AI"
            await websocket.send_text(json.dumps({
                "type": "game_state_update",
                "game_state": serialize_game_state(game_state),
                "message": f"Connected to {ai_type} system!"
            }))
            
        except Exception as e:
            print(f"❌ Failed to initialize AI: {e}")
            demo_state = create_demo_game_state(session_id)
            active_sessions[session_id] = {
                "websocket": websocket,
                "demo_state": demo_state,
                "type": "demo"
            }
    else:
        demo_state = create_demo_game_state(session_id)
        active_sessions[session_id] = {
            "websocket": websocket,
            "demo_state": demo_state,
            "type": "demo"
        }
        
        ai_type = "🤖 GPT Demo AI" if OPENAI_WORKING else "🎮 Demo AI"
        await websocket.send_text(json.dumps({
            "type": "game_state_update",
            "game_state": demo_state,
            "message": f"Connected to {ai_type} - basic Pokemon simulation ready!"
        }))
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message_type = message.get("type")
            
            print(f"📥 Received: {message_type}")
            
            # Route messages to appropriate handlers
            if message_type == "simulate_ai_turn":
                await handle_ai_turn_simulation(session_id, websocket)
                
            elif message_type == "player_action":
                await handle_player_action(session_id, websocket, message)
                
            elif message_type == "get_game_state":
                # Send current game state
                if session_id in active_sessions:
                    session = active_sessions[session_id]
                    if session["type"] == "full_ai":
                        game_state = serialize_game_state(session["game_state"])
                    else:
                        game_state = session["demo_state"]
                    
                    await websocket.send_text(json.dumps({
                        "type": "game_state_update",
                        "game_state": game_state
                    }))
                    
            elif message_type == "reset_game":
                # Reset game
                if session_id in active_sessions and active_sessions[session_id]["type"] == "full_ai":
                    try:
                        new_game_state = create_new_pokemon_game(session_id, "Ash")
                        active_sessions[session_id]["game_state"] = new_game_state
                        game_state = serialize_game_state(new_game_state)
                    except Exception as e:
                        print(f"❌ Error resetting AI game: {e}")
                        demo_state = create_demo_game_state(session_id)
                        active_sessions[session_id] = {
                            "websocket": websocket,
                            "demo_state": demo_state,
                            "type": "demo"
                        }
                        game_state = demo_state
                else:
                    demo_state = create_demo_game_state(session_id)
                    if session_id in active_sessions:
                        active_sessions[session_id]["demo_state"] = demo_state
                        game_state = demo_state
                    else:
                        game_state = demo_state
                
                await websocket.send_text(json.dumps({
                    "type": "game_reset",
                    "message": "🔄 New Pokemon battle started!",
                    "game_state": game_state
                }))
                
            elif message_type == "get_type_advice":
                # Handle type effectiveness advice
                attacking_type = message.get("attacking_type")
                defending_type = message.get("defending_type")
                
                if attacking_type and defending_type:
                    try:
                        if AI_COMPONENTS_LOADED:
                            from src.game.type_advantages import PokemonTypeCalculator
                            from src.models.pokemon_card import PokemonType
                            
                            calc = PokemonTypeCalculator()
                            attack_type_enum = PokemonType(attacking_type.lower())
                            defend_type_enum = PokemonType(defending_type.lower())
                            
                            effectiveness = calc.get_effectiveness(attack_type_enum, defend_type_enum)
                            explanation = calc.get_ai_explanation(attack_type_enum, defend_type_enum)
                        else:
                            # Demo mode type advice
                            effectiveness = 1.0
                            explanation = f"{attacking_type} vs {defending_type}: Demo calculation shows normal effectiveness"
                        
                        await websocket.send_text(json.dumps({
                            "type": "type_advice",
                            "attacking_type": attacking_type,
                            "defending_type": defending_type,
                            "effectiveness": effectiveness,
                            "explanation": explanation
                        }))
                        
                    except Exception as e:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": f"Type advice error: {str(e)}"
                        }))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Missing type information for advice"
                    }))
                
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }))
                
    except WebSocketDisconnect:
        print(f"🔌 Pokemon session {session_id} disconnected")
        if session_id in active_sessions:
            del active_sessions[session_id]
    except Exception as e:
        print(f"❌ Error in session {session_id}: {e}")
        if session_id in active_sessions:
            del active_sessions[session_id]

if __name__ == "__main__":
    print("🎮 Starting Pokemon TCG AI Education Platform...")
    print(f"🤖 AI Status: {'Real GPT-4o-mini' if OPENAI_WORKING else 'Demo Mode'}")
    print(f"🔑 OpenAI API: {'✅ Connected' if OPENAI_WORKING else '❌ Not Available'}")
    print("🌐 Server will be available at: http://localhost:8000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT", "development") == "development" else False,
        log_level="info"
    )