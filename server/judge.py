# server/judge.py
import os
import json
from fastapi import APIRouter, HTTPException, Depends
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from typing import Annotated

# Import tools directly
from server.tools import check_deck_size, check_hand_size, check_turn_rules, check_bench_rules
from server.model import ToolInput

# --- Global variables for the Agent ---
_agent_executor = None
_system_prompt = ""  # Store system prompt globally

# Create a simple prompt template for the React agent
REACT_PROMPT = PromptTemplate.from_template("""
{system_prompt}

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")

async def initialize_agent():
    """
    Initializes the LangGraph agent with Google Gemini as the LLM.
    """
    global _agent_executor, _system_prompt
    print("Initializing Agent with Google Gemini...")

    try:
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)

        # Load the system prompt from the modelfile
        modelfile_path = "server/judge.modelfile"
        with open(modelfile_path, "r") as f:
            content = f.read()
            # Extract content from SYSTEM block
            prompt_match = content.split('SYSTEM """', 1)
            if len(prompt_match) > 1:
                _system_prompt = prompt_match[1].split('"""')[0].strip()
            else:
                raise ValueError("Could not find a valid SYSTEM prompt in judge.modelfile.")
            print(f"System prompt loaded successfully")

        # Define the tools the agent can use - simpler tools that don't require complex inputs
        tools = [
            check_deck_size,
            check_hand_size,
            check_turn_rules,
            check_bench_rules,
        ]

        # Create the React agent with the custom prompt
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=REACT_PROMPT
        )
        
        # Create the agent executor
        _agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )
        
        print("Agent initialized successfully with Google Gemini!")

    except Exception as e:
        print(f"FATAL: Could not initialize agent. Error: {e}")
        _agent_executor = None

def get_agent_executor():
    """Dependency injector to get the initialized agent executor."""
    if not _agent_executor:
        raise HTTPException(status_code=503, detail="Agent is not available or failed to initialize.")
    return _agent_executor

# --- FastAPI Router ---
judge_router = APIRouter()

@judge_router.post("/tools/validate_setup")
async def validate_setup(
    tool_input: ToolInput,
    agent_executor: Annotated[AgentExecutor, Depends(get_agent_executor)]
) -> dict:
    """
    Validates initial setup by invoking the LangGraph agent.
    """
    action = tool_input.proposed_action
    state = tool_input.game_state

    # A clear and concise prompt for the agent
    prompt = f"""
    Validate the initial game setup for Pokemon TCG.
    
    Current setup data:
    - Player deck has {len(state.player_deck)} cards
    - Opponent deck has {len(state.opponent_deck)} cards  
    - Player hand has {len(state.player_hand)} cards
    - Opponent hand has {len(state.opponent_hand)} cards
    - Current turn count: {state.turn_count}
    - Player bench has {len(state.player_bench)} Pokemon
    - Opponent bench has {len(state.opponent_bench)} Pokemon
    
    Use the available tools to check the rules and determine if this setup is valid.
    Provide a final answer: either 'VALID' or 'INVALID: [specific reason]'.
    """

    print("[Judge] Invoking agent for setup validation...")
    
    try:
        # Invoke the agent
        response = await agent_executor.ainvoke({
            "input": prompt,
            "system_prompt": _system_prompt
        })
        
        # Extract the final answer
        final_answer = response.get("output", "INVALID: Agent failed to respond").strip()
            
        print(f"[Judge] Agent responded: {final_answer}")
        return {"result": final_answer}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during agent execution: {e}")
    
@judge_router.post("/tools/validate_move")
async def validate_move(
    tool_input: ToolInput,
    agent_executor: Annotated[AgentExecutor, Depends(get_agent_executor)]
) -> dict:
    """
    Validates a player's move by invoking the LangGraph agent.
    """
    action = tool_input.proposed_action
    state = tool_input.game_state

    # A clear and concise prompt for the agent
    prompt = f"""
    Validate this Pokemon TCG move.
    
    Move details:
    - Action: {action.action}
    - From: {action.source}
    - To: {action.target}
    - Context: {action.context}
    
    Current game state:
    - Turn player: {state.turn_player}
    - Player has {len(state.player_hand)} cards in hand
    - Player deck has {len(state.player_deck)} cards
    - Player bench has {len(state.player_bench)} Pokemon
    - Actions taken this turn: {state.actions_taken_this_turn}
    - Current turn: {state.turn_count}
    
    Use the available tools to check the rules and determine if this move is valid.
    Provide a final answer: either 'VALID' or 'INVALID: [specific reason]'.
    """

    print("[Judge] Invoking agent for move validation...")
    
    try:
        # Invoke the agent
        response = await agent_executor.ainvoke({
            "input": prompt,
            "system_prompt": _system_prompt
        })
        
        # Extract the final answer
        final_answer = response.get("output", "INVALID: Agent failed to respond").strip()
            
        print(f"[Judge] Agent responded: {final_answer}")
        return {"result": final_answer}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during agent execution: {e}")