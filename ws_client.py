# ws_client.py
import asyncio
import json
import time
import websockets
from config import load_config
from printer_raw import open_drawer, print_receipt, print_raw_receipt
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
            # استخدم additional_headers (مطلوب في websockets 11+)
            async with websockets.connect(
                cfg.wss_url,
                additional_headers=headers,
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

                    elif cmd == "PRINT_RECEIPT":
                        await _handle_print_receipt(ws, data, cfg)

                    elif cmd == "PRINT_RAW":
                        await _handle_print_raw(ws, data, cfg)

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


async def _handle_print_receipt(ws, data, cfg):
    """معالجة أمر طباعة الإيصال."""
    # Rate limiting check
    if not app_state.receipt_rate_limiter.allow():
        log.warning("Rate limit exceeded for PRINT_RECEIPT")
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "PRINT_RECEIPT",
            "status": "ERR", "error": "Rate limit exceeded",
        }))
        app_state.add_history(
            action="PRINT_RECEIPT", source="websocket",
            status="error", detail="Rate limit exceeded",
        )
        return

    try:
        receipt_data = data.get("receipt_data", {})
        paper_width = data.get("paper_width", 48)
        encoding = data.get("encoding", "cp437")
        cut_after = data.get("cut_after", True)
        open_drawer_flag = data.get("open_drawer", False)
        
        print_receipt(
            printer_name=cfg.printer_name,
            receipt_data=receipt_data,
            paper_width=paper_width,
            encoding=encoding,
            cut_after=cut_after,
            open_drawer=open_drawer_flag,
            drawer_pin=cfg.drawer_pin,
        )
        
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "PRINT_RECEIPT", "status": "OK",
        }))
        log.info("Receipt printed OK via WebSocket")
        app_state.add_history(
            action="PRINT_RECEIPT", source="websocket", status="ok",
            detail=f"Order: {receipt_data.get('name', 'N/A')}",
        )
    except Exception as e:
        log.error("Receipt print error: %s", e)
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "PRINT_RECEIPT",
            "status": "ERR", "error": str(e),
        }))
        app_state.add_history(
            action="PRINT_RECEIPT", source="websocket",
            status="error", detail=str(e),
        )


async def _handle_print_raw(ws, data, cfg):
    """معالجة أمر طباعة بيانات خام."""
    # Rate limiting check
    if not app_state.receipt_rate_limiter.allow():
        log.warning("Rate limit exceeded for PRINT_RAW")
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "PRINT_RAW",
            "status": "ERR", "error": "Rate limit exceeded",
        }))
        app_state.add_history(
            action="PRINT_RAW", source="websocket",
            status="error", detail="Rate limit exceeded",
        )
        return

    try:
        raw_data = data.get("data", "")
        encoding = data.get("encoding", "utf-8")
        cut_after = data.get("cut_after", True)
        
        print_raw_receipt(
            printer_name=cfg.printer_name,
            raw_data=raw_data,
            encoding=encoding,
            cut_after=cut_after,
        )
        
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "PRINT_RAW", "status": "OK",
        }))
        log.info("Raw data printed OK via WebSocket")
        app_state.add_history(
            action="PRINT_RAW", source="websocket", status="ok",
        )
    except Exception as e:
        log.error("Raw print error: %s", e)
        await ws.send(json.dumps({
            "type": "ACK", "cmd": "PRINT_RAW",
            "status": "ERR", "error": str(e),
        }))
        app_state.add_history(
            action="PRINT_RAW", source="websocket",
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
