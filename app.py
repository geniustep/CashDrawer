# app.py
import asyncio
import threading
import signal
import sys
import webbrowser
import uvicorn
from logger import setup_logging, get_logger
from config import APP_VERSION, load_config

# Initialize logging first
setup_logging()
log = get_logger("app")

# Import after logging setup
from ws_client import start_ws_in_background
from web_ui import app

HOST = "127.0.0.1"
PORT = 16732
URL = f"http://{HOST}:{PORT}"

_shutdown_event = threading.Event()


def run_api():
    """تشغيل خادم FastAPI/Uvicorn."""
    try:
        log.info("Starting API server at %s", URL)
        config = uvicorn.Config(
            app, host=HOST, port=PORT,
            log_level="warning",
            access_log=False,
        )
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        log.error("API server error: %s", e)
        _shutdown_event.set()


def run_ws():
    """تشغيل عميل WebSocket في event loop مستقل."""
    try:
        log.info("Starting WebSocket client...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_ws_in_background(loop)
        loop.run_forever()
    except Exception as e:
        log.error("WebSocket client error: %s", e)
        _shutdown_event.set()


def open_browser():
    """فتح المتصفح تلقائياً عند أول تشغيل."""
    import time
    time.sleep(2)  # Wait for server to start
    try:
        webbrowser.open(URL)
        log.info("Browser opened at %s", URL)
    except Exception:
        log.info("Could not open browser. Navigate to %s manually.", URL)


def signal_handler(sig, frame):
    """معالجة إشارة الإيقاف."""
    log.info("Shutdown signal received")
    _shutdown_event.set()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        log.info("=" * 50)
        log.info("GeniusStep CashDrawer Agent v%s", APP_VERSION)
        log.info("=" * 50)

        # Load config early to validate
        cfg = load_config()
        log.info("Device: %s | Printer: %s", cfg.device_id, cfg.printer_name or "(not set)")

        # Start API server thread
        t_api = threading.Thread(target=run_api, name="api-server", daemon=True)
        t_api.start()
        log.info("API server thread started")

        # Start WebSocket client thread
        t_ws = threading.Thread(target=run_ws, name="ws-client", daemon=True)
        t_ws.start()
        log.info("WebSocket client thread started")

        # Open browser
        t_browser = threading.Thread(target=open_browser, name="browser", daemon=True)
        t_browser.start()

        log.info("All services started. Dashboard: %s", URL)
        log.info("Press Ctrl+C to stop")

        # Wait for shutdown
        _shutdown_event.wait()
        log.info("Shutting down gracefully...")

    except KeyboardInterrupt:
        log.info("Keyboard interrupt received")
    except Exception as e:
        log.error("Fatal error: %s", e, exc_info=True)
        input("\nPress Enter to exit...")
    finally:
        log.info("GeniusStep CashDrawer Agent stopped.")
        sys.exit(0)
