"""
Pokemon TCG LLM Education Platform - Main FastAPI Server
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from pathlib import Path

# Add backend to Python path for imports
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

# Import Pokemon AI components
try:
    from src.ai_agents.opponent_ai import PokemonOpponentAI
    print("✅ Successfully imported Pokemon AI components")
except ImportError as e:
    print(f"⚠️  Warning: Could not import AI components: {e}")
    print("🔧 Running in demo mode")
    PokemonOpponentAI = None

# Initialize FastAPI app
app = FastAPI(
    title="Pokemon TCG LLM Education Platform",
    description="Teaching AI through Pokemon TCG gameplay",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if frontend dist directory exists
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
    print("✅ Serving frontend assets")

@app.get("/")
async def get_pokemon_game():
    """Serve Pokemon TCG game interface"""
    if frontend_dist.exists() and (frontend_dist / "index.html").exists():
        with open("frontend/dist/index.html") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pokemon TCG AI - Development</title>
            <style>body{font-family:Arial;margin:40px;background:#1a1a2e;color:white;text-align:center;}</style>
        </head>
        <body>
            <h1>🎮 Pokemon TCG AI Education</h1>
            <h2>Frontend not built yet</h2>
            <p>Run: <code>cd frontend && npm run dev</code></p>
            <p>Then visit: <a href="http://localhost:5173">http://localhost:5173</a></p>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ai_ready": PokemonOpponentAI is not None}

@app.websocket("/ws/pokemon-game/{session_id}")
async def pokemon_game_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print(f"�� Pokemon session {session_id} connected")
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Demo AI response
            await websocket.send_json({
                "type": "ai_move",
                "message": "AI is analyzing your Pokemon strategy!",
                "analysis": "Demo mode - AI backend components loading...",
                "type_lesson": "🎓 Type advantages are key in Pokemon battles!",
                "strategic_insight": "🎯 AI considers multiple factors when deciding!"
            })
                
    except WebSocketDisconnect:
        print(f"🔌 Session {session_id} disconnected")

if __name__ == "__main__":
    print("🎮 Starting Pokemon TCG AI Education Platform...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
