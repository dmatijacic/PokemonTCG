# scripts/generate_card_database.py
"""
Integrated script for downloading Pokemon TCG card data and images.
This script is kept as reference/template - will be removed during migration to LLM platform.

Features:
- Optional set selection (not just base1)
- Filtered data (only game-relevant fields)
- Combined data + image download
- Error handling and progress tracking
"""

import os
import json
import requests
from tcgdexsdk import TCGdex
from typing import List, Dict, Optional, Set
import argparse
from pathlib import Path
import time

class CardDatabaseGenerator:
    """Generate filtered card database with images"""
    
    def __init__(self, dest_dir: str = "assets/cards"):
        self.dest_dir = Path(dest_dir)
        self.images_dir = self.dest_dir / "images"
        self.data_dir = self.dest_dir / "data"
        
        # Create directories
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize TCGdex
        self.tcgdx = TCGdex("en")
        
        # Define game-relevant fields only
        self.relevant_fields = {
            # Core game fields
            "id", "localId", "name", "image",
            "hp", "types", "category", "rarity",
            
            # Pokemon-specific
            "level", "stage", "evolvesFrom",
            "abilities", "attacks", 
            "weaknesses", "resistances", "retreat",
            
            # Trainer cards
            "trainerType", "effect",
            
            # Energy cards  
            "energyType",
            
            # Set info
            "set"
        }
    
    def get_available_sets(self) -> List[Dict]:
        """Get list of available TCG sets"""
        try:
            sets = self.tcgdx.set.listSync()
            return [{"id": s.id, "name": s.name} for s in sets]
        except Exception as e:
            print(f"Error fetching sets: {e}")
            return []
    
    def list_sets(self):
        """Print available sets for user selection"""
        print("Available Pokemon TCG Sets:")
        print("-" * 50)
        
        sets = self.get_available_sets()
        for set_info in sets[:20]:  # Show first 20 sets
            print(f"{set_info['id']:<15} {set_info['name']}")
        
        if len(sets) > 20:
            print(f"... and {len(sets) - 20} more sets")
        
        print(f"\nTotal sets available: {len(sets)}")
    
    def make_serializable(self, obj, seen: Optional[Set] = None) -> any:
        """Convert complex objects to JSON-serializable format"""
        if seen is None:
            seen = set()

        obj_id = id(obj)
        if obj_id in seen:
            return str(obj)
        seen.add(obj_id)

        if isinstance(obj, dict):
            return {k: self.make_serializable(v, seen) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple, set)):
            return [self.make_serializable(i, seen) for i in obj]
        elif hasattr(obj, '__dict__'):
            return self.make_serializable(vars(obj), seen)
        elif hasattr(obj, '_asdict'):
            return self.make_serializable(obj._asdict(), seen)
        elif isinstance(obj, str):
            return obj.replace("\u00d7", "x")  # Replace Unicode multiply
        elif isinstance(obj, (int, float, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    def filter_card_data(self, card_data) -> Dict:
        """Filter card data to only include game-relevant fields"""
        filtered = {}
        
        for field in self.relevant_fields:
            value = getattr(card_data, field, None)
            
            # Special handling for set info
            if field == "set" and hasattr(card_data, "set"):
                filtered[field] = getattr(card_data.set, "id", None)
            else:
                filtered[field] = self.make_serializable(value)
        
        # Add derived/computed fields useful for games
        filtered["is_pokemon"] = filtered.get("category") == "Pokemon"
        filtered["is_trainer"] = filtered.get("category") == "Trainer"
        filtered["is_energy"] = filtered.get("category") == "Energy"
        
        # Simplify attacks for game logic
        if filtered.get("attacks"):
            simplified_attacks = []
            for attack in filtered["attacks"]:
                if isinstance(attack, dict):
                    simplified_attacks.append({
                        "name": attack.get("name"),
                        "cost": attack.get("cost", []),
                        "damage": attack.get("damage"),
                        "effect": attack.get("effect")
                    })
            filtered["attacks"] = simplified_attacks
        
        return filtered
    
    def download_card_image(self, card_id: str, image_url: str) -> bool:
        """Download single card image"""
        try:
            image_path = self.images_dir / f"{card_id}.png"
            
            # Skip if already exists
            if image_path.exists():
                return True
            
            # Add high quality suffix if not present
            if not image_url.endswith("/high.png"):
                image_url = image_url.rstrip("/") + "/high.png"
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(image_path, "wb") as f:
                f.write(response.content)
            
            return True
            
        except Exception as e:
            print(f"Failed to download image for {card_id}: {e}")
            return False
    
    def generate_set_database(self, set_ids: List[str], download_images: bool = True) -> Dict:
        """Generate database for specified sets"""
        all_cards = []
        total_downloaded = 0
        total_failed = 0
        
        for set_id in set_ids:
            print(f"\nProcessing set: {set_id}")
            
            try:
                # Get set data
                tcg_set = self.tcgdx.set.getSync(set_id)
                card_resumes = tcg_set.cards
                
                print(f"Found {len(card_resumes)} cards in {set_id}")
                
                for i, card_resume in enumerate(card_resumes, 1):
                    try:
                        # Get detailed card data
                        card_data = self.tcgdx.card.getSync(card_resume.id)
                        
                        # Filter to relevant fields
                        filtered_card = self.filter_card_data(card_data)
                        all_cards.append(filtered_card)
                        
                        # Download image if requested
                        if download_images and filtered_card.get("image"):
                            success = self.download_card_image(
                                filtered_card["id"], 
                                filtered_card["image"]
                            )
                            if success:
                                total_downloaded += 1
                            else:
                                total_failed += 1
                        
                        # Progress indicator
                        if i % 10 == 0:
                            print(f"  Processed {i}/{len(card_resumes)} cards...")
                        
                        # Rate limiting
                        time.sleep(0.1)
                        
                    except Exception as e:
                        print(f"Error processing card {card_resume.id}: {e}")
                        total_failed += 1
                        continue
                
            except Exception as e:
                print(f"Error processing set {set_id}: {e}")
                continue
        
        # Save combined database
        database = {
            "metadata": {
                "sets": set_ids,
                "total_cards": len(all_cards),
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "images_downloaded": total_downloaded,
                "images_failed": total_failed
            },
            "cards": all_cards
        }
        
        # Save to file
        output_file = self.data_dir / "database.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Database saved to: {output_file}")
        print(f"📊 Total cards: {len(all_cards)}")
        print(f"🖼️  Images downloaded: {total_downloaded}")
        print(f"❌ Failed downloads: {total_failed}")
        
        return database

def main():
    parser = argparse.ArgumentParser(description="Generate Pokemon TCG card database")
    parser.add_argument("--sets", nargs="+", default=["base1"], 
                       help="Set IDs to download (default: base1)")
    parser.add_argument("--list-sets", action="store_true",
                       help="List available sets and exit")
    parser.add_argument("--no-images", action="store_true",
                       help="Skip image downloads")
    parser.add_argument("--dest", default="assets/cards",
                       help="Destination directory (default: assets/cards)")
    
    args = parser.parse_args()
    
    generator = CardDatabaseGenerator(args.dest)
    
    if args.list_sets:
        generator.list_sets()
        return
    
    print(f"Generating database for sets: {args.sets}")
    print(f"Download images: {not args.no_images}")
    print(f"Destination: {args.dest}")
    
    database = generator.generate_set_database(
        args.sets, 
        download_images=not args.no_images
    )
    
    print(f"\n🎉 Database generation complete!")

if __name__ == "__main__":
    main()

# Example usage:
# 
# List available sets:
# python scripts/generate_card_database.py --list-sets
#
# Download base1 set only (original behavior):
# python scripts/generate_card_database.py --sets base1
#
# Download multiple sets:
# python scripts/generate_card_database.py --sets base1 jungle fossil
#
# Download without images (data only):
# python scripts/generate_card_database.py --sets base1 --no-images
#
# Custom destination:
# python scripts/generate_card_database.py --sets base1 --dest /custom/path