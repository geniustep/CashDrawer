# config.py
import json
import threading
from pathlib import Path
from pydantic import BaseModel, field_validator
from logger import get_logger

log = get_logger("config")

APP_VERSION = "2.0.0"
APP_DIR = Path(r"C:\ProgramData\GeniusStep\CashDrawerAgent")
CFG_PATH = APP_DIR / "config.json"

try:
    APP_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    log.warning("Could not create config directory: %s", APP_DIR)


class AgentConfig(BaseModel):
    device_id: str = "POS-001"
    device_token: str = "CHANGE_ME"
    wss_url: str = "wss://app.propanel.ma/hardware/ws"
    printer_name: str = ""
    drawer_pin: int = 0
    pulse_on: int = 60
    pulse_off: int = 120

    @field_validator("drawer_pin")
    @classmethod
    def pin_must_be_valid(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("drawer_pin must be 0 or 1")
        return v

    @field_validator("pulse_on", "pulse_off")
    @classmethod
    def pulse_must_be_positive(cls, v: int) -> int:
        if v < 1 or v > 255:
            raise ValueError("pulse values must be between 1 and 255")
        return v


class ConfigUpdatePayload(BaseModel):
    """نموذج التحقق من بيانات تحديث الإعدادات."""
    device_id: str | None = None
    device_token: str | None = None
    wss_url: str | None = None
    printer_name: str | None = None
    drawer_pin: int | None = None
    pulse_on: int | None = None
    pulse_off: int | None = None

    @field_validator("drawer_pin")
    @classmethod
    def pin_must_be_valid(cls, v):
        if v is not None and v not in (0, 1):
            raise ValueError("drawer_pin must be 0 or 1")
        return v

    @field_validator("pulse_on", "pulse_off")
    @classmethod
    def pulse_must_be_positive(cls, v):
        if v is not None and (v < 1 or v > 255):
            raise ValueError("pulse values must be between 1 and 255")
        return v


# ── Config cache with thread safety ──
_config_cache: AgentConfig | None = None
_config_lock = threading.Lock()


def load_config(force_reload: bool = False) -> AgentConfig:
    """تحميل الإعدادات مع تخزين مؤقت (thread-safe)."""
    global _config_cache
    with _config_lock:
        if _config_cache is not None and not force_reload:
            return _config_cache
        try:
            if CFG_PATH.exists():
                data = json.loads(CFG_PATH.read_text(encoding="utf-8"))
                _config_cache = AgentConfig(**data)
                log.info("Config loaded from %s", CFG_PATH)
            else:
                _config_cache = AgentConfig()
                save_config(_config_cache)
                log.info("Default config created at %s", CFG_PATH)
        except Exception as e:
            log.error("Failed to load config: %s", e)
            _config_cache = AgentConfig()
        return _config_cache


def save_config(cfg: AgentConfig) -> None:
    """حفظ الإعدادات وتحديث الذاكرة المؤقتة."""
    global _config_cache
    with _config_lock:
        try:
            CFG_PATH.write_text(cfg.model_dump_json(indent=2), encoding="utf-8")
            _config_cache = cfg
            log.info("Config saved to %s", CFG_PATH)
        except Exception as e:
            log.error("Failed to save config: %s", e)
            raise


def invalidate_cache() -> None:
    """مسح الذاكرة المؤقتة لإجبار إعادة التحميل."""
    global _config_cache
    with _config_lock:
        _config_cache = None
