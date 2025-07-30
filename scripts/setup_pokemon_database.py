# scripts/setup_pokemon_database.py
"""
Pokemon TCG Database Setup Script
Initializes Pokemon card database for LLM education platform
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add backend to Python path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from tcgdexsdk import TCGdex  # Fixed import name
import time

class PokemonDatabaseSetup:
    """Setup Pokemon card database for AI education"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.assets_dir = self.base_dir / "assets" / "cards"
        self.data_dir = self.assets_dir / "data"
        self.images_dir = self.assets_dir / "images"
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        self.tcgdx = TCGdex("en")  # Fixed class name
    
    def create_type_chart(self):
        """Create comprehensive Pokemon type effectiveness chart"""
        print("📊 Creating Pokemon type effectiveness chart...")
        
        type_chart = {
            "normal": {
                "rock": 0.5,
                "ghost": 0,
                "steel": 0.5
            },
            "fire": {
                "fire": 0.5,
                "water": 0.5,
                "grass": 2,
                "ice": 2,
                "bug": 2,
                "rock": 0.5,
                "dragon": 0.5,
                "steel": 2
            },
            "water": {
                "fire": 2,
                "water": 0.5,
                "grass": 0.5,
                "ground": 2,
                "rock": 2,
                "dragon": 0.5
            },
            "electric": {
                "water": 2,
                "electric": 0.5,
                "grass": 0.5,
                "ground": 0,
                "flying": 2,
                "dragon": 0.5
            },
            "grass": {
                "fire": 0.5,
                "water": 2,
                "grass": 0.5,
                "poison": 0.5,
                "ground": 2,
                "rock": 2,
                "bug": 0.5,
                "dragon": 0.5,
                "steel": 0.5,
                "flying": 0.5
            },
            "ice": {
                "fire": 0.5,
                "water": 0.5,
                "grass": 2,
                "ice": 0.5,
                "ground": 2,
                "flying": 2,
                "dragon": 2,
                "steel": 0.5
            },
            "fighting": {
                "normal": 2,
                "ice": 2,
                "poison": 0.5,
                "flying": 0.5,
                "psychic": 0.5,
                "bug": 0.5,
                "rock": 2,
                "ghost": 0,
                "dark": 2,
                "steel": 2,
                "fairy": 0.5
            },
            "poison": {
                "grass": 2,
                "poison": 0.5,
                "ground": 0.5,
                "rock": 0.5,
                "ghost": 0.5,
                "steel": 0,
                "fairy": 2
            },
            "ground": {
                "fire": 2,
                "electric": 2,
                "grass": 0.5,
                "poison": 2,
                "flying": 0,
                "bug": 0.5,
                "rock": 2,
                "steel": 2
            },
            "flying": {
                "electric": 0.5,
                "grass": 2,
                "ice": 0.5,
                "fighting": 2,
                "bug": 2,
                "rock": 0.5,
                "steel": 0.5
            },
            "psychic": {
                "fighting": 2,
                "poison": 2,
                "psychic": 0.5,
                "dark": 0,
                "steel": 0.5
            },
            "bug": {
                "fire": 0.5,
                "grass": 2,
                "fighting": 0.5,
                "poison": 0.5,
                "flying": 0.5,
                "psychic": 2,
                "ghost": 0.5,
                "dark": 2,
                "steel": 0.5,
                "fairy": 0.5
            },
            "rock": {
                "fire": 2,
                "ice": 2,
                "fighting": 0.5,
                "ground": 0.5,
                "flying": 2,
                "bug": 2,
                "steel": 0.5
            },
            "ghost": {
                "normal": 0,
                "psychic": 2,
                "ghost": 2,
                "dark": 0.5
            },
            "dragon": {
                "dragon": 2,
                "steel": 0.5,
                "fairy": 0
            },
            "dark": {
                "fighting": 0.5,
                "psychic": 2,
                "ghost": 2,
                "dark": 0.5,
                "fairy": 0.5
            },
            "steel": {
                "fire": 0.5,
                "water": 0.5,
                "electric": 0.5,
                "ice": 2,
                "rock": 2,
                "steel": 0.5,
                "fairy": 2
            },
            "fairy": {
                "fire": 0.5,
                "fighting": 2,
                "poison": 0.5,
                "dragon": 2,
                "dark": 2,
                "steel": 0.5
            }
        }
        
        # Save type chart
        type_chart_file = self.data_dir / "type_chart.json"
        with open(type_chart_file, 'w') as f:
            json.dump(type_chart, f, indent=2)
        
        print(f"✅ Type chart saved to {type_chart_file}")
        return type_chart
    
    def create_starter_decks(self):
        """Create pre-built starter decks for learning"""
        print("🎮 Creating Pokemon starter decks...")
        
        starter_decks = {
            "fire_starter": {
                "name": "Fire Starter Deck",
                "description": "Learn Pokemon with fire types",
                "pokemon": [
                    {"name": "Charmander", "count": 4},
                    {"name": "Charmeleon", "count": 2},
                    {"name": "Charizard", "count": 1},
                    {"name": "Growlithe", "count": 3},
                    {"name": "Arcanine", "count": 2}
                ],
                "energy": [
                    {"type": "fire", "count": 20}
                ],
                "trainers": [
                    {"name": "Professor Oak", "count": 4},
                    {"name": "Potion", "count": 4},
                    {"name": "Switch", "count": 2}
                ]
            },
            "water_starter": {
                "name": "Water Starter Deck", 
                "description": "Learn Pokemon with water types",
                "pokemon": [
                    {"name": "Squirtle", "count": 4},
                    {"name": "Wartortle", "count": 2},
                    {"name": "Blastoise", "count": 1},
                    {"name": "Psyduck", "count": 3},
                    {"name": "Golduck", "count": 2}
                ],
                "energy": [
                    {"type": "water", "count": 20}
                ],
                "trainers": [
                    {"name": "Professor Oak", "count": 4},
                    {"name": "Potion", "count": 4},
                    {"name": "Switch", "count": 2}
                ]
            },
            "grass_starter": {
                "name": "Grass Starter Deck",
                "description": "Learn Pokemon with grass types", 
                "pokemon": [
                    {"name": "Bulbasaur", "count": 4},
                    {"name": "Ivysaur", "count": 2},
                    {"name": "Venusaur", "count": 1},
                    {"name": "Oddish", "count": 3},
                    {"name": "Gloom", "count": 2}
                ],
                "energy": [
                    {"type": "grass", "count": 20}
                ],
                "trainers": [
                    {"name": "Professor Oak", "count": 4},
                    {"name": "Potion", "count": 4},
                    {"name": "Switch", "count": 2}
                ]
            },
            "mixed_beginner": {
                "name": "Mixed Beginner Deck",
                "description": "Learn type advantages with mixed types",
                "pokemon": [
                    {"name": "Pikachu", "count": 3},
                    {"name": "Charmander", "count": 2},
                    {"name": "Squirtle", "count": 2},
                    {"name": "Bulbasaur", "count": 2},
                    {"name": "Eevee", "count": 3}
                ],
                "energy": [
                    {"type": "electric", "count": 8},
                    {"type": "fire", "count": 6},
                    {"type": "water", "count": 6}
                ],
                "trainers": [
                    {"name": "Professor Oak", "count": 4},
                    {"name": "Potion", "count": 6}
                ]
            }
        }
        
        # Save starter decks
        decks_file = self.data_dir / "starter_decks.json"
        with open(decks_file, 'w') as f:
            json.dump(starter_decks, f, indent=2)
        
        print(f"✅ Starter decks saved to {decks_file}")
        return starter_decks
    
    def _serialize_tcgdx_object(self, obj):
        """Convert tcgdexsdk objects to JSON-serializable format"""
        if obj is None:
            return None
        
        if isinstance(obj, (str, int, float, bool)):
            return obj
        
        if isinstance(obj, list):
            return [self._serialize_tcgdx_object(item) for item in obj]
        
        if isinstance(obj, dict):
            return {k: self._serialize_tcgdx_object(v) for k, v in obj.items()}
        
        # Handle custom objects by converting to dict
        if hasattr(obj, '__dict__'):
            return self._serialize_tcgdx_object(vars(obj))
        
        # Fallback to string representation
        return str(obj)
    
    def download_essential_cards(self):
        """Download essential Pokemon cards for education"""
        print("📦 Downloading essential Pokemon cards...")
        
        essential_cards = [
            # Original starters
            "base1-46",  # Charmander
            "base1-58",  # Squirtle  
            "base1-44",  # Bulbasaur
            "base1-25",  # Pikachu
            
            # Evolutions
            "base1-5",   # Charmeleon
            "base1-4",   # Charizard
            "base1-42",  # Wartortle
            "base1-2",   # Blastoise
            "base1-43",  # Ivysaur
            "base1-15",  # Venusaur
            
            # Popular Pokemon
            "base1-51",  # Eevee
            "base1-56",  # Psyduck
            "base1-16",  # Zapdos
            "base1-32",  # Kadabra
        ]
        
        downloaded = 0
        failed = 0
        
        for card_id in essential_cards:
            try:
                print(f"  Downloading {card_id}...")
                card_data = self.tcgdx.card.getSync(card_id)
                print(f"  ✅ Downloaded {card_data.name} ({card_id})")
                
                # Convert to serializable format
                serializable_data = {
                    "id": getattr(card_data, 'id', card_id),
                    "name": getattr(card_data, 'name', 'Unknown'),
                    "types": self._serialize_tcgdx_object(getattr(card_data, 'types', [])),
                    "hp": getattr(card_data, 'hp', None),
                    "attacks": self._serialize_tcgdx_object(getattr(card_data, 'attacks', [])),
                    "weaknesses": self._serialize_tcgdx_object(getattr(card_data, 'weaknesses', [])),
                    "resistances": self._serialize_tcgdx_object(getattr(card_data, 'resistances', [])),
                    "image": getattr(card_data, 'image', None),
                    "category": getattr(card_data, 'category', 'Pokemon'),
                    "stage": getattr(card_data, 'stage', None),
                    "evolves_from": getattr(card_data, 'evolvesFrom', None),
                    "retreat": getattr(card_data, 'retreat', None),
                    "rarity": getattr(card_data, 'rarity', None),
                    "set": getattr(card_data.set, 'id', None) if hasattr(card_data, 'set') else None
                }
                
                # Save card data
                card_file = self.data_dir / f"{card_id}.json"
                print(f"  💾 Saving to {card_file}")
                
                with open(card_file, 'w', encoding='utf-8') as f:
                    json.dump(serializable_data, f, indent=2, ensure_ascii=False)
                
                downloaded += 1
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  ❌ Failed to download {card_id}: {e}")
                print(f"     Error details: {type(e).__name__}")
                failed += 1
                continue
        
        print(f"✅ Downloaded {downloaded} cards, {failed} failed")
        return downloaded
    
    def create_ai_training_data(self):
        """Create training scenarios for AI agents"""
        print("🤖 Creating AI training scenarios...")
        
        training_scenarios = {
            "type_advantage_basics": {
                "description": "Learn basic type advantages",
                "scenarios": [
                    {
                        "situation": "Fire Pokemon vs Grass Pokemon",
                        "explanation": "Fire beats Grass - Fire attacks do double damage",
                        "example": "Charmander's Ember vs Bulbasaur"
                    },
                    {
                        "situation": "Water Pokemon vs Fire Pokemon", 
                        "explanation": "Water beats Fire - Water attacks do double damage",
                        "example": "Squirtle's Water Gun vs Charmander"
                    },
                    {
                        "situation": "Grass Pokemon vs Water Pokemon",
                        "explanation": "Grass beats Water - Grass attacks do double damage", 
                        "example": "Bulbasaur's Vine Whip vs Squirtle"
                    }
                ]
            },
            "strategic_thinking": {
                "description": "AI strategic decision examples",
                "scenarios": [
                    {
                        "situation": "Low HP Pokemon active",
                        "ai_decision": "Retreat to bench and bring out healthy Pokemon",
                        "explanation": "AI calculates survival probability and switches"
                    },
                    {
                        "situation": "Multiple energy available",
                        "ai_decision": "Use powerful attack even if it requires more energy",
                        "explanation": "AI weighs damage output vs energy cost"
                    }
                ]
            }
        }
        
        training_file = self.data_dir / "ai_training_scenarios.json"
        with open(training_file, 'w') as f:
            json.dump(training_scenarios, f, indent=2)
        
        print(f"✅ AI training scenarios saved to {training_file}")
        return training_scenarios
    
    def setup_complete_database(self):
        """Run complete Pokemon database setup"""
        print("🎮 Setting up Pokemon TCG LLM Education Database...")
        print("=" * 60)
        
        try:
            # Create core data files
            type_chart = self.create_type_chart()
            starter_decks = self.create_starter_decks()
            ai_scenarios = self.create_ai_training_data()
            
            # Download essential cards
            cards_downloaded = self.download_essential_cards()
            
            # Create summary
            summary = {
                "setup_completed": True,
                "setup_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "components": {
                    "type_chart": True,
                    "starter_decks": len(starter_decks),
                    "ai_scenarios": len(ai_scenarios),
                    "cards_downloaded": cards_downloaded
                },
                "ready_for_ai": True,
                "ready_for_gameplay": True
            }
            
            summary_file = self.data_dir / "setup_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print("\n" + "=" * 60)
            print("✅ Pokemon TCG LLM Education Database Setup Complete!")
            print(f"📊 Type effectiveness chart: Ready")
            print(f"🎮 Starter decks: {len(starter_decks)} decks created")
            print(f"🤖 AI training scenarios: {len(ai_scenarios)} scenario sets")
            print(f"📦 Essential cards: {cards_downloaded} downloaded")
            print(f"📄 Setup summary: {summary_file}")
            print("\n🚀 Ready for Pokemon AI development!")
            
            return summary
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return None

def main():
    """Main setup function"""
    setup = PokemonDatabaseSetup()
    result = setup.setup_complete_database()
    
    if result:
        print("\n🎯 Next steps:")
        print("1. Start VS Code devcontainer")
        print("2. Run Pokemon game server: python backend/main.py")
        print("3. Begin Pokemon AI agent development")
        return 0
    else:
        print("❌ Setup failed - check error messages above")
        return 1

if __name__ == "__main__":
    exit(main())