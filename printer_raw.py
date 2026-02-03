# printer_raw.py
import win32print
import base64
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


# ══════════════════════════════════════════════════════════════════════════════
#  ESC/POS Receipt Printing Functions
# ══════════════════════════════════════════════════════════════════════════════

# ESC/POS Commands
ESC = 0x1B
GS = 0x1D
LF = 0x0A  # Line Feed

# Text alignment
ALIGN_LEFT = bytes([ESC, 0x61, 0x00])
ALIGN_CENTER = bytes([ESC, 0x61, 0x01])
ALIGN_RIGHT = bytes([ESC, 0x61, 0x02])

# Text formatting
BOLD_ON = bytes([ESC, 0x45, 0x01])
BOLD_OFF = bytes([ESC, 0x45, 0x00])
DOUBLE_HEIGHT_ON = bytes([ESC, 0x21, 0x10])
DOUBLE_WIDTH_ON = bytes([ESC, 0x21, 0x20])
DOUBLE_SIZE_ON = bytes([ESC, 0x21, 0x30])
NORMAL_SIZE = bytes([ESC, 0x21, 0x00])
UNDERLINE_ON = bytes([ESC, 0x2D, 0x01])
UNDERLINE_OFF = bytes([ESC, 0x2D, 0x00])

# Printer control
INIT_PRINTER = bytes([ESC, 0x40])
CUT_PAPER = bytes([GS, 0x56, 0x00])  # Full cut
CUT_PAPER_PARTIAL = bytes([GS, 0x56, 0x01])  # Partial cut
FEED_LINES = lambda n: bytes([ESC, 0x64, n])  # Feed n lines


def escpos_init() -> bytes:
    """تهيئة الطابعة - إعادة الضبط."""
    return INIT_PRINTER


def escpos_cut(partial: bool = True) -> bytes:
    """قص الورقة."""
    return CUT_PAPER_PARTIAL if partial else CUT_PAPER


def escpos_feed(lines: int = 3) -> bytes:
    """تغذية الورق بعدد معين من السطور."""
    return FEED_LINES(lines)


def escpos_text(text: str, encoding: str = "cp437") -> bytes:
    """
    تحويل النص إلى bytes للطباعة.
    يدعم Code Page 437 (افتراضي) أو cp1256 للعربية.
    """
    try:
        return text.encode(encoding, errors="replace")
    except (UnicodeEncodeError, LookupError):
        return text.encode("utf-8", errors="replace")


def escpos_line(char: str = "-", width: int = 48) -> bytes:
    """طباعة خط فاصل."""
    return escpos_text(char * width + "\n")


def escpos_set_encoding(codepage: int = 0) -> bytes:
    """
    تعيين Code Page للطابعة.
    0 = CP437 (USA, Standard Europe)
    16 = WPC1252 (Latin I)
    17 = PC866 (Cyrillic #2)
    22 = Arabic (PC864)
    """
    return bytes([ESC, 0x74, codepage])


def build_receipt_commands(
    receipt_data: dict,
    paper_width: int = 48,
    encoding: str = "cp437",
    include_logo: bool = False,
    cut_after: bool = True,
    open_drawer_after: bool = False,
    drawer_pin: int = 0,
) -> bytes:
    """
    بناء أوامر ESC/POS لطباعة إيصال POS كامل.
    
    Args:
        receipt_data: بيانات الإيصال من Odoo POS (export_for_printing)
        paper_width: عرض الورقة بالأحرف (32, 42, 48)
        encoding: ترميز النص
        include_logo: هل يتم طباعة الشعار (غير مدعوم حالياً)
        cut_after: قص الورقة بعد الطباعة
        open_drawer_after: فتح الدرج بعد الطباعة
        drawer_pin: منفذ الدرج (0 أو 1)
    
    Returns:
        bytes: أوامر ESC/POS للطباعة
    """
    commands = bytearray()
    
    # Initialize printer
    commands.extend(INIT_PRINTER)
    
    # Set encoding if needed
    if encoding == "cp1256":
        commands.extend(escpos_set_encoding(22))  # Arabic
    
    def add_text(text: str, align: bytes = ALIGN_LEFT, bold: bool = False, 
                 double: bool = False, newline: bool = True):
        """Helper to add formatted text."""
        commands.extend(align)
        if bold:
            commands.extend(BOLD_ON)
        if double:
            commands.extend(DOUBLE_SIZE_ON)
        commands.extend(escpos_text(text, encoding))
        if newline:
            commands.append(LF)
        if double:
            commands.extend(NORMAL_SIZE)
        if bold:
            commands.extend(BOLD_OFF)
    
    def add_line(char: str = "-"):
        commands.extend(escpos_line(char, paper_width))
    
    def format_currency(amount, symbol="", position="after"):
        """تنسيق المبلغ."""
        if position == "before":
            return f"{symbol}{amount:.2f}"
        return f"{amount:.2f} {symbol}"
    
    # ═══════════════════════════════════════════════════════════════════════
    # Header - معلومات المتجر
    # ═══════════════════════════════════════════════════════════════════════
    
    company = receipt_data.get("company", {})
    header = receipt_data.get("headerData", {})
    
    # اسم الشركة
    company_name = company.get("name") or header.get("company", {}).get("name", "")
    if company_name:
        add_text(company_name, ALIGN_CENTER, bold=True, double=True)
    
    # عنوان نقطة البيع
    pos_name = header.get("header", "") or receipt_data.get("pos", {}).get("name", "")
    if pos_name:
        add_text(pos_name, ALIGN_CENTER, bold=True)
    
    # عنوان الشركة
    address_parts = []
    if company.get("street"):
        address_parts.append(company["street"])
    if company.get("city"):
        city_line = company["city"]
        if company.get("zip"):
            city_line = f"{company['zip']} {city_line}"
        address_parts.append(city_line)
    if company.get("country", {}).get("name"):
        address_parts.append(company["country"]["name"])
    
    for addr_line in address_parts:
        add_text(addr_line, ALIGN_CENTER)
    
    # معلومات الاتصال
    if company.get("phone"):
        add_text(f"Tel: {company['phone']}", ALIGN_CENTER)
    if company.get("vat"):
        add_text(f"VAT: {company['vat']}", ALIGN_CENTER)
    
    add_line("=")
    
    # ═══════════════════════════════════════════════════════════════════════
    # Order Info - معلومات الطلب
    # ═══════════════════════════════════════════════════════════════════════
    
    order_name = receipt_data.get("name", "")
    if order_name:
        add_text(f"Order: {order_name}", ALIGN_CENTER, bold=True)
    
    # التاريخ والوقت
    date_str = receipt_data.get("date", {})
    if isinstance(date_str, dict):
        date_str = date_str.get("localestring", "")
    if date_str:
        add_text(f"Date: {date_str}", ALIGN_CENTER)
    
    # الموظف
    employee = receipt_data.get("employee", "")
    if employee:
        add_text(f"Cashier: {employee}", ALIGN_CENTER)
    
    # العميل
    client = receipt_data.get("client")
    if client:
        client_name = client.get("name", "") if isinstance(client, dict) else str(client)
        if client_name:
            add_text(f"Customer: {client_name}", ALIGN_CENTER)
    
    add_line("-")
    
    # ═══════════════════════════════════════════════════════════════════════
    # Order Lines - خطوط الطلب
    # ═══════════════════════════════════════════════════════════════════════
    
    orderlines = receipt_data.get("orderlines", [])
    currency = receipt_data.get("currency", {})
    currency_symbol = currency.get("symbol", "")
    currency_position = currency.get("position", "after")
    
    for line in orderlines:
        product_name = line.get("product_name", line.get("productName", "Unknown"))
        quantity = line.get("quantity", line.get("qty", 1))
        unit_price = line.get("price", line.get("unit_price", 0))
        price_display = line.get("price_display", "")
        discount = line.get("discount", 0)
        
        # Product name (may wrap)
        if len(product_name) > paper_width - 12:
            add_text(product_name[:paper_width - 3] + "...", ALIGN_LEFT)
        else:
            add_text(product_name, ALIGN_LEFT)
        
        # Quantity x Price = Total (right aligned)
        if price_display:
            line_total = price_display
        else:
            total = line.get("price_display_one", quantity * unit_price)
            if isinstance(total, (int, float)):
                line_total = format_currency(total, currency_symbol, currency_position)
            else:
                line_total = str(total)
        
        qty_price = f"  {quantity} x {format_currency(unit_price, currency_symbol, currency_position)}"
        spacing = paper_width - len(qty_price) - len(line_total)
        if spacing < 1:
            spacing = 1
        detail_line = qty_price + " " * spacing + line_total
        add_text(detail_line, ALIGN_LEFT)
        
        # Discount if any
        if discount and discount > 0:
            add_text(f"  Discount: {discount}%", ALIGN_LEFT)
    
    add_line("-")
    
    # ═══════════════════════════════════════════════════════════════════════
    # Totals - المجاميع
    # ═══════════════════════════════════════════════════════════════════════
    
    def add_total_line(label: str, amount, bold: bool = False, double: bool = False):
        """Add a total line with label and amount."""
        if isinstance(amount, (int, float)):
            amount_str = format_currency(amount, currency_symbol, currency_position)
        else:
            amount_str = str(amount)
        spacing = paper_width - len(label) - len(amount_str)
        if spacing < 1:
            spacing = 1
        total_line = label + " " * spacing + amount_str
        add_text(total_line, ALIGN_LEFT, bold=bold, double=double)
    
    # Subtotal
    subtotal = receipt_data.get("subtotal", receipt_data.get("total_without_tax", 0))
    if subtotal:
        add_total_line("Subtotal:", subtotal)
    
    # Taxes
    tax_details = receipt_data.get("tax_details", [])
    for tax in tax_details:
        tax_name = tax.get("name", "Tax")
        tax_amount = tax.get("amount", 0)
        add_total_line(f"  {tax_name}:", tax_amount)
    
    total_tax = receipt_data.get("total_tax", 0)
    if total_tax and not tax_details:
        add_total_line("Tax:", total_tax)
    
    # Discount total
    total_discount = receipt_data.get("total_discount", 0)
    if total_discount and total_discount > 0:
        add_total_line("Discount:", -total_discount)
    
    add_line("=")
    
    # Grand Total
    total = receipt_data.get("total_with_tax", receipt_data.get("amount_total", 0))
    add_total_line("TOTAL:", total, bold=True, double=True)
    
    add_line("=")
    
    # ═══════════════════════════════════════════════════════════════════════
    # Payments - المدفوعات
    # ═══════════════════════════════════════════════════════════════════════
    
    paymentlines = receipt_data.get("paymentlines", [])
    if paymentlines:
        add_text("PAYMENT:", ALIGN_LEFT, bold=True)
        for payment in paymentlines:
            pm_name = payment.get("name", payment.get("journal", "Payment"))
            pm_amount = payment.get("amount", 0)
            add_total_line(f"  {pm_name}:", pm_amount)
    
    # Change
    change = receipt_data.get("change", 0)
    if change and change > 0:
        add_total_line("CHANGE:", change, bold=True)
    
    add_line("-")
    
    # ═══════════════════════════════════════════════════════════════════════
    # Footer - تذييل
    # ═══════════════════════════════════════════════════════════════════════
    
    footer = header.get("footer", "") or receipt_data.get("footer", "")
    if footer:
        commands.append(LF)
        add_text(footer, ALIGN_CENTER)
    
    # Thank you message
    commands.append(LF)
    add_text("Thank you for your purchase!", ALIGN_CENTER)
    add_text("شكراً لتسوقكم معنا", ALIGN_CENTER)
    
    # ═══════════════════════════════════════════════════════════════════════
    # Final operations
    # ═══════════════════════════════════════════════════════════════════════
    
    # Feed paper
    commands.extend(escpos_feed(4))
    
    # Cut paper
    if cut_after:
        commands.extend(escpos_cut(partial=True))
    
    # Open drawer
    if open_drawer_after:
        commands.extend(escpos_open_drawer(drawer_pin))
    
    return bytes(commands)


def print_receipt(
    printer_name: str,
    receipt_data: dict,
    paper_width: int = 48,
    encoding: str = "cp437",
    cut_after: bool = True,
    open_drawer: bool = False,
    drawer_pin: int = 0,
):
    """
    طباعة إيصال POS كامل.
    
    Args:
        printer_name: اسم الطابعة في ويندوز
        receipt_data: بيانات الإيصال من Odoo POS
        paper_width: عرض الورقة (32, 42, 48 حرف)
        encoding: ترميز النص (cp437, cp1256)
        cut_after: قص الورقة
        open_drawer: فتح الدرج بعد الطباعة
        drawer_pin: منفذ الدرج
    """
    log.info("Printing receipt to '%s' (width=%d, encoding=%s)", printer_name, paper_width, encoding)
    
    try:
        commands = build_receipt_commands(
            receipt_data=receipt_data,
            paper_width=paper_width,
            encoding=encoding,
            cut_after=cut_after,
            open_drawer_after=open_drawer,
            drawer_pin=drawer_pin,
        )
        
        send_raw(printer_name, commands, job_name="POS Receipt")
        log.info("Receipt printed successfully (%d bytes)", len(commands))
        return True
        
    except Exception as e:
        log.error("Receipt printing failed: %s", e)
        raise


def print_raw_receipt(
    printer_name: str,
    raw_data: str,
    encoding: str = "utf-8",
    cut_after: bool = True,
):
    """
    طباعة بيانات خام (نص عادي أو base64).
    
    Args:
        printer_name: اسم الطابعة
        raw_data: البيانات (نص عادي أو base64)
        encoding: ترميز النص
        cut_after: قص الورقة
    """
    log.info("Printing raw data to '%s'", printer_name)
    
    try:
        # Check if base64 encoded
        try:
            data = base64.b64decode(raw_data)
        except Exception:
            # Not base64, treat as text
            data = raw_data.encode(encoding, errors="replace")
        
        # Add cut command if needed
        if cut_after:
            data += escpos_feed(3) + escpos_cut(partial=True)
        
        send_raw(printer_name, data, job_name="Raw Receipt")
        log.info("Raw receipt printed successfully (%d bytes)", len(data))
        return True
        
    except Exception as e:
        log.error("Raw receipt printing failed: %s", e)
        raise
