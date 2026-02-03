# setup_windows.py
# سكريبت بديل لإنشاء installer باستخدام cx_Freeze
from cx_Freeze import setup, Executable
import sys

# الملفات المطلوبة
build_exe_options = {
    "packages": [
        "asyncio",
        "threading",
        "uvicorn",
        "fastapi",
        "websockets",
        "pydantic",
        "win32print",
        "win32api",
        "win32con",
        "json",
        "pathlib",
    ],
    "includes": [
        "app",
        "web_ui",
        "ws_client",
        "printer_raw",
        "config",
    ],
    "excludes": ["tkinter", "matplotlib", "numpy", "pandas"],
    "include_files": [],
    "optimize": 2,
}

# إعدادات التنفيذ
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # بدون نافذة console
    # استخدم base = None إذا أردت رؤية نافذة console

executables = [
    Executable(
        "app.py",
        base=base,
        target_name="GeniusStepCashDrawerAgent.exe",
        icon=None,  # يمكنك إضافة مسار أيقونة .ico هنا
    )
]

setup(
    name="GeniusStep CashDrawer Agent",
    version="1.0.0",
    description="وكيل GeniusStep للتحكم في درج النقدية",
    options={"build_exe": build_exe_options},
    executables=executables,
)
