# logger.py
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

APP_NAME = "GeniusStepCashDrawer"
LOG_DIR = Path(r"C:\ProgramData\GeniusStep\CashDrawerAgent\logs")

def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """تهيئة نظام التسجيل المركزي مع ملفات دوارة + console."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    logger = logging.getLogger(APP_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s.%(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # File handler (rotating: 5 MB x 3 files)
    try:
        log_file = LOG_DIR / "agent.log"
        fh = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except OSError:
        logger.warning("Could not create log file, using console only")

    return logger


def get_logger(module: str = "") -> logging.Logger:
    """إرجاع logger فرعي لوحدة معينة."""
    name = f"{APP_NAME}.{module}" if module else APP_NAME
    return logging.getLogger(name)
