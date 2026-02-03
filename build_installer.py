# build_installer.py
# سكريبت لبناء ملف قابل للتثبيت على Windows
import PyInstaller.__main__
import sys
import os

# إعدادات البناء
app_name = "GeniusStepCashDrawerAgent"
main_script = "app.py"
icon_path = None  # يمكنك إضافة مسار أيقونة .ico هنا

# بناء الأوامر
args = [
    main_script,
    '--name', app_name,
    '--onefile',  # ملف واحد قابل للتنفيذ
    '--windowed',  # بدون نافذة console (استخدم --console إذا أردت رؤية السجلات)
    '--clean',  # تنظيف الملفات المؤقتة
    '--noconfirm',  # تأكيد تلقائي
]

# إذا كان هناك أيقونة
if icon_path and os.path.exists(icon_path):
    args.extend(['--icon', icon_path])

# إضافة ملفات البيانات إذا لزم الأمر
# args.extend(['--add-data', 'path/to/data;data'])

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
]

for imp in hidden_imports:
    args.extend(['--hidden-import', imp])

# تشغيل PyInstaller
print(f"جاري بناء {app_name}...")
PyInstaller.__main__.run(args)
print(f"تم البناء بنجاح! الملف موجود في مجلد dist/")
