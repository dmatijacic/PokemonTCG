# server/pokemon_tcg.py

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# --- Lokalni Moduli (ISPRAVAK OVDJE) ---
sys.path.append(str(Path(__file__).parent.resolve()))
# Uklonili smo 'get_agent_executor' jer više ne postoji
from judge import judge_router, initialize_agent

# --- Lifespan za glavnu aplikaciju ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Inicijalizira AI agenta pri pokretanju servera.
    """
    await initialize_agent()
    yield
    print("Shutting down application.")

# --- Glavna FastAPI Aplikacija ---
app = FastAPI(lifespan=lifespan)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
import json

# --- ISPRAVLJENI Logging Middleware ---
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Prvo pročitaj tijelo zahtjeva
        body_bytes = await request.body()
        
        # Logiraj informaciju. Dekodiramo bytes u string za čitljiv ispis.
        try:
            body_json = json.loads(body_bytes.decode('utf-8')) if body_bytes else {}
            print(f"Incoming request: {request.method} {request.url} Body: {body_json}")
        except json.JSONDecodeError:
            print(f"Incoming request: {request.method} {request.url} Body (non-JSON): {body_bytes.decode('utf-8')}")

        # Kreiraj novu "receive" funkciju koja vraća spremljeno tijelo
        async def receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        # Kreiraj novi "scope" s našom novom "receive" funkcijom
        new_scope = request.scope.copy()
        new_scope['receive'] = receive
        
        # Kreiraj novi Request objekt s novim scope-om
        new_request = Request(new_scope)

        # Proslijedi novi zahtjev dalje u aplikaciju
        response = await call_next(new_request)
        
        return response
    
app.add_middleware(LoggingMiddleware)

# --- API Routeri ---
app.include_router(judge_router, prefix="/mcp/judge", tags=["Judge"])

# --- Statičke datoteke (Frontend) ---
project_root = Path(__file__).parent.parent
client_dir = project_root / "client"
assets_dir = project_root / "assets"

app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
app.mount("/", StaticFiles(directory=client_dir, html=True), name="client")
