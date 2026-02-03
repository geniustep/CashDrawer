# printer_raw.py
import win32print
from logger import get_logger

log = get_logger("printer")


def send_raw(printer_name: str, data: bytes, job_name: str = "GeniusStep CashDrawer"):
    """إرسال بيانات RAW مباشرة إلى الطابعة."""
    if not printer_name:
        raise RuntimeError("Printer name is empty. اختر طابعة أولاً.")
    log.debug("Sending %d bytes to printer '%s'", len(data), printer_name)
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        win32print.StartDocPrinter(hPrinter, 1, (job_name, None, "RAW"))
        try:
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, data)
            win32print.EndPagePrinter(hPrinter)
        finally:
            win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)
    log.info("Data sent to printer '%s' OK", printer_name)


def escpos_open_drawer(pin: int = 0, t1: int = 60, t2: int = 120) -> bytes:
    """توليد أمر ESC/POS لفتح درج النقدية."""
    # ESC p m t1 t2
    return bytes([0x1B, 0x70, pin & 0xFF, t1 & 0xFF, t2 & 0xFF])


def open_drawer(printer_name: str, pin: int = 0, t1: int = 60, t2: int = 120):
    """فتح درج النقدية عبر الطابعة."""
    log.info("Opening drawer: printer='%s', pin=%d, t1=%d, t2=%d", printer_name, pin, t1, t2)
    data = escpos_open_drawer(pin, t1, t2)
    send_raw(printer_name, data, job_name="Open Cash Drawer")
    log.info("Drawer opened successfully")
