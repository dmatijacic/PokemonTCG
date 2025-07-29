# src/monitoring/pokemon_cost_tracker.py
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import asyncio
from langfuse import Langfuse

@dataclass
class PokemonCostEntry:
    timestamp: datetime
    agent_role: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    environment: str
    pokemon_context: str  # What Pokemon situation triggered this AI call
    game_session_id: str

class PokemonCostTracker:
    """
    Real-time cost tracking and budget management for Pokemon AI agents
    """
    
    def __init__(self):
        self.langfuse = Langfuse()
        self.daily_budget = {
            "development": 3.00,  # $3/day during Pokemon AI development
            "production": 8.00    # $8/day when child plays Pokemon with AI
        }
        self.pokemon_cost_entries: List[PokemonCostEntry] = []
        
    async def track_pokemon_usage(self, session_id: str, environment: str) -> Dict:
        """Get real-time Pokemon AI usage from Langfuse"""
        try:
            # Get Pokemon game traces from last 24 hours
            traces = self.langfuse.get_traces(
                session_id=f"pokemon_game_{session_id}",
                from_timestamp=datetime.now() - timedelta(hours=24)
            )
            
            daily_cost = 0
            pokemon_usage_by_agent = {}
            pokemon_games_played = 0
            
            for trace in traces:
                if hasattr(trace, 'usage') and trace.usage:
                    # Calculate cost based on model and tokens
                    agent_role = trace.metadata.get('agent_role', 'unknown')
                    model = trace.metadata.get('model', 'unknown')
                    game_type = trace.metadata.get('game_type', 'unknown')
                    
                    # Only count Pokemon-related AI usage
                    if game_type != 'pokemon_tcg':
                        continue
                    
                    input_tokens = trace.usage.input or 0
                    output_tokens = trace.usage.output or 0
                    
                    # Get cost rates for Pokemon AI
                    cost = self._calculate_pokemon_cost(model, input_tokens, output_tokens)
                    daily_cost += cost
                    
                    if agent_role not in pokemon_usage_by_agent:
                        pokemon_usage_by_agent[agent_role] = {
                            'calls': 0, 'tokens': 0, 'cost': 0, 'pokemon_decisions': []
                        }
                    
                    pokemon_usage_by_agent[agent_role]['calls'] += 1
                    pokemon_usage_by_agent[agent_role]['tokens'] += input_tokens + output_tokens
                    pokemon_usage_by_agent[agent_role]['cost'] += cost
                    
                    # Track Pokemon-specific decisions
                    if hasattr(trace, 'name') and 'pokemon' in trace.name.lower():
                        pokemon_usage_by_agent[agent_role]['pokemon_decisions'].append({
                            'timestamp': trace.timestamp,
                            'decision_type': trace.name,
                            'cost': cost
                        })
            
            # Count unique Pokemon game sessions
            pokemon_games_played = len(set(
                trace.session_id for trace in traces 
                if trace.metadata.get('game_type') == 'pokemon_tcg'
            ))
            
            return {
                'daily_cost': daily_cost,
                'budget_remaining': self.daily_budget[environment] - daily_cost,
                'pokemon_usage_by_agent': pokemon_usage_by_agent,
                'budget_used_percent': (daily_cost / self.daily_budget[environment]) * 100,
                'pokemon_games_played': pokemon_games_played,
                'average_cost_per_game': daily_cost / max(pokemon_games_played, 1),
                'environment': environment
            }
            
        except Exception as e:
            print(f"Error tracking Pokemon AI usage: {e}")
            return {'error': str(e)}
    
    def _calculate_pokemon_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on model pricing for Pokemon AI"""
        pricing = {
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
            'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125}
        }
        
        if model not in pricing:
            return 0.001 * (input_tokens + output_tokens) / 1000  # Fallback estimate
        
        rates = pricing[model]
        input_cost = (input_tokens / 1000) * rates['input']
        output_cost = (output_tokens / 1000) * rates['output']
        
        return input_cost + output_cost
    
    async def check_pokemon_budget_alert(self, environment: str, session_id: str) -> Optional[str]:
        """Check if approaching budget limits during Pokemon gameplay"""
        usage = await self.track_pokemon_usage(session_id, environment)
        
        if 'error' in usage:
            return None
            
        budget_percent = usage.get('budget_used_percent', 0)
        games_played = usage.get('pokemon_games_played', 0)
        
        if budget_percent > 90:
            return f"🚨 POKEMON AI BUDGET ALERT: {budget_percent:.1f}% used! ({games_played} Pokemon games played today)"
        elif budget_percent > 75:
            return f"⚡ Pokemon AI budget notice: {budget_percent:.1f}% used after {games_played} games"
        elif games_played >= 10:  # High usage warning regardless of cost
            return f"🎮 Lots of Pokemon battles today! {games_played} games played (${usage.get('daily_cost', 0):.2f} spent)"
        
        return None
    
    def generate_pokemon_cost_report(self, usage_data: Dict) -> str:
        """Generate a detailed Pokemon AI cost report"""
        if 'error' in usage_data:
            return f"Error generating Pokemon cost report: {usage_data['error']}"
        
        report = ["=== POKEMON AI COST REPORT ==="]
        report.append(f"Environment: {usage_data.get('environment', 'unknown')}")
        report.append(f"Pokemon Games Played: {usage_data.get('pokemon_games_played', 0)}")
        report.append(f"Total Daily Cost: ${usage_data.get('daily_cost', 0):.4f}")
        report.append(f"Average Cost per Pokemon Game: ${usage_data.get('average_cost_per_game', 0):.4f}")
        report.append(f"Budget Used: {usage_data.get('budget_used_percent', 0):.1f}%")
        report.append(f"Budget Remaining: ${usage_data.get('budget_remaining', 0):.4f}")
        report.append("")
        
        # Pokemon AI agent breakdown
        report.append("Pokemon AI Agent Usage:")
        pokemon_agents = usage_data.get('pokemon_usage_by_agent', {})
        
        for agent_role, agent_data in pokemon_agents.items():
            report.append(f"  {agent_role}:")
            report.append(f"    Calls: {agent_data.get('calls', 0)}")
            report.append(f"    Tokens: {agent_data.get('tokens', 0):,}")
            report.append(f"    Cost: ${agent_data.get('cost', 0):.4f}")
            
            # Recent Pokemon decisions
            decisions = agent_data.get('pokemon_decisions', [])
            if decisions:
                report.append(f"    Recent Pokemon Decisions: {len(decisions)}")
                for decision in decisions[-3:]:  # Last 3 decisions
                    report.append(f"      - {decision['decision_type']} (${decision['cost']:.4f})")
        
        return "\n".join(report)

# src/server/pokemon_environment_manager.py
import os
from typing import Dict, Any
from ..monitoring.pokemon_cost_tracker import PokemonCostTracker

class PokemonEnvironmentManager:
    """
    Manages switching between development and production configurations for Pokemon AI
    """
    
    def __init__(self):
        self.pokemon_cost_tracker = PokemonCostTracker()
        
    def get_current_pokemon_environment(self) -> str:
        """Get current Pokemon AI environment setting"""
        return os.getenv("ENVIRONMENT", "development").lower()
    
    async def switch_pokemon_environment(self, new_env: str, session_id: str) -> Dict[str, Any]:
        """
        Switch between development and production environments for Pokemon AI
        """
        if new_env not in ["development", "production"]:
            return {"error": "Environment must be 'development' or 'production' for Pokemon AI"}
        
        # Check current Pokemon AI usage before switching
        current_env = self.get_current_pokemon_environment()
        usage = await self.pokemon_cost_tracker.track_pokemon_usage(session_id, current_env)
        
        # Set new environment
        os.environ["ENVIRONMENT"] = new_env
        
        return {
            "previous_environment": current_env,
            "new_environment": new_env,
            "previous_pokemon_usage": usage,
            "message": f"Switched Pokemon AI to {new_env} environment",
            "cost_impact": self._get_cost_impact_message(current_env, new_env)
        }
    
    def get_pokemon_environment_info(self) -> Dict[str, Any]:
        """Get information about current Pokemon AI environment"""
        current_env = self.get_current_pokemon_environment()
        
        return {
            "current_environment": current_env,
            "pokemon_models_in_use": self._get_pokemon_models_for_env(current_env),
            "daily_budget": self.pokemon_cost_tracker.daily_budget[current_env],
            "cost_optimization": "maximum" if current_env == "development" else "balanced",
            "pokemon_ai_focus": "development_testing" if current_env == "development" else "child_education"
        }
    
    def _get_pokemon_models_for_env(self, environment: str) -> Dict[str, str]:
        """Get Pokemon AI model mapping for environment"""
        if environment == "development":
            return {
                "pokemon_opponent": "gpt-3.5-turbo",
                "pokemon_teacher": "gpt-3.5-turbo", 
                "pokemon_helper": "gpt-3.5-turbo",
                "pokemon_judge": "gpt-3.5-turbo"
            }
        else:
            return {
                "pokemon_opponent": "claude-3-haiku-20240307",
                "pokemon_teacher": "claude-3-haiku-20240307",
                "pokemon_helper": "gpt-4o-mini", 
                "pokemon_judge": "claude-3-haiku-20240307"
            }
    
    def _get_cost_impact_message(self, old_env: str, new_env: str) -> str:
        """Generate message about cost impact of environment switch"""
        if old_env == "development" and new_env == "production":
            return "Switched to higher-quality Pokemon AI models. Cost will increase but Pokemon gameplay will be more educational."
        elif old_env == "production" and new_env == "development":
            return "Switched to cost-optimized Pokemon AI models. Lower cost but simpler Pokemon AI responses."
        else:
            return "No environment change detected."

# FastAPI endpoints for Pokemon environment management
from fastapi import APIRouter, HTTPException
from ..server.pokemon_environment_manager import PokemonEnvironmentManager

pokemon_env_router = APIRouter(prefix="/pokemon/environment", tags=["pokemon-environment"])
pokemon_env_manager = PokemonEnvironmentManager()

@pokemon_env_router.get("/status")
async def get_pokemon_environment_status():
    """Get current Pokemon AI environment configuration"""
    return pokemon_env_manager.get_pokemon_environment_info()

@pokemon_env_router.post("/switch/{new_env}")
async def switch_pokemon_environment(new_env: str, session_id: str = "default_pokemon_session"):
    """Switch between development and production environments for Pokemon AI"""
    if new_env not in ["development", "production"]:
        raise HTTPException(status_code=400, detail="Environment must be 'development' or 'production'")
    
    return await pokemon_env_manager.switch_pokemon_environment(new_env, session_id)

@pokemon_env_router.get("/cost/usage/{session_id}")
async def get_pokemon_cost_usage(session_id: str):
    """Get real-time Pokemon AI cost usage"""
    environment = pokemon_env_manager.get_current_pokemon_environment()
    usage = await pokemon_env_manager.pokemon_cost_tracker.track_pokemon_usage(session_id, environment)
    
    if 'error' in usage:
        raise HTTPException(status_code=500, detail=usage['error'])
    
    return usage

@pokemon_env_router.get("/cost/report/{session_id}")
async def get_pokemon_cost_report(session_id: str):
    """Get detailed Pokemon AI cost report"""
    environment = pokemon_env_manager.get_current_pokemon_environment()
    usage = await pokemon_env_manager.pokemon_cost_tracker.track_pokemon_usage(session_id, environment)
    
    if 'error' in usage:
        raise HTTPException(status_code=500, detail=usage['error'])
    
    report = pokemon_env_manager.pokemon_cost_tracker.generate_pokemon_cost_report(usage)
    
    return {
        "session_id": session_id,
        "environment": environment,
        "report": report,
        "raw_data": usage
    }

@pokemon_env_router.get("/cost/alert/{session_id}")
async def check_pokemon_budget_alert(session_id: str):
    """Check for Pokemon AI budget alerts"""
    environment = pokemon_env_manager.get_current_pokemon_environment()
    alert = await pokemon_env_manager.pokemon_cost_tracker.check_pokemon_budget_alert(environment, session_id)
    
    return {
        "alert": alert,
        "has_alert": alert is not None,
        "environment": environment,
        "session_id": session_id
    }

# CLI utility for quick Pokemon environment switching
if __name__ == "__main__":
    import sys
    import asyncio
    
    async def main():
        if len(sys.argv) > 1:
            env = sys.argv[1]
            session = sys.argv[2] if len(sys.argv) > 2 else "cli_pokemon_session"
            
            manager = PokemonEnvironmentManager()
            result = await manager.switch_pokemon_environment(env, session)
            
            print(f"Pokemon AI Environment Switch Result:")
            print(f"  Previous: {result['previous_environment']}")
            print(f"  New: {result['new_environment']}")
            print(f"  Message: {result['message']}")
            print(f"  Cost Impact: {result['cost_impact']}")
            
            if 'previous_pokemon_usage' in result:
                usage = result['previous_pokemon_usage']
                if 'error' not in usage:
                    print(f"  Previous Usage: {usage['pokemon_games_played']} games, ${usage['daily_cost']:.4f}")
        else:
            print("Usage: python pokemon_environment_manager.py [development|production] [session_id]")
            print("Example: python pokemon_environment_manager.py production ash_first_game")
    
    asyncio.run(main())