# ws_client.py
import asyncio
import json
import time
import websockets
from config import load_config
from printer_raw import open_drawer
from state import app_state
from logger import get_logger

log = get_logger("ws_client")

# Exponential backoff settings
MIN_RETRY_DELAY = 3
MAX_RETRY_DELAY = 30


async def run_ws():
    """عميل WebSocket مع إعادة اتصال ذكية (exponential backoff)."""
    log.info("WebSocket client initializing...")
    retry_delay = MIN_RETRY_DELAY

    while True:
        cfg = load_config(force_reload=True)
        headers = {
            "X-Device-Id": cfg.device_id,
            "X-Device-Token": cfg.device_token,
        }

        try:
            log.info("Connecting to %s ...", cfg.wss_url)
            async with websockets.connect(
                cfg.wss_url,
                extra_headers=headers,
                ping_interval=20,
                ping_timeout=20,
            ) as ws:
                # Connection successful - reset backoff
                retry_delay = MIN_RETRY_DELAY
                app_state.set_ws_connected(True)
                log.info("WebSocket connected!")

                # Send HELLO
                hello = {"type": "HELLO", "device_id": cfg.device_id}
                await ws.send(json.dumps(hello))
                log.info("Sent HELLO (device_id: %s)", cfg.device_id)

                app_state.add_history(
                    action="WS_CONNECT",
                    source="websocket",
                    status="ok",
                    detail=f"Connected to {cfg.wss_url}",
                )

                async for msg in ws:
                    try:
                        data = json.loads(msg)
                    except (json.JSONDecodeError, ValueError):
                        log.warning("Received invalid JSON: %s", msg[:100])
                        continue

                    cmd = data.get("cmd", "")
                    log.info("Received command: %s", cmd)

                    if cmd == "OPEN_DRAWER":
                        await _handle_open_drawer(ws, cfg)

                    elif cmd == "PING":
                        await ws.send(json.dumps({
                            "type": "PONG",
                            "device_id": cfg.device_id,
                            "timestamp": time.time(),
                        }))
                        log.debug("Responded to PING")

                    elif cmd == "GET_STATUS":
                        status = app_state.health_dict()
                        status["type"] = "STATUS_RESPONSE"
                        status["device_id"] = cfg.device_id
                        await ws.send(json.dumps(status))
                        log.info("Sent status response")

                    elif cmd == "UPDATE_CONFIG":
                        await _handle_remote_config(ws, data, cfg)

                    else:
                        log.warning("Unknown command: %s", cmd)

        except websockets.exceptions.ConnectionClosed as e:
            log.warning("WebSocket connection closed: %s", e)
            app_state.set_ws_connected(False, error=str(e))
            app_state.add_history(
                action="WS_DISCONNECT",
                source="websocket",
                status="error",
                detail=str(e),
            )
        except Exception as e:
            log.error("WebSocket error: %s", e)
            app_state.set_ws_connected(False, error=str(e))
            app_state.add_history(
                action="WS_ERROR",
                source="websocket",
                status="error",
                detail=str(e),
            )

        # Exponential backoff
        log.info("Retrying in %d seconds...", retry_delay)
        await asyncio.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)


async def _handle_open_drawer(ws, cfg):
    """معالجة أمر فتح الدرج."""
    # Rate limiting check
    if not app_state.drawer_rate_limiter.allow():
        log.warning("Rate limit exceeded for OPEN_DRAWER")
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "OPEN_DRAWER",
            "status": "ERR", "error": "Rate limit exceeded",
        }))
        app_state.add_history(
            action="OPEN_DRAWER", source="websocket",
            status="error", detail="Rate limit exceeded",
        )
        return

    try:
        open_drawer(cfg.printer_name, cfg.drawer_pin, cfg.pulse_on, cfg.pulse_off)
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "OPEN_DRAWER", "status": "OK",
        }))
        log.info("Drawer opened OK via WebSocket")
        app_state.add_history(
            action="OPEN_DRAWER", source="websocket", status="ok",
        )
    except Exception as e:
        log.error("Drawer error: %s", e)
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "OPEN_DRAWER",
            "status": "ERR", "error": str(e),
        }))
        app_state.add_history(
            action="OPEN_DRAWER", source="websocket",
            status="error", detail=str(e),
        )


async def _handle_remote_config(ws, data, cfg):
    """معالجة أمر تحديث الإعدادات عن بُعد."""
    from config import save_config, AgentConfig
    try:
        new_data = {**cfg.model_dump(), **data.get("config", {})}
        new_cfg = AgentConfig(**new_data)
        save_config(new_cfg)
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "UPDATE_CONFIG", "status": "OK",
        }))
        log.info("Config updated remotely")
        app_state.add_history(
            action="UPDATE_CONFIG", source="websocket", status="ok",
        )
    except Exception as e:
        log.error("Remote config update error: %s", e)
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "UPDATE_CONFIG",
            "status": "ERR", "error": str(e),
        }))


def start_ws_in_background(loop: asyncio.AbstractEventLoop):
    """تشغيل عميل WebSocket في الخلفية."""
    loop.create_task(run_ws())
