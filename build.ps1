# build.ps1
# سكريبت PowerShell لبناء GeniusStep CashDrawer Agent

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "بناء GeniusStep CashDrawer Agent" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# البحث عن Python
$python = $null
$pythonPaths = @(
    "python",
    "python3",
    "py",
    "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
    "$env:ProgramFiles\Python*\python.exe"
)

foreach ($path in $pythonPaths) {
    try {
        if ($path -like "*\*") {
            $found = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) {
                $python = $found.FullName
                break
            }
        } else {
            $result = Get-Command $path -ErrorAction SilentlyContinue
            if ($result) {
                $python = $result.Source
                break
            }
        }
    } catch {
        continue
    }
}

if (-not $python) {
    Write-Host "خطأ: Python غير مثبت أو غير موجود في PATH" -ForegroundColor Red
    Write-Host "يرجى تثبيت Python من python.org أو Microsoft Store" -ForegroundColor Yellow
    Read-Host "اضغط Enter للخروج"
    exit 1
}

Write-Host "[1/3] تثبيت المتطلبات..." -ForegroundColor Yellow
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "خطأ في تثبيت المتطلبات" -ForegroundColor Red
    Read-Host "اضغط Enter للخروج"
    exit 1
}

Write-Host ""
Write-Host "[2/3] تنظيف البناء السابق..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }
Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force

Write-Host ""
Write-Host "[3/3] بناء الملف التنفيذي (هذا قد يستغرق بضع دقائق)..." -ForegroundColor Yellow
& $python -m PyInstaller GeniusStepCashDrawerAgent.spec --clean --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "خطأ في عملية البناء" -ForegroundColor Red
    Read-Host "اضغط Enter للخروج"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "تم البناء بنجاح!" -ForegroundColor Green
Write-Host "الملف موجود في: dist\GeniusStepCashDrawerAgent.exe" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Read-Host "اضغط Enter للخروج"
