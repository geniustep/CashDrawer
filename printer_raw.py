# printer_raw.py
import win32print


def send_raw(printer_name: str, data: bytes, job_name: str = "GeniusStep CashDrawer"):
    if not printer_name:
        raise RuntimeError("Printer name is empty. اختر طابعة أولًا.")
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


def escpos_open_drawer(pin: int = 0, t1: int = 60, t2: int = 120) -> bytes:
    # ESC p m t1 t2
    return bytes([0x1B, 0x70, pin & 0xFF, t1 & 0xFF, t2 & 0xFF])


def open_drawer(printer_name: str, pin: int = 0, t1: int = 60, t2: int = 120):
    data = escpos_open_drawer(pin, t1, t2)
    send_raw(printer_name, data, job_name="Open Cash Drawer")
