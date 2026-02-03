# config.py
from pydantic import BaseModel
from pathlib import Path
import json

APP_DIR = Path(r"C:\ProgramData\GeniusStep\CashDrawerAgent")
CFG_PATH = APP_DIR / "config.json"
APP_DIR.mkdir(parents=True, exist_ok=True)

class AgentConfig(BaseModel):
    device_id: str = "POS-001"
    device_token: str = "CHANGE_ME"
    wss_url: str = "wss://app.propanel.ma/hardware/ws"
    printer_name: str = ""          # اسم الطابعة كما يظهر في Windows
    drawer_pin: int = 0             # 0 أو 1 حسب الطابعة
    pulse_on: int = 60              # t1
    pulse_off: int = 120            # t2

def load_config() -> AgentConfig:
    if CFG_PATH.exists():
        data = json.loads(CFG_PATH.read_text(encoding="utf-8"))
        return AgentConfig(**data)
    cfg = AgentConfig()
    save_config(cfg)
    return cfg

def save_config(cfg: AgentConfig) -> None:
    CFG_PATH.write_text(cfg.model_dump_json(indent=2), encoding="utf-8")