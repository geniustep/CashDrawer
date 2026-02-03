# web_ui.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, Response
import win32print
from config import (
    load_config, save_config, AgentConfig,
    ConfigUpdatePayload, APP_VERSION,
)
from printer_raw import open_drawer
from state import app_state
from dashboard import get_dashboard_html
from logger import get_logger

log = get_logger("web_ui")

app = FastAPI(title="GeniusStep CashDrawer Agent", version=APP_VERSION)

# CORS: السماح لطلبات من واجهة Odoo POS (متصفح على نفس الجهاز أو خادم Odoo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ── Dashboard ──

@app.get("/", response_class=HTMLResponse)
def dashboard():
    """صفحة لوحة التحكم الرئيسية."""
    return get_dashboard_html()


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """تفادي 404 عند طلب المتصفح للأيقونة."""
    return Response(status_code=204)


# ── API Endpoints ──

@app.get("/printers")
def list_printers():
    """قائمة الطابعات المثبتة على النظام."""
    try:
        printers = [
            p[2] for p in win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            )
        ]
        log.info("Listed %d printers", len(printers))
        return {"printers": printers}
    except Exception as e:
        log.error("Failed to list printers: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
def get_config():
    """قراءة الإعدادات مع إخفاء جزء من Token."""
    cfg = load_config()
    data = cfg.model_dump()
    # إخفاء Token - إظهار آخر 4 أحرف فقط
    token = data.get("device_token", "")
    if len(token) > 4:
        data["device_token_masked"] = "●" * (len(token) - 4) + token[-4:]
    else:
        data["device_token_masked"] = "●" * len(token)
    return data


@app.post("/config")
def set_config(payload: ConfigUpdatePayload):
    """تحديث الإعدادات مع التحقق من صحة البيانات."""
    cfg = load_config()
    update_data = payload.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    try:
        new_cfg = AgentConfig(**{**cfg.model_dump(), **update_data})
        save_config(new_cfg)
        log.info("Config updated via REST: %s", list(update_data.keys()))

        result = new_cfg.model_dump()
        token = result.get("device_token", "")
        if len(token) > 4:
            result["device_token_masked"] = "●" * (len(token) - 4) + token[-4:]
        else:
            result["device_token_masked"] = "●" * len(token)

        app_state.add_history(
            action="UPDATE_CONFIG", source="rest_api", status="ok",
            detail=f"Updated: {', '.join(update_data.keys())}",
        )
        return {"ok": True, "config": result}
    except Exception as e:
        log.error("Config update failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/test/open_drawer")
def test_open_drawer():
    """اختبار فتح درج النقدية."""
    # Rate limiting
    if not app_state.drawer_rate_limiter.allow():
        log.warning("Rate limit exceeded for test open_drawer")
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    cfg = load_config()
    try:
        open_drawer(cfg.printer_name, cfg.drawer_pin, cfg.pulse_on, cfg.pulse_off)
        log.info("Test drawer open: OK")
        app_state.add_history(
            action="OPEN_DRAWER", source="test", status="ok",
        )
        return {"ok": True}
    except Exception as e:
        log.error("Test drawer open failed: %s", e)
        app_state.add_history(
            action="OPEN_DRAWER", source="test", status="error", detail=str(e),
        )
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
def health_check():
    """فحص صحة التطبيق وحالة المكونات."""
    return app_state.health_dict()


@app.get("/history")
def get_history(limit: int = 50):
    """سجل العمليات الأخيرة."""
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200
    return {"history": app_state.get_history(limit=limit)}


@app.get("/version")
def get_version():
    """إرجاع إصدار التطبيق."""
    return {"version": APP_VERSION}


# ── تجنب 404: توجيه أي مسار غير معرّف إلى الصفحة الرئيسية ──

@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
def catch_all(full_path: str):
    """أي مسار غير معرّف (مثل /dashboard أو /index) يعيد لوحة التحكم."""
    return get_dashboard_html()
