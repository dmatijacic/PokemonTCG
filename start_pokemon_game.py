#!/usr/bin/env python3
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
        print("\n🛑 Shutting down Pokemon game...")
