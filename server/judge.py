# server/judge.py
import os
import json
from fastapi import APIRouter, HTTPException, Depends
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated

# Import tools directly
from server.tools import is_card_in_hand, is_first_action_of_turn, is_bench_full, deck_size
from server.model import ToolInput

# --- Global variables for the Agent ---
_agent_executor = None
_system_prompt = ""  # Store system prompt globally

async def initialize_agent():
    """
    Initializes the LangGraph agent with Google Gemini as the LLM.
    This function is now fully asynchronous and uses the correct agent creation method.
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
            print(f"System prompt loaded: {_system_prompt}")

        # Define the tools the agent can use
        tools = [
            is_card_in_hand,
            is_first_action_of_turn,
            is_bench_full,
            deck_size,
        ]

        # Create the agent executor (Corrected: without messages_modifier)
        _agent_executor = create_react_agent(llm, tools)
        
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
    agent_executor: Annotated[dict, Depends(get_agent_executor)]
) -> dict:
    """
    Validates initial setup by invoking the LangGraph agent.
    """
    action = tool_input.proposed_action
    state = tool_input.game_state

    # A clear and concise prompt for the agent
    prompt = f"""
    The user wants to validate setup.
    Use the available tools to check if initail configuration is valid according to the game rules.
    After using the tools, provide a final answer: either 'VALID' or 'INVALID: [reason]'.

    The current game state is:
    {json.dumps(state.model_dump(), indent=2)}
    """

    print("[Judge] Invoking agent...")
    print(f"[Judge] Prompt: {prompt}")
    try:
        # Invoke the agent, passing the system prompt with the user message
        response = await agent_executor.ainvoke({
            "messages": [
                SystemMessage(content=_system_prompt),
                HumanMessage(content=prompt)
            ]
        })
        final_answer = response['messages'][-1].content.strip()
        print(f"[Judge] Agent responded: {final_answer}")
        return {"result": final_answer}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during agent execution: {e}")
    
@judge_router.post("/tools/validate_move")
async def validate_move(
    tool_input: ToolInput,
    agent_executor: Annotated[dict, Depends(get_agent_executor)]
) -> dict:
    """
    Validates a player's move by invoking the LangGraph agent.
    """
    action = tool_input.proposed_action
    state = tool_input.game_state

    # A clear and concise prompt for the agent
    prompt = f"""
    The user wants to '{action.action}' on context '{action.context}' from '{action.source}' to '{action.target}'.
    Use the available tools to check if this move is valid according to the game rules.
    After using the tools, provide a final answer: either 'VALID' or 'INVALID: [reason]'.

    The current game state is:
    {json.dumps(state.model_dump(), indent=2)}
    """

    print("[Judge] Invoking agent...")
    print(f"[Judge] Prompt: {prompt}")
    try:
        # Invoke the agent, passing the system prompt with the user message
        response = await agent_executor.ainvoke({
            "messages": [
                SystemMessage(content=_system_prompt),
                HumanMessage(content=prompt)
            ]
        })
        final_answer = response['messages'][-1].content.strip()
        print(f"[Judge] Agent responded: {final_answer}")
        return {"result": final_answer}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during agent execution: {e}")

