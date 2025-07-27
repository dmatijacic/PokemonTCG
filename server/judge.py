# server/judge.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
from contextlib import asynccontextmanager

# Novi importi za agenta!
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

# --- Modeli ostaju isti ---
class Player(str, Enum):
    PLAYER = "player"
    OPPONENT = "opponent"

class GameState(BaseModel):
    player_hand: list[str] = []
    player_battle_zone: list[str] = []
    turn_player: Player

class ProposedAction(BaseModel):
    action_type: str
    card_name: str | None = None

class ToolInput(BaseModel):
    game_state: GameState
    proposed_action: ProposedAction

# --- Globalni Agent ---
# Kreiramo globalnu varijablu za našeg agenta
# Inicijalizirat će se pri pokretanju servera
agent_executor = None

@asynccontextmanager
async def lifespan(app: APIRouter):
    # ...
    print("Initializing AI Agent...")
    
    client = MultiServerMCPClient({
        "validator": {
            "transport": "streamable_http",
            # ISPRAVAK: Uklonite /mcp/ s kraja URL-a
            "url": "http://localhost:8001/mcp", 
        }
    })

    try:
        tools = await client.get_tools()
        print(f"Successfully loaded tools from MCP server: {[tool.name for tool in tools]}")
    except Exception as e:
        print(f"FATAL: Could not connect to MCP server. Is it running? Error: {e}")
        tools = []
    

    # 3. Kreiranje LLM-a
    # Za lokalni model, koristili bismo ChatOllama, ali za primjer koristimo OpenAI
    # jer je standard za ReAct agente.
    # llm = ChatOllama(model="pokemon-judge:latest")
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    agent_executor = create_react_agent(llm, tools)
    print("AI Agent initialized successfully!")
    yield
    print("Shutting down AI Agent.")


judge_router = APIRouter(lifespan=lifespan)

@judge_router.post("/tools/validate_move")
async def validate_move(tool_input: ToolInput) -> dict:
    """
    Validira potez tako što pita AI agenta za odluku.
    Agent sam odlučuje koje alate treba pozvati.
    """
    if not agent_executor:
        raise HTTPException(status_code=503, detail="AI Agent is not available.")

    # Formatiramo upit za agenta
    action = tool_input.proposed_action
    state = tool_input.game_state
    
    prompt = f"""
    The user wants to perform the action '{action.action_type}' with the card '{action.card_name}'.
    The current game state is:
    - Hand: {state.player_hand}
    - Bench: {state.player_battle_zone}

    Use your available tools to check if the move is valid. If all tool checks pass,
    then use your knowledge of Pokémon TCG rules to make a final decision.
    Respond with only 'VALID' or 'INVALID: [reason]'.
    """
    
    print(f"[Judge] Invoking agent with prompt:\n{prompt}")

    try:
        # Pozivamo agenta da obradi upit
        response = await agent_executor.ainvoke({
            "messages": [HumanMessage(content=prompt)]
        })
        
        # Formatiramo odgovor
        # ReAct agenti imaju izlaz u 'messages' listi, zadnja poruka je odgovor
        final_answer = response['messages'][-1].content
        print(f"[Judge] Agent responded: {final_answer}")
        return {"result": final_answer}

    except Exception as e:
        print(f"Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail="Error during agent execution.")