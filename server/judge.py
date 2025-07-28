# server/judge.py
import os
import re
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from enum import Enum
import json
# DODAJTE OVE IMPORTE
from typing import TypedDict, Annotated, Sequence
import operator

# LangChain & MCP Imports
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from server.model import ToolInput

# --- Definiranje stanja za naš LangGraph graf ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# --- Agent Management (Potpuno novo) ---
_agent_executor = None
_llm_with_tools = None # Poseban LLM za odabir alata
_final_answer_llm = None # Poseban LLM za konačni odgovor

async def initialize_agent():
    """Inicijalizira LangGraph agenta, alate i executor."""
    global _agent_executor, _llm_with_tools, _final_answer_llm
    print("Initializing Custom LangGraph Agent...")

    # 1. Spajanje na MCP server i dohvaćanje alata
    client = MultiServerMCPClient({"validator": {"transport": "streamable_http", "url": "http://localhost:8001/mcp"}})
    try:
        tools = await client.get_tools()
        tool_executor = ToolNode(tools)
        print(f"Successfully loaded tools: {[t.name for t in tools]}")
    except Exception as e:
        print(f"FATAL: Could not load tools. Error: {e}")
        return

    # 2. Kreiranje dva LLM-a
    # Jedan za pozivanje alata (zahtijeva JSON format)
    _llm_with_tools = ChatOllama(model="pokemon-judge:latest", temperature=0, base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"), format="json").bind_tools(tools)
    # Drugi za generiranje konačnog odgovora (običan tekst)
    _final_answer_llm = ChatOllama(model="pokemon-judge:latest", temperature=0, base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"))

    # 4. Definiranje logike grafa
    def should_continue(state: AgentState) -> str:
        """Odlučuje hoće li ponovno pozvati alate ili generirati konačni odgovor."""
        last_message = state['messages'][-1]
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return "end" # Ako nema poziva alata, idemo na konačni odgovor
        return "continue" # Inače, nastavi s izvršavanjem alata

    def call_model(state: AgentState):
        """Poziva LLM da odluči o sljedećem koraku (poziv alata)."""
        response = _llm_with_tools.invoke(state['messages'])
        return {"messages": [response]}
        
    def generate_final_answer(state: AgentState):
        """Generira konačni odgovor nakon što su alati izvršeni."""
        # Kreiramo novi prompt s cijelom povijesti, uključujući rezultate alata
        final_prompt = "Based on the preceding conversation and tool results, is the original move VALID or INVALID? Respond with only one of those two words, followed by a brief reason if invalid."
        final_state = state['messages'] + [HumanMessage(content=final_prompt)]
        
        response = _final_answer_llm.invoke(final_state)
        return {"messages": [response]}

    # 5. Kreiranje grafa
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_executor)
    workflow.add_node("final_answer", generate_final_answer) # Novi čvor
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": "final_answer" # Ako je kraj, idi na 'final_answer'
        }
    )
    workflow.add_edge("tools", "agent")
    workflow.add_edge("final_answer", END) # 'final_answer' je kraj grafa

    # 6. Kompajliranje grafa
    _agent_executor = workflow.compile()
    print("Custom LangGraph Agent with Final Answer node initialized successfully!")


def get_agent_executor():
    if not _agent_executor:
        raise HTTPException(status_code=503, detail="AI Agent is not available.")
    return _agent_executor

# --- Router ---
judge_router = APIRouter()

@judge_router.post("/tools/validate_move")
async def validate_move(
    tool_input: ToolInput,
    agent_executor = Depends(get_agent_executor)
) -> dict:
    action = tool_input.proposed_action
    state = tool_input.game_state
    
    # Novi, puno jednostavniji prompt!
    prompt = f"""
    A user wants to perform the action '{action.action_type}' with the card '{action.card_name}'.
    The current hand is {state.player_hand} and the bench is {state.player_bench}.
    First, call the necessary tools to check if the move is valid based on the game state.
    After the tools have been called, provide a final answer: either 'VALID' or 'INVALID: [reason]'.
    """
    
    print(f"[Judge] Invoking custom agent...")
    try:
        # Pozivamo naš kompajlirani graf
        response = await agent_executor.ainvoke({
            "messages": [HumanMessage(content=prompt)]
        })
        final_answer = response['messages'][-1].content
        print(f"[Judge] Agent responded: {final_answer}")
        return {"result": final_answer}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during agent execution: {e}")
