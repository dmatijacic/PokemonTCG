# backend/src/ai_agents/base_pokemon_agent.py
"""
Base Pokemon Agent - Foundation for all Pokemon-playing AI agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add the models path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.pokemon_card import PokemonCard
from models.game_state import PokemonGameState

class BasePokemonAgent(ABC):
    """
    Base class for all Pokemon-playing AI agents
    """
    
    def __init__(self, agent_role: str, game_session_id: str = None, child_name: str = "trainer"):
        self.agent_role = agent_role
        self.game_session_id = game_session_id
        self.child_name = child_name
        self.conversation_history = []
        
        # Initialize model factory (placeholder for now)
        self.model_factory = MockModelFactory()
        
    @abstractmethod
    def get_pokemon_system_prompt(self) -> str:
        """Define the agent's Pokemon personality and role"""
        pass
    
    def get_pokemon_knowledge_context(self) -> str:
        """Basic Pokemon knowledge for all agents"""
        return """
        POKEMON TYPE EFFECTIVENESS (Key for AI Strategy):
        Super Effective (2x damage):
        - Fire > Grass, Bug, Steel, Ice
        - Water > Fire, Ground, Rock  
        - Electric > Water, Flying
        - Grass > Water, Ground, Rock
        - Ice > Grass, Ground, Flying, Dragon
        - Fighting > Normal, Rock, Steel, Ice, Dark
        
        Not Very Effective (0.5x damage):
        - Fire < Water, Ground, Rock
        - Water < Grass, Electric
        - Electric < Ground (0x), Grass
        - Grass < Fire, Ice, Poison, Flying, Bug
        
        POKEMON BATTLE BASICS:
        - Each Pokemon has HP (health points)
        - Attacks require energy cards
        - Weakness doubles damage taken
        - Resistance reduces damage taken
        - Knocked out Pokemon go to discard pile
        - Win by taking all prize cards or opponent has no Pokemon
        """
    
    async def respond_to_pokemon_situation(self, situation: str, game_state: Optional[PokemonGameState] = None) -> str:
        """Generate response to Pokemon game situation"""
        # For now, return a simple response
        # In full implementation, this would use LLM
        return f"AI {self.agent_role} analyzing situation: {situation}"
    
    def analyze_pokemon_matchup(self, my_pokemon: PokemonCard, opponent_pokemon: PokemonCard) -> Dict[str, Any]:
        """Analyze matchup between two Pokemon"""
        if not (my_pokemon and opponent_pokemon):
            return {"advantage": "unknown", "explanation": "Missing Pokemon data"}
        
        # Simple type advantage analysis
        my_types = my_pokemon.types
        opponent_types = opponent_pokemon.types
        
        if not (my_types and opponent_types):
            return {"advantage": "neutral", "explanation": "No type information available"}
        
        # Basic type effectiveness (simplified)
        type_chart = {
            "fire": {"grass": 2, "water": 0.5},
            "water": {"fire": 2, "grass": 0.5}, 
            "grass": {"water": 2, "fire": 0.5},
            "electric": {"water": 2, "flying": 2}
        }
        
        my_type = my_types[0].value.lower()
        opponent_type = opponent_types[0].value.lower()
        
        effectiveness = type_chart.get(my_type, {}).get(opponent_type, 1.0)
        
        if effectiveness > 1.0:
            return {
                "advantage": "favorable", 
                "effectiveness": effectiveness,
                "explanation": f"{my_type.title()} is super effective against {opponent_type.title()}!"
            }
        elif effectiveness < 1.0:
            return {
                "advantage": "unfavorable",
                "effectiveness": effectiveness, 
                "explanation": f"{my_type.title()} is not very effective against {opponent_type.title()}."
            }
        else:
            return {
                "advantage": "neutral",
                "effectiveness": effectiveness,
                "explanation": f"Neutral matchup between {my_type.title()} and {opponent_type.title()}."
            }
    
    def get_educational_context(self, situation: str) -> Dict[str, str]:
        """Generate educational context for AI learning"""
        return {
            "ai_concept": "strategic_decision_making",
            "pokemon_example": situation,
            "learning_objective": "Understanding how AI analyzes game states and makes decisions",
            "child_explanation": f"Watch how the AI thinks about this Pokemon situation step by step!"
        }

# Mock classes for development
class MockModelFactory:
    """Placeholder model factory for development"""
    
    def __init__(self):
        self.config = MockConfig()
    
    def create_pokemon_model(self, *args, **kwargs):
        return MockModel()
    
    def get_pokemon_cost_info(self, agent_role: str):
        return {
            "model": "development-mock",
            "cost_per_1k_tokens": 0.0,
            "environment": "development"
        }

class MockConfig:
    """Placeholder config for development"""
    
    def __init__(self):
        self.environment = MockEnvironment()

class MockEnvironment:
    """Placeholder environment for development"""
    
    def __init__(self):
        self.value = "development"

class MockModel:
    """Placeholder model for development"""
    
    async def ainvoke(self, messages):
        return MockResponse("AI is thinking about Pokemon strategy...")

class MockResponse:
    """Placeholder response for development"""
    
    def __init__(self, content):
        self.content = content

# Test the base agent
if __name__ == "__main__":
    from models.pokemon_card import PokemonCard, CardCategory, PokemonType
    
    # Create a test agent
    class TestAgent(BasePokemonAgent):
        def get_pokemon_system_prompt(self):
            return "Test Pokemon AI agent"
    
    agent = TestAgent("test_agent", "test_session", "Ash")
    
    # Test matchup analysis
    charmander = PokemonCard(
        id="test-char", name="Charmander", category=CardCategory.POKEMON,
        types=[PokemonType.FIRE]
    )
    
    bulbasaur = PokemonCard(
        id="test-bulb", name="Bulbasaur", category=CardCategory.POKEMON, 
        types=[PokemonType.GRASS]
    )
    
    matchup = agent.analyze_pokemon_matchup(charmander, bulbasaur)
    print(f"🔥 Charmander vs 🌱 Bulbasaur: {matchup}")
    
    context = agent.get_educational_context("Charmander vs Bulbasaur type matchup")
    print(f"🎓 Educational context: {context}")
    
    print("\n✅ Base Pokemon Agent working correctly!")