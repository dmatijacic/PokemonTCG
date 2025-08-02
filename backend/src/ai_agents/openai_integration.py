# backend/src/ai_agents/openai_integration.py
"""
OpenAI Integration for Pokemon AI
Ensures proper GPT model communication
"""

import os
import asyncio
from typing import Dict, Any, Optional
from openai import OpenAI

class PokemonOpenAIClient:
    """
    Handles OpenAI API communication for Pokemon AI
    """
    
    def __init__(self):
        self.client = None
        self.api_key = None
        self.model = "gpt-4o-mini"  # Best value model
        self.is_available = False
        
        self._initialize()
    
    def _initialize(self):
        """Initialize OpenAI client"""
        try:
            # Get API key
            self.api_key = os.getenv("OPENAI_API_KEY")
            
            if not self.api_key:
                print("⚠️  No OPENAI_API_KEY found - Pokemon AI will run in demo mode")
                return
            
            if not self.api_key.startswith("sk-"):
                print("⚠️  Invalid API key format - Pokemon AI will run in demo mode")
                return
            
            # Initialize client
            self.client = OpenAI(api_key=self.api_key)
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            print(f"⚠️  OpenAI initialization failed: {e}")
            self.is_available = False
    
    def _test_connection(self):
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Pokemon expert."},
                    {"role": "user", "content": "Say 'Pokemon AI Ready' if you can hear me."}
                ],
                max_tokens=10
            )
            
            if response.choices[0].message.content:
                self.is_available = True
                print(f"✅ OpenAI GPT-4o-mini connected successfully!")
                print(f"🎮 Pokemon AI will use real GPT intelligence")
            else:
                print("⚠️  OpenAI responded but with empty content")
                
        except Exception as e:
            print(f"⚠️  OpenAI connection test failed: {e}")
            self.is_available = False
    
    async def get_pokemon_ai_response(self, system_prompt: str, user_message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Get AI response for Pokemon gameplay
        """
        if not self.is_available:
            return None
        
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 300),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9)
            )
            
            # Extract response
            ai_text = response.choices[0].message.content
            
            # Log usage for cost tracking
            usage = response.usage
            cost = (usage.prompt_tokens * 0.00015 + usage.completion_tokens * 0.0006) / 1000
            
            print(f"🤖 GPT Response: {ai_text[:100]}...")
            print(f"📊 Tokens: {usage.total_tokens}, Cost: ${cost:.6f}")
            
            return {
                "response": ai_text,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "cost": cost,
                "model": self.model
            }
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current OpenAI integration status"""
        return {
            "available": self.is_available,
            "model": self.model,
            "api_key_configured": bool(self.api_key),
            "api_key_format_valid": self.api_key.startswith("sk-") if self.api_key else False
        }

# Global instance
pokemon_openai = PokemonOpenAIClient()

