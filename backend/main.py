"""
Pokemon TCG LLM Education Platform - Main FastAPI Server
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI(
    title="Pokemon TCG LLM Education Platform",
    description="Teaching AI through Pokemon TCG gameplay",
    version="1.0.0"
)

# Serve Pokemon game frontend
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

@app.get("/")
async def get_pokemon_game():
    """Serve Pokemon TCG game interface"""
    with open("frontend/dist/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check for Pokemon game server"""
    return {
        "status": "healthy",
        "service": "pokemon-tcg-llm-education",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.websocket("/ws/pokemon-game/{session_id}")
async def pokemon_game_websocket(websocket: WebSocket, session_id: str):
    """WebSocket for real-time Pokemon game communication"""
    await websocket.accept()
    
    try:
        while True:
            # Receive Pokemon move from child
            data = await websocket.receive_text()
            
            # TODO: Process Pokemon move through AI agents
            # TODO: Generate AI response and explanations
            # TODO: Send back to frontend
            
            # Placeholder response
            response = {
                "type": "ai_move",
                "message": "AI is thinking about Pokemon strategy...",
                "session_id": session_id
            }
            
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        print(f"Pokemon game session {session_id} disconnected")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
