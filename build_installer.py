# build_installer.py
# سكريبت لبناء ملف قابل للتثبيت على Windows
import PyInstaller.__main__
import os

# إعدادات البناء
app_name = "GeniusStepCashDrawerAgent"
main_script = "app.py"
icon_path = None  # يمكنك إضافة مسار أيقونة .ico هنا

# بناء الأوامر
args = [
    main_script,
    '--name', app_name,
    '--onefile',
    '--console',  # نافذة console لرؤية السجلات
    '--clean',
    '--noconfirm',
]

# إذا كان هناك أيقونة
if icon_path and os.path.exists(icon_path):
    args.extend(['--icon', icon_path])

# إضافة مكتبات مخفية
hidden_imports = [
    'win32print',
    'win32api',
    'win32con',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'websockets',
    'pydantic',
    'fastapi',
    'starlette',
    'h11',
    'click',
    'anyio',
    'logger',
    'config',
    'state',
    'dashboard',
    'web_ui',
    'ws_client',
    'printer_raw',
]

for imp in hidden_imports:
    args.extend(['--hidden-import', imp])

# تشغيل PyInstaller
print(f"Building {app_name}...")
PyInstaller.__main__.run(args)
print(f"Build complete! Output: dist/{app_name}.exe")
