@echo off
chcp 65001 >nul
echo ========================================
echo بناء GeniusStep CashDrawer Agent
echo ========================================
echo.

REM التحقق من تثبيت Python
python --version >nul 2>&1
if errorlevel 1 (
    echo خطأ: Python غير مثبت أو غير موجود في PATH
    pause
    exit /b 1
)

echo [1/3] تثبيت المتطلبات...
pip install -r requirements.txt
if errorlevel 1 (
    echo خطأ في تثبيت المتطلبات
    pause
    exit /b 1
)

echo.
echo [2/3] تنظيف البناء السابق...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
for /d %%d in (__pycache__) do rmdir /s /q "%%d"

echo.
echo [3/3] بناء الملف التنفيذي...
pyinstaller GeniusStepCashDrawerAgent.spec
if errorlevel 1 (
    echo خطأ في عملية البناء
    pause
    exit /b 1
)

echo.
echo ========================================
echo تم البناء بنجاح!
echo الملف موجود في: dist\GeniusStepCashDrawerAgent.exe
echo ========================================
pause
