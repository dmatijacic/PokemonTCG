# backend/src/config/pokemon_model_config.py
"""
Corrected Pokemon AI Model Configuration - Updated with accurate pricing
"""

POKEMON_AI_MODELS = {
    # DEVELOPMENT - Use the cheapest, best models
    "development": {
        "pokemon_opponent": "gpt-4o-mini",      # Cheapest + great performance
        "pokemon_teacher": "gpt-4o-mini",       # Perfect for educational content
        "pokemon_helper": "gpt-4o-mini",        # Excellent for hints/encouragement
        "cost_per_1k_tokens": 0.0003,           # Average of input/output
        "daily_budget": 2.00                    # Very affordable for development
    },
    
    # PRODUCTION - Still use cheap models, maybe mix in Claude for variety
    "production": {
        "pokemon_opponent": "gpt-4o-mini",           # Still cheapest option!
        "pokemon_teacher": "claude-3-haiku-20240307", # Mix for variety
        "pokemon_helper": "gpt-4o-mini",             # Stick with cheap + good
        "cost_per_1k_tokens": 0.0004,               # Slightly higher with Claude mix
        "daily_budget": 3.00                        # Still very affordable
    }
}

# Updated cost calculations (corrected)
ACCURATE_MODEL_PRICING = {
    "gpt-4o-mini": {
        "input": 0.00015,   # $0.15 per 1M tokens
        "output": 0.0006,   # $0.60 per 1M tokens
        "notes": "🏆 BEST VALUE - Cheapest + excellent quality"
    },
    "gpt-3.5-turbo": {
        "input": 0.0015,    # $1.50 per 1M tokens (10x more expensive!)
        "output": 0.002,    # $2.00 per 1M tokens
        "notes": "❌ AVOID - More expensive, worse performance than GPT-4o-mini"
    },
    "claude-3-haiku-20240307": {
        "input": 0.00025,   # $0.25 per 1M tokens  
        "output": 0.00125,  # $1.25 per 1M tokens
        "notes": "✅ GOOD - Slightly more than GPT-4o-mini but good variety"
    }
}

def get_pokemon_cost_estimate(games_per_day: int = 10, tokens_per_game: int = 2000):
    """
    Estimate daily costs for Pokemon AI with corrected pricing
    """
    estimates = {}
    
    for model_name, pricing in ACCURATE_MODEL_PRICING.items():
        # Average cost per token (input + output)
        avg_cost_per_token = (pricing["input"] + pricing["output"]) / 2
        
        # Daily cost calculation
        daily_tokens = games_per_day * tokens_per_game
        daily_cost = daily_tokens * avg_cost_per_token
        
        estimates[model_name] = {
            "daily_cost": daily_cost,
            "monthly_cost": daily_cost * 30,
            "cost_per_game": daily_cost / games_per_day,
            "recommendation": pricing["notes"]
        }
    
    return estimates

# Example cost estimates
if __name__ == "__main__":
    print("🎮 Pokemon AI Cost Estimates (10 games/day, 2K tokens/game):")
    print("=" * 60)
    
    estimates = get_pokemon_cost_estimate()
    
    for model, data in estimates.items():
        print(f"\n{model}:")
        print(f"  Daily cost: ${data['daily_cost']:.4f}")
        print(f"  Monthly cost: ${data['monthly_cost']:.2f}")
        print(f"  Cost per Pokemon game: ${data['cost_per_game']:.4f}")
        print(f"  {data['recommendation']}")
    
    print(f"\n🏆 WINNER: GPT-4o-mini")
    print(f"   - Cheapest option at ~${estimates['gpt-4o-mini']['daily_cost']:.2f}/day")
    print(f"   - Better performance than GPT-3.5-turbo")
    print(f"   - Perfect for Pokemon AI education!")
    
    print(f"\n💡 Your Pokemon project monthly cost with GPT-4o-mini:")
    print(f"   Development: ~${estimates['gpt-4o-mini']['monthly_cost']:.2f}/month")
    print(f"   Production: ~${estimates['gpt-4o-mini']['monthly_cost'] * 1.5:.2f}/month")