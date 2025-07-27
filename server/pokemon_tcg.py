# pokemon_tcg.py

# To run this, you only need FastAPI and uvicorn
# pip install -r server/requirements.txt

import sys
from pathlib import Path
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# --- Path Correction ---
# Add the script's own directory to the Python path to find the other modules.
sys.path.append(str(Path(__file__).parent.resolve()))

# --- Import Local Modules ---
# FIX: Changed from relative to absolute imports.
from judge import judge_router
# from opponent import opponent_router
# from advisor import advisor_router

# --- 1. Create the Main FastAPI Web Application ---
app = FastAPI()

# --- 2. Add CORS Middleware ---
origins = ["*"] # Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Mount the API Routers ---
# The final URL will be, for example: /mcp/judge/tools/validate_move
app.include_router(judge_router, prefix="/mcp/judge", tags=["Judge"])
# app.include_router(opponent_router, prefix="/mcp/opponent", tags=["Opponent"])
# app.include_router(advisor_router, prefix="/mcp/advisor", tags=["Advisor"])


# --- 4. Mount the Static Frontend Files ---
project_root = Path(__file__).parent.parent
client_dir = project_root / "client"
assets_dir = client_dir / "assets"

# Mount the 'assets' directory first.
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
# Mount the 'client' directory at the root to serve index.html.
app.mount("/", StaticFiles(directory=client_dir, html=True), name="client")


# To run this unified server, use uvicorn:
# uvicorn server.pokemon_tcg:app --host 0.0.0.0 --port 8000
