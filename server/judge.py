# server/judge.py
import os
import json
import textwrap
import traceback # <-- 1. IMPORT TRACEBACK
from fastapi import APIRouter, HTTPException, Depends
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts.chat import HumanMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from typing import Annotated

# Import your tools and models
from .tools import tools
from .model import ToolInput, ValidationResult

# --- Global Agent Executor ---
# This will be initialized on startup
_agent_executor = None

# 2. RESTRUCTURE INITIALIZATION
# This is now a standalone async function to be called by the lifespan manager
async def initialize_agent():
    global _agent_executor
    print("Initializing Agent with Google Gemini...")

    try:
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)
        structured_llm = llm.with_structured_output(ValidationResult)

        # --- Load SYSTEM prompt from judge.modelfile
        with open("server/judge.modelfile", "r") as f:
            content = f.read()
            prompt_match = content.split('SYSTEM """', 1)
            if len(prompt_match) > 1:
                _system_prompt = prompt_match[1].split('"""')[0].strip()
            else:
                raise ValueError("Could not find a valid SYSTEM prompt in judge.modelfile.")

        # --- USER prompt: define tool format and injection points
        user_prompt_template = """
        TOOLS
        ------
        You have access to the following tools:
        {tools}

        To use a tool, please use the following format:
        ```
        Thought: Do I need to use a tool? Yes
        Action: the action to take. Should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ```

        When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
        ```
        Thought: Do I need to use a tool? No
        Final Answer: [your response here]
        ```

        Begin!
        Question: {input}
        """

        user_prompt = HumanMessagePromptTemplate(
            prompt=PromptTemplate.from_template(user_prompt_template)
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", _system_prompt),
            user_prompt,
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # --- Create the ReAct agent
        agent = create_react_agent(structured_llm, tools, prompt)
        _agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        print("Structured agent initialized successfully with Google Gemini!")

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
    """ Validates initial setup by invoking the agent. """
    state = tool_input.game_state

    prompt_input = (
        "Check if initial configuration is valid according to the game rules.\n"
        f"The current game state is:\n{json.dumps(state.model_dump())}"
    )

    print(f"[Judge] Invoking agent for setup validation...")
    try:
        response = await agent_executor.ainvoke({
            "input": prompt_input,
            "tools": tools,
            "tool_names": [t.name for t in tools]
        })
        validation_result = response  # Already a ValidationResult instance
        print(f"[Judge] Agent responded: {validation_result}")
        return validation_result.model_dump()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during agent execution: {e}")
    
@judge_router.post("/tools/validate_move")
async def validate_move(
    tool_input: ToolInput,
    agent_executor: Annotated[AgentExecutor, Depends(get_agent_executor)]
) -> dict:
    """ Validates a player's move by invoking the agent. """
    action = tool_input.proposed_action
    state = tool_input.game_state
    prompt = f"The user wants to '{action.action}' on context '{action.context}' from '{action.source}' to '{action.target}'. Use tools to validate this move against the game state:\n{json.dumps(state.model_dump())}"

    print(f"[Judge] Invoking agent for move validation...")
    try:
        response = await agent_executor.ainvoke({"input": prompt, "agent_scratchpad": []})
        validation_result = response['output']
        print(f"[Judge] Agent responded: {validation_result}")
        return validation_result.model_dump()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during agent execution: {e}")
