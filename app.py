# app.py
import asyncio
import threading
import sys
import uvicorn
from ws_client import start_ws_in_background
from web_ui import app

def run_api():
    try:
        print("=" * 50)
        print("GeniusStep CashDrawer Agent")
        print("=" * 50)
        print("Starting API server at http://127.0.0.1:16732")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        uvicorn.run(app, host="127.0.0.1", port=16732, log_level="info")
    except Exception as e:
        print(f"API server error: {e}")
        sys.exit(1)

def run_ws():
    try:
        print("Starting WebSocket client...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_ws_in_background(loop)
        loop.run_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        loop.stop()
    except Exception as e:
        print(f"WebSocket client error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        print("Initializing server...")
        t1 = threading.Thread(target=run_api, daemon=True)
        t1.start()
        print("API server started!")
        run_ws()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
