# backend/src/ai_agents/enhanced_opponent_ai.py
"""
Enhanced Pokemon Opponent AI with real GPT integration
"""

import asyncio
from typing import Dict, Any
from openai_integration import pokemon_openai
from opponent_ai import PokemonOpponentAI as BasePokemonOpponentAI

class EnhancedPokemonOpponentAI(BasePokemonOpponentAI):
    """
    Pokemon AI that uses real GPT model when available
    """
    
    def __init__(self, game_session_id: str = None, child_name: str = "trainer", difficulty: str = "easy"):
        super().__init__(game_session_id, child_name, difficulty)
        self.openai_client = pokemon_openai
        self.use_gpt = self.openai_client.is_available
        
        if self.use_gpt:
            print(f"🤖 Enhanced Pokemon AI using GPT-4o-mini for {child_name}")
        else:
            print(f"🎮 Pokemon AI using demo mode for {child_name}")
    
    async def make_move(self, game_state) -> Dict[str, Any]:
        """Make a Pokemon move using GPT when available"""
        
        if not self.use_gpt:
            # Fall back to base class demo behavior
            return await super().make_move(game_state)
        
        try:
            # Generate system prompt for GPT
            system_prompt = self._generate_gpt_system_prompt()
            
            # Generate game situation description
            situation = self._describe_game_situation(game_state)
            
            # Get GPT response
            gpt_response = await self.openai_client.get_pokemon_ai_response(
                system_prompt=system_prompt,
                user_message=situation,
                max_tokens=400,
                temperature=0.8
            )
            
            if gpt_response:
                # Parse GPT response into game decision
                decision = self._parse_gpt_response(gpt_response["response"], game_state)
                
                # Add GPT metadata
                decision["gpt_used"] = True
                decision["gpt_cost"] = gpt_response["cost"]
                decision["gpt_tokens"] = gpt_response["usage"]["total_tokens"]
                
                print(f"🎯 GPT Pokemon AI Decision: {decision.get('action', 'unknown')}")
                
                return decision
            else:
                print("⚠️  GPT failed, falling back to demo mode")
                return await super().make_move(game_state)
                
        except Exception as e:
            print(f"❌ Enhanced AI error: {e}")
            # Fall back to demo mode
            return await super().make_move(game_state)
    
    def _generate_gpt_system_prompt(self) -> str:
        """Generate system prompt for GPT Pokemon AI"""
        return f"""You are an intelligent Pokemon TCG opponent playing against {self.child_name}, a 9-year-old child.

Your role:
- Play Pokemon strategically but fairly
- Explain your moves in simple, educational terms
- Teach about type advantages through gameplay
- Be encouraging and show how AI thinks

Respond with a JSON object containing:
{{
    "action": "attack|retreat|switch|play_pokemon",
    "explanation": "Simple explanation of your move",
    "type_lesson": "Educational point about Pokemon types (if relevant)",
    "strategic_insight": "How AI thinks about this situation",
    "reasoning": "Why you chose this move"
}}

Keep explanations child-friendly and educational. Focus on teaching AI concepts through Pokemon strategy."""

    def _describe_game_situation(self, game_state) -> str:
        """Describe current game situation for GPT"""
        summary = game_state.get_game_summary_for_ai()
        
        # Add specific Pokemon matchup info
        my_pokemon = game_state.ai_player.active_pokemon
        opponent_pokemon = game_state.child_player.active_pokemon
        
        situation = f"""
Current Pokemon Battle Situation:

{summary}

Current Matchup:
- Your Pokemon: {my_pokemon.name if my_pokemon else 'None'} ({my_pokemon.hp if my_pokemon else 0} HP)
- Opponent's Pokemon: {opponent_pokemon.name if opponent_pokemon else 'None'} ({opponent_pokemon.hp if opponent_pokemon else 0} HP)

Your turn! Choose the best move and explain your AI thinking process to help the child learn.
"""
        
        return situation
    
    def _parse_gpt_response(self, gpt_text: str, game_state) -> Dict[str, Any]:
        """Parse GPT response into game decision"""
        try:
            import json
            
            # Try to extract JSON from response
            if "{" in gpt_text and "}" in gpt_text:
                start = gpt_text.find("{")
                end = gpt_text.rfind("}") + 1
                json_str = gpt_text[start:end]
                
                parsed = json.loads(json_str)
                
                # Validate required fields
                if "action" in parsed and "explanation" in parsed:
                    return parsed
            
            # If JSON parsing fails, create structured response from text
            return {
                "action": "attack",  # Default action
                "explanation": gpt_text[:200] + "..." if len(gpt_text) > 200 else gpt_text,
                "type_lesson": "🎓 AI analyzes multiple factors to make optimal decisions!",
                "strategic_insight": "🎯 This demonstrates how AI processes information and chooses actions.",
                "reasoning": "GPT provided strategic analysis"
            }
            
        except Exception as e:
            print(f"⚠️  GPT response parsing error: {e}")
            return {
                "action": "attack",
                "explanation": "AI is making a strategic Pokemon move!",
                "type_lesson": "🎓 AI considers type advantages when choosing moves!",
                "strategic_insight": "🎯 This shows how AI makes decisions under uncertainty."
            }

# Test function
async def test_enhanced_pokemon_ai():
    """Test the enhanced Pokemon AI with GPT"""
    print("🧪 Testing Enhanced Pokemon AI with GPT...")
    
    # Check OpenAI status
    status = pokemon_openai.get_status()
    print(f"📊 OpenAI Status: {status}")
    
    if not status["available"]:
        print("❌ OpenAI not available - check API key and connection")
        return False
    
    try:
        # Create enhanced AI
        ai = EnhancedPokemonOpponentAI("test", "TestTrainer", "easy")
        
        # Create mock game state
        from ..models.game_state import create_new_pokemon_game
        game_state = create_new_pokemon_game("test", "TestTrainer")
        
        # Test AI decision
        decision = await ai.make_move(game_state)
        
        print("✅ Enhanced Pokemon AI test successful!")
        print(f"🎯 Decision: {decision}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Pokemon AI test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_enhanced_pokemon_ai())