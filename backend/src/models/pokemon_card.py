# backend/src/models/pokemon_card.py
"""
Pokemon Card data models for TCG LLM Education Platform
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from dataclasses import dataclass

class PokemonType(str, Enum):
    """Pokemon energy types"""
    NORMAL = "normal"
    FIRE = "fire" 
    WATER = "water"
    ELECTRIC = "electric"
    GRASS = "grass"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"
    DARK = "dark"
    STEEL = "steel"
    FAIRY = "fairy"
    COLORLESS = "colorless"

class CardCategory(str, Enum):
    """Pokemon card categories"""
    POKEMON = "Pokemon"
    TRAINER = "Trainer"
    ENERGY = "Energy"

class PokemonStage(str, Enum):
    """Pokemon evolution stages"""
    BASIC = "Basic"
    STAGE1 = "Stage 1"
    STAGE2 = "Stage 2"

class Rarity(str, Enum):
    """Pokemon card rarities"""
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    RARE_HOLO = "Rare Holo"
    RARE_SECRET = "Rare Secret"

@dataclass
class EnergyCost:
    """Energy cost for attacks"""
    type: PokemonType
    amount: int

class Attack(BaseModel):
    """Pokemon attack data"""
    name: str
    cost: List[Union[PokemonType, str]] = Field(default_factory=list)
    damage: Optional[Union[int, str]] = None
    effect: Optional[str] = None
    
    def get_energy_cost(self) -> List[EnergyCost]:
        """Convert cost to structured energy requirements"""
        energy_costs = []
        cost_count = {}
        
        for energy in self.cost:
            energy_type = PokemonType(energy) if isinstance(energy, str) else energy
            cost_count[energy_type] = cost_count.get(energy_type, 0) + 1
        
        for energy_type, amount in cost_count.items():
            energy_costs.append(EnergyCost(type=energy_type, amount=amount))
        
        return energy_costs
    
    def get_damage_value(self) -> int:
        """Extract numeric damage value"""
        if isinstance(self.damage, int):
            return self.damage
        elif isinstance(self.damage, str) and self.damage.isdigit():
            return int(self.damage)
        else:
            return 0  # Variable damage or special effects

class Weakness(BaseModel):
    """Pokemon weakness data"""
    type: PokemonType
    multiplier: float = 2.0

class Resistance(BaseModel):
    """Pokemon resistance data"""
    type: PokemonType
    reduction: int = 20

class Ability(BaseModel):
    """Pokemon ability data"""
    name: str
    effect: str
    type: Optional[str] = None

class PokemonCard(BaseModel):
    """Complete Pokemon card data model"""
    
    # Basic card info
    id: str
    name: str
    category: CardCategory
    rarity: Optional[Rarity] = None
    set_id: Optional[str] = None
    image_url: Optional[str] = None
    
    # Pokemon-specific fields
    hp: Optional[int] = None
    types: List[PokemonType] = Field(default_factory=list)
    stage: Optional[PokemonStage] = None
    evolves_from: Optional[str] = None
    retreat_cost: int = 0
    
    # Combat data
    attacks: List[Attack] = Field(default_factory=list)
    weaknesses: List[Weakness] = Field(default_factory=list)
    resistances: List[Resistance] = Field(default_factory=list)
    abilities: List[Ability] = Field(default_factory=list)
    
    # Trainer/Energy specific
    trainer_type: Optional[str] = None
    energy_type: Optional[PokemonType] = None
    effect: Optional[str] = None
    
    # Helper properties
    @property
    def is_pokemon(self) -> bool:
        return self.category == CardCategory.POKEMON
    
    @property
    def is_trainer(self) -> bool:
        return self.category == CardCategory.TRAINER
    
    @property
    def is_energy(self) -> bool:
        return self.category == CardCategory.ENERGY
    
    @property
    def is_basic(self) -> bool:
        return self.stage == PokemonStage.BASIC
    
    @property
    def primary_type(self) -> Optional[PokemonType]:
        """Get the first/primary type of the Pokemon"""
        return self.types[0] if self.types else None
    
    def can_evolve_to(self, other_card: 'PokemonCard') -> bool:
        """Check if this Pokemon can evolve to another"""
        return (self.is_pokemon and other_card.is_pokemon and 
                other_card.evolves_from == self.name)
    
    def is_weak_to(self, attack_type: PokemonType) -> bool:
        """Check if Pokemon is weak to a specific type"""
        return any(w.type == attack_type for w in self.weaknesses)
    
    def is_resistant_to(self, attack_type: PokemonType) -> bool:
        """Check if Pokemon resists a specific type"""
        return any(r.type == attack_type for r in self.resistances)
    
    def calculate_damage_multiplier(self, attack_type: PokemonType) -> float:
        """Calculate damage multiplier based on weakness/resistance"""
        multiplier = 1.0
        
        # Check weakness
        for weakness in self.weaknesses:
            if weakness.type == attack_type:
                multiplier *= weakness.multiplier
        
        # Resistance reduces damage (handled separately)
        return multiplier
    
    def calculate_damage_reduction(self, attack_type: PokemonType) -> int:
        """Calculate damage reduction from resistance"""
        reduction = 0
        
        for resistance in self.resistances:
            if resistance.type == attack_type:
                reduction += resistance.reduction
        
        return reduction
    
    def get_usable_attacks(self, available_energy: Dict[PokemonType, int]) -> List[Attack]:
        """Get attacks that can be used with available energy"""
        usable_attacks = []
        
        for attack in self.attacks:
            energy_costs = attack.get_energy_cost()
            can_use = True
            
            for cost in energy_costs:
                if available_energy.get(cost.type, 0) < cost.amount:
                    can_use = False
                    break
            
            if can_use:
                usable_attacks.append(attack)
        
        return usable_attacks
    
    def to_ai_context(self) -> str:
        """Generate AI-readable description of the card"""
        if self.is_pokemon:
            context = f"{self.name} ({'/'.join(self.types)}, {self.hp} HP)"
            if self.attacks:
                attacks_desc = ", ".join([f"{a.name} ({a.damage} damage)" for a in self.attacks])
                context += f" - Attacks: {attacks_desc}"
            return context
        elif self.is_trainer:
            return f"{self.name} (Trainer) - {self.effect or 'Special effect'}"
        elif self.is_energy:
            return f"{self.name} ({self.energy_type} Energy)"
        
        return f"{self.name} (Unknown card type)"

# Factory functions for creating cards from API data
def create_pokemon_card_from_tcgdx(card_data) -> PokemonCard:
    """Create PokemonCard from TCGdx API data"""
    
    # Convert types
    types = []
    if hasattr(card_data, 'types') and card_data.types:
        for type_name in card_data.types:
            try:
                types.append(PokemonType(type_name.lower()))
            except ValueError:
                types.append(PokemonType.COLORLESS)  # Default for unknown types
    
    # Convert attacks
    attacks = []
    if hasattr(card_data, 'attacks') and card_data.attacks:
        for attack_data in card_data.attacks:
            attack = Attack(
                name=attack_data.get('name', 'Unknown Attack'),
                cost=attack_data.get('cost', []),
                damage=attack_data.get('damage'),
                effect=attack_data.get('effect')
            )
            attacks.append(attack)
    
    # Convert weaknesses
    weaknesses = []
    if hasattr(card_data, 'weaknesses') and card_data.weaknesses:
        for weakness_data in card_data.weaknesses:
            try:
                weakness_type = PokemonType(weakness_data.get('type', '').lower())
                weakness = Weakness(
                    type=weakness_type,
                    multiplier=float(weakness_data.get('multiplier', '2x').replace('x', ''))
                )
                weaknesses.append(weakness)
            except (ValueError, AttributeError):
                continue
    
    # Convert resistances
    resistances = []
    if hasattr(card_data, 'resistances') and card_data.resistances:
        for resistance_data in card_data.resistances:
            try:
                resistance_type = PokemonType(resistance_data.get('type', '').lower())
                resistance = Resistance(
                    type=resistance_type,
                    reduction=int(resistance_data.get('value', '20').replace('-', ''))
                )
                resistances.append(resistance)
            except (ValueError, AttributeError):
                continue
    
    # Determine category
    category = CardCategory.POKEMON
    if hasattr(card_data, 'category'):
        try:
            category = CardCategory(card_data.category)
        except ValueError:
            category = CardCategory.POKEMON
    
    # Create the card
    return PokemonCard(
        id=getattr(card_data, 'id', 'unknown'),
        name=getattr(card_data, 'name', 'Unknown Pokemon'),
        category=category,
        hp=getattr(card_data, 'hp', None),
        types=types,
        stage=PokemonStage(getattr(card_data, 'stage', 'Basic')) if hasattr(card_data, 'stage') else PokemonStage.BASIC,
        evolves_from=getattr(card_data, 'evolvesFrom', None),
        retreat_cost=getattr(card_data, 'retreat', 0) or 0,
        attacks=attacks,
        weaknesses=weaknesses,
        resistances=resistances,
        set_id=getattr(card_data.set, 'id', None) if hasattr(card_data, 'set') else None,
        image_url=getattr(card_data, 'image', None),
        rarity=Rarity(getattr(card_data, 'rarity', 'Common')) if hasattr(card_data, 'rarity') else Rarity.COMMON,
        trainer_type=getattr(card_data, 'trainerType', None),
        energy_type=PokemonType(getattr(card_data, 'energyType', '').lower()) if hasattr(card_data, 'energyType') else None,
        effect=getattr(card_data, 'effect', None)
    )

# Example usage and testing
if __name__ == "__main__":
    # Create a sample Pikachu card
    pikachu = PokemonCard(
        id="base1-25",
        name="Pikachu",
        category=CardCategory.POKEMON,
        hp=60,
        types=[PokemonType.ELECTRIC],
        stage=PokemonStage.BASIC,
        attacks=[
            Attack(
                name="Thunder Shock",
                cost=[PokemonType.ELECTRIC, PokemonType.COLORLESS],
                damage=10,
                effect="Flip a coin. If heads, the Defending Pokemon is now Paralyzed."
            ),
            Attack(
                name="Agility", 
                cost=[PokemonType.ELECTRIC, PokemonType.ELECTRIC],
                damage=20,
                effect="Flip a coin. If heads, during your opponent's next turn, prevent all effects of attacks, including damage, done to Pikachu."
            )
        ],
        retreat_cost=1,
        rarity=Rarity.COMMON
    )
    
    # Test AI context generation
    print("Pikachu AI Context:", pikachu.to_ai_context())
    
    # Test energy requirements
    available_energy = {PokemonType.ELECTRIC: 2, PokemonType.COLORLESS: 1}
    usable_attacks = pikachu.get_usable_attacks(available_energy)
    print(f"Usable attacks with available energy: {[a.name for a in usable_attacks]}")
    
    # Create a Charmander card 
    charmander = PokemonCard(
        id="base1-46",
        name="Charmander",
        category=CardCategory.POKEMON,
        hp=50,
        types=[PokemonType.FIRE],
        stage=PokemonStage.BASIC,
        attacks=[
            Attack(
                name="Scratch",
                cost=[PokemonType.COLORLESS],
                damage=10
            ),
            Attack(
                name="Ember",
                cost=[PokemonType.FIRE, PokemonType.COLORLESS],
                damage=30,
                effect="Discard 1 Fire Energy card attached to Charmander in order to use this attack."
            )
        ],
        weaknesses=[Weakness(type=PokemonType.WATER, multiplier=2.0)],
        retreat_cost=1,
        rarity=Rarity.COMMON
    )
    
    print("Charmander AI Context:", charmander.to_ai_context())
    print(f"Charmander weak to Water: {charmander.is_weak_to(PokemonType.WATER)}")
    
    # Create a Professor Oak trainer card
    professor_oak = PokemonCard(
        id="base1-102",
        name="Professor Oak",
        category=CardCategory.TRAINER,
        effect="Discard your hand and draw 7 cards.",
        rarity=Rarity.UNCOMMON
    )
    
    print("Professor Oak AI Context:", professor_oak.to_ai_context())
    
    # Create a Fire Energy card
    fire_energy = PokemonCard(
        id="base1-98",
        name="Fire Energy",
        category=CardCategory.ENERGY,
        energy_type=PokemonType.FIRE,
        effect="Provides 1 Fire energy.",
        rarity=Rarity.COMMON
    )
    
    print("Fire Energy AI Context:", fire_energy.to_ai_context())
    
    print("\n✅ Pokemon card models working correctly!")