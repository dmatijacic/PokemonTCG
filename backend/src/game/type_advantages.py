# backend/src/game/type_advantages.py
"""
Pokemon Type Effectiveness Calculator for TCG LLM Education Platform
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
import json
from pathlib import Path

from ..models.pokemon_card import PokemonType, PokemonCard

class EffectivenessLevel(Enum):
    """Type effectiveness levels"""
    NO_EFFECT = 0.0
    NOT_VERY_EFFECTIVE = 0.5
    NORMAL_EFFECTIVE = 1.0
    SUPER_EFFECTIVE = 2.0

class PokemonTypeCalculator:
    """
    Calculates Pokemon type effectiveness for battles and AI decision-making
    """
    
    def __init__(self):
        self.type_chart = self._load_type_chart()
    
    def _load_type_chart(self) -> Dict[str, Dict[str, float]]:
        """Load type effectiveness chart from JSON file or create default"""
        try:
            # Try to load from assets
            assets_path = Path(__file__).parent.parent.parent.parent / "assets" / "cards" / "data" / "type_chart.json"
            if assets_path.exists():
                with open(assets_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Could not load type chart from file: {e}")
        
        # Return comprehensive type chart
        return {
            "normal": {
                "rock": 0.5, "ghost": 0, "steel": 0.5
            },
            "fire": {
                "fire": 0.5, "water": 0.5, "grass": 2, "ice": 2,
                "bug": 2, "rock": 0.5, "dragon": 0.5, "steel": 2
            },
            "water": {
                "fire": 2, "water": 0.5, "grass": 0.5, "ground": 2,
                "rock": 2, "dragon": 0.5
            },
            "electric": {
                "water": 2, "electric": 0.5, "grass": 0.5, "ground": 0,
                "flying": 2, "dragon": 0.5
            },
            "grass": {
                "fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5,
                "ground": 2, "rock": 2, "bug": 0.5, "dragon": 0.5,
                "steel": 0.5, "flying": 0.5
            },
            "ice": {
                "fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5,
                "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5
            },
            "fighting": {
                "normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5,
                "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0,
                "dark": 2, "steel": 2, "fairy": 0.5
            },
            "poison": {
                "grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5,
                "ghost": 0.5, "steel": 0, "fairy": 2
            },
            "ground": {
                "fire": 2, "electric": 2, "grass": 0.5, "poison": 2,
                "flying": 0, "bug": 0.5, "rock": 2, "steel": 2
            },
            "flying": {
                "electric": 0.5, "grass": 2, "ice": 0.5, "fighting": 2,
                "bug": 2, "rock": 0.5, "steel": 0.5
            },
            "psychic": {
                "fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0,
                "steel": 0.5
            },
            "bug": {
                "fire": 0.5, "grass": 2, "fighting": 0.5, "poison": 0.5,
                "flying": 0.5, "psychic": 2, "ghost": 0.5, "dark": 2,
                "steel": 0.5, "fairy": 0.5
            },
            "rock": {
                "fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5,
                "flying": 2, "bug": 2, "steel": 0.5
            },
            "ghost": {
                "normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5
            },
            "dragon": {
                "dragon": 2, "steel": 0.5, "fairy": 0
            },
            "dark": {
                "fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5,
                "fairy": 0.5
            },
            "steel": {
                "fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2,
                "rock": 2, "steel": 0.5, "fairy": 2
            },
            "fairy": {
                "fire": 0.5, "fighting": 2, "poison": 0.5, "dragon": 2,
                "dark": 2, "steel": 0.5
            }
        }
    
    def get_effectiveness(self, attacking_type: PokemonType, defending_type: PokemonType) -> float:
        """Get type effectiveness multiplier"""
        attacking_key = attacking_type.value
        defending_key = defending_type.value
        
        if attacking_key in self.type_chart:
            return self.type_chart[attacking_key].get(defending_key, 1.0)
        
        return 1.0  # Normal effectiveness by default
    
    def get_effectiveness_level(self, attacking_type: PokemonType, defending_type: PokemonType) -> EffectivenessLevel:
        """Get effectiveness level enum"""
        multiplier = self.get_effectiveness(attacking_type, defending_type)
        
        if multiplier == 0.0:
            return EffectivenessLevel.NO_EFFECT
        elif multiplier == 0.5:
            return EffectivenessLevel.NOT_VERY_EFFECTIVE
        elif multiplier == 2.0:
            return EffectivenessLevel.SUPER_EFFECTIVE
        else:
            return EffectivenessLevel.NORMAL_EFFECTIVE
    
    def calculate_attack_damage(self, 
                              attack_damage: int,
                              attacking_type: PokemonType,
                              defending_pokemon: PokemonCard) -> int:
        """
        Calculate final damage after type effectiveness, weakness, and resistance
        """
        if attack_damage <= 0:
            return 0
        
        final_damage = attack_damage
        
        # Apply type effectiveness for each defending type
        for defending_type in defending_pokemon.types:
            effectiveness = self.get_effectiveness(attacking_type, defending_type)
            final_damage = int(final_damage * effectiveness)
        
        # Apply weakness (handled by the Pokemon card itself)
        weakness_multiplier = defending_pokemon.calculate_damage_multiplier(attacking_type)
        final_damage = int(final_damage * weakness_multiplier)
        
        # Apply resistance (reduce damage)
        resistance_reduction = defending_pokemon.calculate_damage_reduction(attacking_type)
        final_damage = max(0, final_damage - resistance_reduction)
        
        return final_damage
    
    def get_best_attack_type_against(self, defending_pokemon: PokemonCard) -> Tuple[PokemonType, float]:
        """Find the most effective attack type against a Pokemon"""
        best_type = PokemonType.NORMAL
        best_effectiveness = 0.0
        
        for attack_type in PokemonType:
            if attack_type == PokemonType.COLORLESS:  # Skip colorless
                continue
                
            total_effectiveness = 1.0
            
            # Calculate effectiveness against all defending types
            for defending_type in defending_pokemon.types:
                effectiveness = self.get_effectiveness(attack_type, defending_type)
                total_effectiveness *= effectiveness
            
            # Consider weakness
            weakness_multiplier = defending_pokemon.calculate_damage_multiplier(attack_type)
            total_effectiveness *= weakness_multiplier
            
            if total_effectiveness > best_effectiveness:
                best_effectiveness = total_effectiveness
                best_type = attack_type
        
        return best_type, best_effectiveness
    
    def get_worst_attack_type_against(self, defending_pokemon: PokemonCard) -> Tuple[PokemonType, float]:
        """Find the least effective attack type against a Pokemon"""
        worst_type = PokemonType.NORMAL
        worst_effectiveness = float('inf')
        
        for attack_type in PokemonType:
            if attack_type == PokemonType.COLORLESS:
                continue
                
            total_effectiveness = 1.0
            
            for defending_type in defending_pokemon.types:
                effectiveness = self.get_effectiveness(attack_type, defending_type)
                total_effectiveness *= effectiveness
            
            weakness_multiplier = defending_pokemon.calculate_damage_multiplier(attack_type)
            total_effectiveness *= weakness_multiplier
            
            if total_effectiveness < worst_effectiveness:
                worst_effectiveness = total_effectiveness
                worst_type = attack_type
        
        return worst_type, worst_effectiveness
    
    def analyze_matchup(self, pokemon1: PokemonCard, pokemon2: PokemonCard) -> Dict[str, any]:
        """Analyze the type matchup between two Pokemon"""
        analysis = {
            "pokemon1": pokemon1.name,
            "pokemon2": pokemon2.name,
            "advantages": {
                "pokemon1_vs_pokemon2": [],
                "pokemon2_vs_pokemon1": []
            },
            "summary": ""
        }
        
        # Analyze Pokemon 1's attacks against Pokemon 2
        for attack in pokemon1.attacks:
            if pokemon1.types:  # Use Pokemon's primary type for attack type
                attack_type = pokemon1.types[0]
                damage = attack.get_damage_value()
                
                if damage > 0:
                    final_damage = self.calculate_attack_damage(damage, attack_type, pokemon2)
                    effectiveness = self.get_effectiveness_level(attack_type, pokemon2.types[0] if pokemon2.types else PokemonType.NORMAL)
                    
                    analysis["advantages"]["pokemon1_vs_pokemon2"].append({
                        "attack": attack.name,
                        "base_damage": damage,
                        "final_damage": final_damage,
                        "effectiveness": effectiveness.name,
                        "multiplier": final_damage / damage if damage > 0 else 0
                    })
        
        # Analyze Pokemon 2's attacks against Pokemon 1
        for attack in pokemon2.attacks:
            if pokemon2.types:
                attack_type = pokemon2.types[0]
                damage = attack.get_damage_value()
                
                if damage > 0:
                    final_damage = self.calculate_attack_damage(damage, attack_type, pokemon1)
                    effectiveness = self.get_effectiveness_level(attack_type, pokemon1.types[0] if pokemon1.types else PokemonType.NORMAL)
                    
                    analysis["advantages"]["pokemon2_vs_pokemon1"].append({
                        "attack": attack.name,
                        "base_damage": damage,
                        "final_damage": final_damage,
                        "effectiveness": effectiveness.name,
                        "multiplier": final_damage / damage if damage > 0 else 0
                    })
        
        # Generate summary
        p1_advantages = [a for a in analysis["advantages"]["pokemon1_vs_pokemon2"] if a["multiplier"] > 1.0]
        p2_advantages = [a for a in analysis["advantages"]["pokemon2_vs_pokemon1"] if a["multiplier"] > 1.0]
        
        if p1_advantages and not p2_advantages:
            analysis["summary"] = f"{pokemon1.name} has type advantage over {pokemon2.name}"
        elif p2_advantages and not p1_advantages:
            analysis["summary"] = f"{pokemon2.name} has type advantage over {pokemon1.name}"
        elif p1_advantages and p2_advantages:
            analysis["summary"] = f"Both Pokemon have some type advantages"
        else:
            analysis["summary"] = f"Neutral type matchup between {pokemon1.name} and {pokemon2.name}"
        
        return analysis
    
    def get_ai_explanation(self, attacking_type: PokemonType, defending_type: PokemonType) -> str:
        """Generate child-friendly explanation of type effectiveness"""
        effectiveness = self.get_effectiveness(attacking_type, defending_type)
        
        attacking_name = attacking_type.value.title()
        defending_name = defending_type.value.title()
        
        if effectiveness == 2.0:
            return f"{attacking_name} attacks are super effective against {defending_name} Pokemon! They do double damage!"
        elif effectiveness == 0.5:
            return f"{attacking_name} attacks are not very effective against {defending_name} Pokemon. They do half damage."
        elif effectiveness == 0.0:
            return f"{attacking_name} attacks have no effect on {defending_name} Pokemon!"
        else:
            return f"{attacking_name} attacks do normal damage to {defending_name} Pokemon."
    
    def get_strategic_advice(self, my_pokemon: PokemonCard, opponent_pokemon: PokemonCard) -> Dict[str, str]:
        """Generate strategic advice for AI agents"""
        advice = {
            "offensive": "",
            "defensive": "",
            "recommendation": ""
        }
        
        if not my_pokemon.types or not opponent_pokemon.types:
            advice["recommendation"] = "Type information unavailable for strategic analysis."
            return advice
        
        # Offensive analysis
        my_type = my_pokemon.types[0]
        opponent_type = opponent_pokemon.types[0]
        
        offensive_effectiveness = self.get_effectiveness(my_type, opponent_type)
        
        if offensive_effectiveness >= 2.0:
            advice["offensive"] = f"Your {my_pokemon.name} has type advantage! {my_type.value.title()} beats {opponent_type.value.title()}."
        elif offensive_effectiveness <= 0.5:
            advice["offensive"] = f"Your {my_pokemon.name} is at a type disadvantage. {my_type.value.title()} is weak against {opponent_type.value.title()}."
        else:
            advice["offensive"] = f"Neutral type matchup for your {my_pokemon.name}."
        
        # Defensive analysis
        defensive_effectiveness = self.get_effectiveness(opponent_type, my_type)
        
        if defensive_effectiveness >= 2.0:
            advice["defensive"] = f"Be careful! {opponent_pokemon.name}'s {opponent_type.value.title()} attacks are super effective against your {my_type.value.title()} Pokemon."
        elif defensive_effectiveness <= 0.5:
            advice["defensive"] = f"Good news! Your {my_pokemon.name} resists {opponent_pokemon.name}'s {opponent_type.value.title()} attacks."
        else:
            advice["defensive"] = f"Your {my_pokemon.name} takes normal damage from {opponent_pokemon.name}."
        
        # Overall recommendation
        if offensive_effectiveness >= 2.0 and defensive_effectiveness <= 1.0:
            advice["recommendation"] = f"Great matchup! Attack with {my_pokemon.name} for maximum damage."
        elif offensive_effectiveness <= 0.5 and defensive_effectiveness >= 2.0:
            advice["recommendation"] = f"Poor matchup. Consider switching to a different Pokemon if possible."
        elif offensive_effectiveness >= 2.0:
            advice["recommendation"] = f"Attack aggressively with {my_pokemon.name} while you have type advantage."
        elif defensive_effectiveness >= 2.0:
            advice["recommendation"] = f"Play defensively or consider switching Pokemon."
        else:
            advice["recommendation"] = f"Balanced matchup. Focus on Pokemon with higher attack damage."
        
        return advice

# Helper functions for AI education
def get_type_advantage_examples() -> List[Dict[str, str]]:
    """Get examples of type advantages for AI teaching"""
    return [
        {
            "attacking": "Fire",
            "defending": "Grass",
            "result": "Super Effective (2x damage)",
            "explanation": "Fire burns grass easily",
            "example": "Charmander's Ember vs Bulbasaur"
        },
        {
            "attacking": "Water", 
            "defending": "Fire",
            "result": "Super Effective (2x damage)",
            "explanation": "Water puts out fire",
            "example": "Squirtle's Water Gun vs Charmander"
        },
        {
            "attacking": "Grass",
            "defending": "Water", 
            "result": "Super Effective (2x damage)",
            "explanation": "Plants absorb water to grow",
            "example": "Bulbasaur's Vine Whip vs Squirtle"
        },
        {
            "attacking": "Electric",
            "defending": "Water",
            "result": "Super Effective (2x damage)",
            "explanation": "Electricity conducts through water",
            "example": "Pikachu's Thunderbolt vs Squirtle"
        },
        {
            "attacking": "Electric",
            "defending": "Ground",
            "result": "No Effect (0x damage)",
            "explanation": "Ground absorbs electricity safely",
            "example": "Pikachu's attacks vs Diglett"
        }
    ]

# Global instance for easy access
type_calculator = PokemonTypeCalculator()

# Example usage and testing
if __name__ == "__main__":
    from ..models.pokemon_card import PokemonCard, CardCategory, Attack, Weakness
    
    # Create test Pokemon
    charmander = PokemonCard(
        id="test-char", name="Charmander", category=CardCategory.POKEMON,
        hp=50, types=[PokemonType.FIRE],
        attacks=[Attack(name="Ember", damage=30)]
    )
    
    squirtle = PokemonCard(
        id="test-squi", name="Squirtle", category=CardCategory.POKEMON,
        hp=50, types=[PokemonType.WATER],
        attacks=[Attack(name="Water Gun", damage=30)],
        weaknesses=[Weakness(type=PokemonType.ELECTRIC, multiplier=2.0)]
    )
    
    bulbasaur = PokemonCard(
        id="test-bulb", name="Bulbasaur", category=CardCategory.POKEMON,
        hp=50, types=[PokemonType.GRASS],
        attacks=[Attack(name="Vine Whip", damage=30)]
    )
    
    calc = PokemonTypeCalculator()
    
    # Test basic effectiveness
    print("=== Type Effectiveness Tests ===")
    print(f"Fire vs Grass: {calc.get_effectiveness(PokemonType.FIRE, PokemonType.GRASS)}x")
    print(f"Water vs Fire: {calc.get_effectiveness(PokemonType.WATER, PokemonType.FIRE)}x")
    print(f"Grass vs Water: {calc.get_effectiveness(PokemonType.GRASS, PokemonType.WATER)}x")
    
    # Test damage calculation
    print("\n=== Damage Calculation Tests ===")
    fire_vs_grass_damage = calc.calculate_attack_damage(30, PokemonType.FIRE, bulbasaur)
    print(f"Charmander's Ember (30) vs Bulbasaur: {fire_vs_grass_damage} damage")
    
    water_vs_fire_damage = calc.calculate_attack_damage(30, PokemonType.WATER, charmander)
    print(f"Squirtle's Water Gun (30) vs Charmander: {water_vs_fire_damage} damage")
    
    # Test matchup analysis
    print("\n=== Matchup Analysis ===")
    matchup = calc.analyze_matchup(charmander, bulbasaur)
    print(f"Charmander vs Bulbasaur: {matchup['summary']}")
    
    # Test AI explanations
    print("\n=== AI Explanations ===")
    explanation = calc.get_ai_explanation(PokemonType.FIRE, PokemonType.GRASS)
    print(f"Fire vs Grass: {explanation}")
    
    # Test strategic advice
    print("\n=== Strategic Advice ===")
    advice = calc.get_strategic_advice(charmander, bulbasaur)
    print(f"Offensive: {advice['offensive']}")
    print(f"Defensive: {advice['defensive']}")
    print(f"Recommendation: {advice['recommendation']}")
    
    print("\n✅ Pokemon type calculator working correctly!")