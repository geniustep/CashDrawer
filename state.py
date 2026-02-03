# state.py
import time
import threading
from collections import deque
from dataclasses import dataclass, field
from logger import get_logger

log = get_logger("state")


@dataclass
class HistoryEntry:
    timestamp: float
    action: str
    source: str  # "websocket" | "rest_api" | "test"
    status: str  # "ok" | "error"
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "time_str": time.strftime("%H:%M:%S", time.localtime(self.timestamp)),
            "date_str": time.strftime("%Y-%m-%d", time.localtime(self.timestamp)),
            "action": self.action,
            "source": self.source,
            "status": self.status,
            "detail": self.detail,
        }


class RateLimiter:
    """حد أقصى لعدد العمليات خلال فترة زمنية."""

    def __init__(self, max_calls: int = 10, period_seconds: float = 60.0):
        self.max_calls = max_calls
        self.period = period_seconds
        self._calls: deque[float] = deque()
        self._lock = threading.Lock()

    def allow(self) -> bool:
        now = time.time()
        with self._lock:
            while self._calls and now - self._calls[0] > self.period:
                self._calls.popleft()
            if len(self._calls) >= self.max_calls:
                return False
            self._calls.append(now)
            return True

    @property
    def remaining(self) -> int:
        now = time.time()
        with self._lock:
            while self._calls and now - self._calls[0] > self.period:
                self._calls.popleft()
            return max(0, self.max_calls - len(self._calls))


class AppState:
    """حالة التطبيق المشتركة بين كل المكونات."""

    def __init__(self):
        self._lock = threading.Lock()
        self.start_time: float = time.time()

        # WebSocket state
        self.ws_connected: bool = False
        self.ws_last_error: str = ""
        self.ws_reconnect_count: int = 0

        # Operation history
        self._history: deque[HistoryEntry] = deque(maxlen=200)

        # Rate limiter: 10 drawer opens per minute
        self.drawer_rate_limiter = RateLimiter(max_calls=10, period_seconds=60.0)

        # Counters
        self.total_opens: int = 0
        self.today_opens: int = 0
        self._today_date: str = time.strftime("%Y-%m-%d")

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self.start_time

    @property
    def uptime_str(self) -> str:
        s = int(self.uptime_seconds)
        days, s = divmod(s, 86400)
        hours, s = divmod(s, 3600)
        minutes, s = divmod(s, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        parts.append(f"{s}s")
        return " ".join(parts)

    def add_history(self, action: str, source: str, status: str, detail: str = ""):
        entry = HistoryEntry(
            timestamp=time.time(),
            action=action,
            source=source,
            status=status,
            detail=detail,
        )
        with self._lock:
            self._history.appendleft(entry)
            if status == "ok" and action == "OPEN_DRAWER":
                self.total_opens += 1
                today = time.strftime("%Y-%m-%d")
                if today != self._today_date:
                    self._today_date = today
                    self.today_opens = 0
                self.today_opens += 1
        log.info("History: %s | %s | %s | %s", action, source, status, detail)

    def get_history(self, limit: int = 50) -> list[dict]:
        with self._lock:
            items = list(self._history)[:limit]
        return [e.to_dict() for e in items]

    def set_ws_connected(self, connected: bool, error: str = ""):
        with self._lock:
            if not connected and self.ws_connected:
                self.ws_reconnect_count += 1
            self.ws_connected = connected
            self.ws_last_error = error

    def health_dict(self) -> dict:
        with self._lock:
            last_entry = self._history[0].to_dict() if self._history else None
        return {
            "status": "healthy",
            "ws_connected": self.ws_connected,
            "ws_last_error": self.ws_last_error,
            "ws_reconnect_count": self.ws_reconnect_count,
            "uptime": self.uptime_str,
            "uptime_seconds": round(self.uptime_seconds),
            "total_opens": self.total_opens,
            "today_opens": self.today_opens,
            "last_operation": last_entry,
        }


# ── Singleton ──
app_state = AppState()
