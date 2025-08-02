#!/usr/bin/env python3
# scripts/setup_backend_connection.py
"""
Setup script for connecting Pokemon frontend to backend
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔧 Checking requirements for Pokemon AI backend connection...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("❌ Python 3.8+ required")
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check if backend directory exists
    backend_dir = Path("backend")
    if not backend_dir.exists():
        issues.append("❌ Backend directory not found")
    else:
        print("✅ Backend directory found")
    
    # Check if frontend directory exists
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        issues.append("❌ Frontend directory not found")
    else:
        print("✅ Frontend directory found")
    
    # Check for requirements.txt
    requirements_file = backend_dir / "requirements.txt"
    if not requirements_file.exists():
        issues.append("❌ Backend requirements.txt not found")
    else:
        print("✅ Backend requirements.txt found")
    
    # Check for package.json
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        issues.append("❌ Frontend package.json not found")
    else:
        print("✅ Frontend package.json found")
    
    return issues

def install_backend_dependencies():
    """Install Python backend dependencies"""
    print("\n📦 Installing Python backend dependencies...")
    
    try:
        # Install backend requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
        ], check=True)
        print("✅ Backend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install backend dependencies: {e}")
        return False

def install_frontend_dependencies():
    """Install Node.js frontend dependencies"""
    print("\n📦 Installing Node.js frontend dependencies...")
    
    try:
        # Check if npm is available
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        
        # Install frontend dependencies
        subprocess.run(["npm", "install"], cwd="frontend", check=True)
        print("✅ Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        print("💡 Make sure Node.js and npm are installed")
        return False
    except FileNotFoundError:
        print("❌ npm not found - please install Node.js")
        return False

def setup_pokemon_database():
    """Setup Pokemon card database"""
    print("\n🎮 Setting up Pokemon card database...")
    
    try:
        subprocess.run([
            sys.executable, "scripts/setup_pokemon_database.py"
        ], check=True)
        print("✅ Pokemon database setup complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Pokemon database setup had issues: {e}")
        print("🔄 Game will run in demo mode")
        return False
    except FileNotFoundError:
        print("⚠️  Pokemon database setup script not found")
        print("🔄 Game will run in demo mode")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\n🔧 Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            # Copy from example
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                content = src.read()
                # Set development defaults
                content = content.replace("ENVIRONMENT=development", "ENVIRONMENT=development")
                content = content.replace("DEBUG=true", "DEBUG=true")
                dst.write(content)
            print("✅ Created .env file from .env.example")
        else:
            # Create basic .env
            with open(env_file, 'w') as f:
                f.write("""# Pokemon TCG AI Education Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# AI Model Keys (optional for demo)
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
""")
            print("✅ Created basic .env file")
    else:
        print("✅ .env file already exists")

def test_backend_imports():
    """Test if backend AI components can be imported"""
    print("\n🤖 Testing Pokemon AI components...")
    
    try:
        # Test imports
        sys.path.append("backend")
        
        from backend.src.models.pokemon_card import PokemonCard, PokemonType
        from backend.src.game.type_advantages import PokemonTypeCalculator
        from backend.src.ai_agents.opponent_ai import PokemonOpponentAI
        
        # Test basic functionality
        calc = PokemonTypeCalculator()
        effectiveness = calc.get_effectiveness(PokemonType.FIRE, PokemonType.GRASS)
        
        if effectiveness == 2.0:
            print("✅ Pokemon AI components working correctly")
            return True
        else:
            print("⚠️  Pokemon AI components loaded but may have issues")
            return False
            
    except ImportError as e:
        print(f"⚠️  Pokemon AI components not fully available: {e}")
        print("🔄 Backend will run in demo mode")
        return False
    except Exception as e:
        print(f"⚠️  Error testing Pokemon AI: {e}")
        return False

def generate_startup_scripts():
    """Generate convenient startup scripts"""
    print("\n📝 Generating startup scripts...")
    
    # Backend startup script
    backend_script = Path("start_backend.py")
    with open(backend_script, 'w') as f:
        f.write("""#!/usr/bin/env python3
# Auto-generated Pokemon backend startup script
import subprocess
import sys

print("🎮 Starting Pokemon TCG AI Backend Server...")
subprocess.run([sys.executable, "backend/main.py"])
""")
    backend_script.chmod(0o755)
    print("✅ Created start_backend.py")
    
    # Frontend startup script (bash)
    frontend_script = Path("start_frontend.sh")
    with open(frontend_script, 'w') as f:
        f.write("""#!/bin/bash
# Auto-generated Pokemon frontend startup script
echo "🎮 Starting Pokemon TCG AI Frontend..."
cd frontend
npm run dev
""")
    frontend_script.chmod(0o755)
    print("✅ Created start_frontend.sh")
    
    # Combined startup script
    combined_script = Path("start_pokemon_game.py")
    with open(combined_script, 'w') as f:
        f.write("""#!/usr/bin/env python3
# Auto-generated Pokemon game startup script
import subprocess
import sys
import time
import threading

def start_backend():
    print("🤖 Starting Pokemon AI Backend...")
    subprocess.run([sys.executable, "backend/main.py"])

def start_frontend():
    time.sleep(3)  # Wait for backend to start
    print("🎮 Starting Pokemon Frontend...")
    subprocess.run(["npm", "run", "dev"], cwd="frontend")

if __name__ == "__main__":
    print("🎮 Starting Complete Pokemon TCG AI Education Platform...")
    
    # Start backend in background thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend (this will block)
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\\n🛑 Shutting down Pokemon game...")
""")
    combined_script.chmod(0o755)
    print("✅ Created start_pokemon_game.py")

def main():
    """Main setup function"""
    print("🎮 Pokemon TCG AI Education Platform Setup")
    print("=" * 50)
    
    # Check requirements
    issues = check_requirements()
    if issues:
        print("\n❌ Setup issues found:")
        for issue in issues:
            print(f"  {issue}")
        print("\n🔧 Please resolve these issues and run setup again")
        return 1
    
    # Install dependencies
    backend_success = install_backend_dependencies()
    frontend_success = install_frontend_dependencies()
    
    if not (backend_success and frontend_success):
        print("\n❌ Dependency installation failed")
        return 1
    
    # Setup environment
    create_env_file()
    
    # Setup Pokemon database
    setup_pokemon_database()
    
    # Test AI components
    ai_working = test_backend_imports()
    
    # Generate startup scripts
    generate_startup_scripts()
    
    print("\n" + "=" * 50)
    print("✅ Pokemon TCG AI Education Platform Setup Complete!")
    print("\n🚀 To start the game:")
    print("  Option 1 (Recommended): python start_pokemon_game.py")
    print("  Option 2 (Manual):")
    print("    Terminal 1: python start_backend.py")  
    print("    Terminal 2: ./start_frontend.sh")
    print("  Option 3 (Individual):")
    print("    Backend: python backend/main.py")
    print("    Frontend: cd frontend && npm run dev")
    
    print(f"\n🤖 AI Status: {'✅ Full AI Available' if ai_working else '⚠️ Demo Mode'}")
    print("🌐 Game will be available at: http://localhost:5173")
    print("🎯 Backend API at: http://localhost:8000")
    
    return 0

if __name__ == "__main__":
    exit(main())