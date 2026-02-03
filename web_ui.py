# web_ui.py
from fastapi import FastAPI, HTTPException
import win32print
from config import load_config, save_config, AgentConfig
from printer_raw import open_drawer

app = FastAPI(title="GeniuStep CashDrawer Agent")

@app.get("/printers")
def list_printers():
    # يعرض الطابعات المثبتة
    printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
    return {"printers": printers}

@app.get("/config")
def get_config():
    return load_config().model_dump()

@app.post("/config")
def set_config(payload: dict):
    cfg = load_config()
    new_cfg = AgentConfig(**{**cfg.model_dump(), **payload})
    save_config(new_cfg)
    return {"ok": True, "config": new_cfg.model_dump()}

@app.post("/test/open_drawer")
def test_open_drawer():
    cfg = load_config()
    try:
        open_drawer(cfg.printer_name, cfg.drawer_pin, cfg.pulse_on, cfg.pulse_off)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
