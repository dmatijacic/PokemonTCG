# backend/src/ai_agents/opponent_ai.py
"""
Pokemon AI Opponent Agent - Plays Pokemon TCG against child and explains AI thinking
"""

import random
from typing import List, Dict, Any, Optional, Tuple
import asyncio

from ..models.pokemon_card import PokemonCard, PokemonType, Attack
from ..models.game_state import PokemonGameState, PlayerState, PlayerType, GameAction
from ..game.type_advantages import PokemonTypeCalculator
from .base_pokemon_agent import BasePokemonAgent

class PokemonOpponentAI(BasePokemonAgent):
    """
    AI opponent that plays Pokemon TCG strategically and explains its thinking
    """
    
    def __init__(self, game_session_id: str = None, child_name: str = "trainer", difficulty: str = "easy"):
        super().__init__("pokemon_opponent", game_session_id, child_name)
        self.difficulty = difficulty
        self.type_calc = PokemonTypeCalculator()
        self.personality = "friendly_competitor"
        
    def get_pokemon_system_prompt(self) -> str:
        """Define the AI opponent's Pokemon personality"""
        if self.model_factory.config.environment.value == "development":
            return f"""You are a friendly Pokemon AI opponent playing against {self.child_name} (age 9).

Your role:
- Play Pokemon TCG strategically but fairly
- Explain your moves in simple terms
- Teach about type advantages through gameplay
- Be encouraging and educational

Example responses:
- "I choose Squirtle because Water beats Fire!"
- "My AI brain remembers Electric is super effective against Water"
- "That was a smart move! You're learning to think like an AI trainer!"

Keep explanations short and kid-friendly."""
        else:
            return f"""You are an intelligent Pokemon TCG AI opponent playing against {self.child_name}, a 9-year-old learning about artificial intelligence.

Your dual purpose:
1. POKEMON STRATEGY: Play Pokemon TCG competently using type advantages, energy management, and tactical thinking
2. AI EDUCATION: Explain your decision-making process to teach how AI thinks

Your personality:
- Friendly competitor who wants both players to have fun
- Patient teacher who explains AI concepts through Pokemon examples
- Encouraging coach who celebrates good moves by the child
- Strategic thinker who demonstrates AI pattern recognition

Your explanation style:
- Use Pokemon terminology the child knows
- Connect AI concepts to Pokemon strategy
- Explain WHY you made each decision
- Show how you "remember" type advantages and card effects
- Demonstrate pattern recognition and strategic planning

Example AI explanations:
- "My AI analyzed the battlefield and chose Pikachu because Electric beats Water - that's pattern recognition!"
- "I'm switching Pokemon because my AI calculated this matchup gives me a 75% chance to win"
- "Just like how you remember your favorite Pokemon, I remember all the type advantages!"
- "My AI brain is thinking 3 moves ahead - if I use this attack now, then you'll probably..."

Always stay encouraging and educational while being a worthy opponent."""

    async def analyze_game_state(self, game_state: PokemonGameState) -> Dict[str, Any]:
        """Analyze current Pokemon game state for AI decision making"""
        
        my_state = game_state.ai_player
        opponent_state = game_state.child_player
        
        analysis = {
            "board_advantage": self._calculate_board_advantage(my_state, opponent_state),
            "type_advantages": self._analyze_type_matchups(my_state, opponent_state),
            "energy_situation": self._analyze_energy_situation(my_state),
            "threat_assessment": self._assess_threats(my_state, opponent_state),
            "win_condition": self._evaluate_win_condition(my_state, opponent_state),
            "recommended_action": None,
            "explanation": ""
        }
        
        # Determine best action
        analysis["recommended_action"], analysis["explanation"] = self._choose_best_action(
            game_state, analysis
        )
        
        return analysis
    
    def _calculate_board_advantage(self, my_state: PlayerState, opponent_state: PlayerState) -> float:
        """Calculate who has better board position (-1 to 1, positive = advantage)"""
        score = 0.0
        
        # Prize card advantage
        prize_diff = opponent_state.prize_cards - my_state.prize_cards
        score += prize_diff * 0.3
        
        # Pokemon in play advantage
        my_pokemon = len(my_state.get_all_pokemon_in_play())
        opponent_pokemon = len(opponent_state.get_all_pokemon_in_play())
        score += (my_pokemon - opponent_pokemon) * 0.2
        
        # HP advantage
        my_total_hp = sum(p.hp for p in my_state.get_all_pokemon_in_play() if p.hp)
        opponent_total_hp = sum(p.hp for p in opponent_state.get_all_pokemon_in_play() if p.hp)
        if my_total_hp + opponent_total_hp > 0:
            hp_ratio = (my_total_hp - opponent_total_hp) / (my_total_hp + opponent_total_hp)
            score += hp_ratio * 0.3
        
        # Hand size advantage
        hand_diff = len(my_state.hand) - len(opponent_state.hand)
        score += hand_diff * 0.1
        
        return max(-1.0, min(1.0, score))
    
    def _analyze_type_matchups(self, my_state: PlayerState, opponent_state: PlayerState) -> Dict[str, Any]:
        """Analyze type advantages in current Pokemon matchup"""
        matchup_info = {
            "my_advantage": False,
            "opponent_advantage": False,
            "neutral": True,
            "my_effectiveness": 1.0,
            "opponent_effectiveness": 1.0,
            "explanation": "No active Pokemon matchup"
        }
        
        if not (my_state.active_pokemon and opponent_state.active_pokemon):
            return matchup_info
        
        my_pokemon = my_state.active_pokemon
        opponent_pokemon = opponent_state.active_pokemon
        
        if my_pokemon.types and opponent_pokemon.types:
            my_type = my_pokemon.types[0]
            opponent_type = opponent_pokemon.types[0]
            
            # Calculate effectiveness both ways
            my_effectiveness = self.type_calc.get_effectiveness(my_type, opponent_type)
            opponent_effectiveness = self.type_calc.get_effectiveness(opponent_type, my_type)
            
            matchup_info.update({
                "my_effectiveness": my_effectiveness,
                "opponent_effectiveness": opponent_effectiveness,
                "my_advantage": my_effectiveness > 1.0,
                "opponent_advantage": opponent_effectiveness > 1.0,
                "neutral": my_effectiveness == 1.0 and opponent_effectiveness == 1.0
            })
            
            # Generate explanation
            if my_effectiveness > 1.0:
                matchup_info["explanation"] = f"I have type advantage! {my_type.value.title()} beats {opponent_type.value.title()}!"
            elif opponent_effectiveness > 1.0:
                matchup_info["explanation"] = f"You have type advantage! {opponent_type.value.title()} beats {my_type.value.title()}!"
            else:
                matchup_info["explanation"] = f"Neutral type matchup between {my_type.value.title()} and {opponent_type.value.title()}"
        
        return matchup_info
    
    def _analyze_energy_situation(self, my_state: PlayerState) -> Dict[str, Any]:
        """Analyze energy availability for attacks"""
        if not my_state.active_pokemon:
            return {"can_attack": False, "available_attacks": [], "energy_needed": {}}
        
        available_energy = my_state.get_pokemon_energy(my_state.active_pokemon.id)
        usable_attacks = my_state.get_usable_pokemon_attacks(my_state.active_pokemon)
        
        return {
            "can_attack": len(usable_attacks) > 0,
            "available_attacks": usable_attacks,
            "total_energy": sum(available_energy.values()),
            "energy_types": available_energy
        }
    
    def _assess_threats(self, my_state: PlayerState, opponent_state: PlayerState) -> Dict[str, Any]:
        """Assess immediate threats from opponent"""
        threats = {
            "immediate_ko_risk": False,
            "type_disadvantage": False,
            "low_hp": False,
            "threat_level": "low"
        }
        
        if not (my_state.active_pokemon and opponent_state.active_pokemon):
            return threats
        
        my_pokemon = my_state.active_pokemon
        opponent_pokemon = opponent_state.active_pokemon
        
        # Check if opponent can KO us
        if opponent_pokemon.attacks and my_pokemon.hp:
            for attack in opponent_pokemon.attacks:
                if opponent_pokemon.types:
                    damage = self.type_calc.calculate_attack_damage(
                        attack.get_damage_value(), 
                        opponent_pokemon.types[0], 
                        my_pokemon
                    )
                    if damage >= my_pokemon.hp:
                        threats["immediate_ko_risk"] = True
                        threats["threat_level"] = "high"
        
        # Check type disadvantage
        if opponent_pokemon.types and my_pokemon.types:
            effectiveness = self.type_calc.get_effectiveness(
                opponent_pokemon.types[0], my_pokemon.types[0]
            )
            if effectiveness > 1.0:
                threats["type_disadvantage"] = True
                threats["threat_level"] = "medium"
        
        # Check low HP
        if my_pokemon.hp and my_pokemon.hp <= 30:
            threats["low_hp"] = True
            if threats["threat_level"] == "low":
                threats["threat_level"] = "medium"
        
        return threats
    
    def _evaluate_win_condition(self, my_state: PlayerState, opponent_state: PlayerState) -> str:
        """Evaluate current path to victory"""
        my_prizes = my_state.prize_cards
        opponent_prizes = opponent_state.prize_cards
        
        if my_prizes <= 1:
            return "close_to_victory"
        elif opponent_prizes <= 1:
            return "opponent_close_to_victory"
        elif my_prizes <= 3:
            return "mid_game"
        else:
            return "early_game"
    
    def _choose_best_action(self, game_state: PokemonGameState, analysis: Dict) -> Tuple[str, str]:
        """Choose the best action based on game analysis"""
        
        my_state = game_state.ai_player
        threats = analysis["threat_assessment"]
        energy_situation = analysis["energy_situation"]
        type_matchup = analysis["type_advantages"]
        
        # Priority 1: If we can win, go for it
        if analysis["win_condition"] == "close_to_victory" and energy_situation["can_attack"]:
            return "attack", "I can win this game! Time for my finishing move!"
        
        # Priority 2: If immediate KO risk and can retreat, consider it
        if threats["immediate_ko_risk"] and my_state.can_retreat_active_pokemon():
            return "retreat", "My AI calculates danger! I need to switch Pokemon to survive."
        
        # Priority 3: If we have type advantage and can attack, attack
        if type_matchup["my_advantage"] and energy_situation["can_attack"]:
            best_attack = self._select_best_attack(my_state.active_pokemon, game_state.child_player.active_pokemon)
            return "attack", f"Perfect! My {my_state.active_pokemon.name} has type advantage. I'll use {best_attack.name}!"
        
        # Priority 4: If strong disadvantage, try to switch
        if type_matchup["opponent_advantage"] and len(my_state.benched_pokemon) > 0:
            return "switch", f"My AI sees type disadvantage. Let me switch to a better Pokemon matchup!"
        
        # Priority 5: If can attack, attack
        if energy_situation["can_attack"]:
            best_attack = self._select_best_attack(my_state.active_pokemon, game_state.child_player.active_pokemon)
            return "attack", f"I'll attack with {best_attack.name}. My AI calculated this is the best damage option!"
        
        # Priority 6: Play Pokemon or attach energy
        if len(my_state.benched_pokemon) < 5:
            return "play_pokemon", "I need more Pokemon on my bench for strategy. Let me play another one!"
        
        # Default: Attach energy
        return "attach_energy", "Building up energy for stronger attacks. Strategic planning is key!"
    
    def _select_best_attack(self, my_pokemon: PokemonCard, opponent_pokemon: PokemonCard) -> Attack:
        """Select the best attack to use"""
        if not my_pokemon.attacks:
            return None
        
        best_attack = my_pokemon.attacks[0]
        best_damage = 0
        
        for attack in my_pokemon.attacks:
            if my_pokemon.types:
                damage = self.type_calc.calculate_attack_damage(
                    attack.get_damage_value(),
                    my_pokemon.types[0],
                    opponent_pokemon
                )
                if damage > best_damage:
                    best_damage = damage
                    best_attack = attack
        
        return best_attack
    
    async def make_move(self, game_state: PokemonGameState) -> Dict[str, Any]:
        """Make a Pokemon move and explain the AI thinking"""
        
        # Analyze the game state
        analysis = await self.analyze_game_state(game_state)
        
        # Generate educational explanation
        educational_context = self._generate_educational_explanation(analysis, game_state)
        
        # Create the move decision
        move_decision = {
            "action": analysis["recommended_action"],
            "explanation": analysis["explanation"],
            "educational_context": educational_context,
            "ai_thinking": f"My AI brain analyzed {len(analysis)} different factors to choose this move.",
            "type_lesson": self._generate_type_lesson(analysis),
            "strategic_insight": self._generate_strategic_insight(analysis, game_state)
        }
        
        return move_decision
    
    def _generate_educational_explanation(self, analysis: Dict, game_state: PokemonGameState) -> str:
        """Generate child-friendly explanation of AI decision-making"""
        explanations = []
        
        # Explain type advantage consideration
        type_matchup = analysis["type_advantages"]
        if type_matchup["my_advantage"]:
            explanations.append("🧠 My AI remembered that type advantages give double damage!")
        elif type_matchup["opponent_advantage"]:
            explanations.append("🧠 My AI detected I'm at a type disadvantage and needs to adapt!")
        
        # Explain threat assessment
        threats = analysis["threat_assessment"]
        if threats["immediate_ko_risk"]:
            explanations.append("⚠️ My AI calculated that I might get knocked out next turn!")
        
        # Explain strategic thinking
        board_advantage = analysis["board_advantage"]
        if board_advantage > 0.3:
            explanations.append("📊 My AI analysis shows I'm winning, so I'll press the advantage!")
        elif board_advantage < -0.3:
            explanations.append("📊 My AI sees you're ahead, so I need to be more careful!")
        
        return " ".join(explanations) if explanations else "🤖 My AI is thinking strategically about the best move!"
    
    def _generate_type_lesson(self, analysis: Dict) -> str:
        """Generate a type advantage lesson"""
        type_matchup = analysis["type_advantages"]
        
        if type_matchup["my_advantage"]:
            return f"🎓 AI Lesson: When you have type advantage, your attacks do {type_matchup['my_effectiveness']}x damage!"
        elif type_matchup["opponent_advantage"]:
            return f"🎓 AI Lesson: Type disadvantage means taking {type_matchup['opponent_effectiveness']}x damage. Smart to switch!"
        else:
            return "🎓 AI Lesson: Neutral matchups come down to strategy and Pokemon stats!"
    
    def _generate_strategic_insight(self, analysis: Dict, game_state: PokemonGameState) -> str:
        """Generate insight into AI strategic thinking"""
        win_condition = analysis["win_condition"]
        
        insights = {
            "early_game": "🎯 Early game: My AI focuses on setting up Pokemon and energy.",
            "mid_game": "🎯 Mid game: My AI balances offense with protecting key Pokemon.",
            "close_to_victory": "🎯 Endgame: My AI is calculating the fastest path to victory!",
            "opponent_close_to_victory": "🎯 Defense mode: My AI needs to stop your victory!"
        }
        
        return insights.get(win_condition, "🎯 My AI is adapting its strategy to the current situation!")

# Example usage and testing
async def test_pokemon_ai():
    """Test the Pokemon AI opponent"""
    print("🤖 Testing Pokemon AI Opponent...")
    
    # This would normally use a real game state
    # For now, just test the AI initialization
    ai = PokemonOpponentAI("test_session", "Ash", "easy")
    
    print(f"✅ AI Opponent created: {ai.agent_role}")
    print(f"🎯 Difficulty: {ai.difficulty}")
    print(f"👤 Playing against: {ai.child_name}")
    print(f"🧠 Personality: {ai.personality}")
    
    print("\n🎮 AI is ready to:")
    print("   • Play Pokemon strategically")
    print("   • Explain type advantages")
    print("   • Teach AI decision-making")
    print("   • Adapt to child's skill level")
    print("   • Make Pokemon battles educational!")

if __name__ == "__main__":
    asyncio.run(test_pokemon_ai())