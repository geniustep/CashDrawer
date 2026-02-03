# ws_client.py
import asyncio
import json
import websockets
from config import load_config
from printer_raw import open_drawer

async def run_ws():
    print("WebSocket client: initializing...")
    while True:
        cfg = load_config()
        headers = {
            "X-Device-Id": cfg.device_id,
            "X-Device-Token": cfg.device_token,
        }

        try:
            print(f"WebSocket client: connecting to {cfg.wss_url}...")
            async with websockets.connect(cfg.wss_url, extra_headers=headers, ping_interval=20, ping_timeout=20) as ws:
                print("WebSocket client: connected!")
                # hello
                await ws.send(json.dumps({"type": "HELLO", "device_id": cfg.device_id}))
                print(f"WebSocket client: sent HELLO (device_id: {cfg.device_id})")
                async for msg in ws:
                    try:
                        data = json.loads(msg)
                    except Exception:
                        continue

                    if data.get("cmd") == "OPEN_DRAWER":
                        print("WebSocket client: received OPEN_DRAWER")
                        try:
                            open_drawer(cfg.printer_name, cfg.drawer_pin, cfg.pulse_on, cfg.pulse_off)
                            await ws.send(json.dumps({"type": "ACK", "cmd": "OPEN_DRAWER", "status": "OK"}))
                            print("WebSocket client: drawer opened OK")
                        except Exception as e:
                            print(f"WebSocket client: drawer error: {e}")
                            await ws.send(json.dumps({"type": "ACK", "cmd": "OPEN_DRAWER", "status": "ERR", "error": str(e)}))
        except Exception as e:
            print(f"WebSocket client: connection error: {e}")
            print("WebSocket client: retrying in 3 seconds...")
            # انتظار بسيط ثم إعادة الاتصال
            await asyncio.sleep(3)

def start_ws_in_background(loop: asyncio.AbstractEventLoop):
    loop.create_task(run_ws())
