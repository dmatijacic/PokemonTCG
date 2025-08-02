#!/usr/bin/env python3
# start_pokemon_backend.py - Fixed startup script

import os
import sys
from pathlib import Path

def load_environment():
    """Load environment variables properly"""
    try:
        from dotenv import load_dotenv
        
        # Load from .env file with override
        loaded = load_dotenv(override=True)
        print(f"✅ Environment loaded: {loaded}")
        
        # Verify API key
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.startswith("sk-"):
            print(f"🔑 OpenAI API Key: {api_key[:15]}...{api_key[-4:]}")
            return True
        else:
            print("⚠️  OpenAI API Key not found or invalid")
            return False
            
    except ImportError:
        print("❌ python-dotenv not installed")
        return False
    except Exception as e:
        print(f"❌ Environment loading error: {e}")
        return False

if __name__ == "__main__":
    print("🎮 Starting Pokemon TCG AI Backend with Fixed Environment...")
    
    # Load environment first
    env_loaded = load_environment()
    
    # Start the backend
    try:
        import subprocess
        subprocess.run([sys.executable, "backend/main.py"])
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")
