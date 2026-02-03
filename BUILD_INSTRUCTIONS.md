# تعليمات بناء ملف قابل للتثبيت على Windows

## الطريقة 1: استخدام PyInstaller (موصى بها)

### 1. تثبيت المتطلبات
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. البناء باستخدام ملف spec
```bash
pyinstaller GeniusStepCashDrawerAgent.spec
```

### 3. البناء باستخدام سكريبت Python
```bash
python build_installer.py
```

### 4. النتيجة
الملف التنفيذي سيكون في مجلد `dist/GeniusStepCashDrawerAgent.exe`

---

## الطريقة 2: استخدام cx_Freeze

### 1. تثبيت cx_Freeze
```bash
pip install cx_Freeze
```

### 2. البناء
```bash
python setup_windows.py build
```

### 3. النتيجة
الملف التنفيذي سيكون في مجلد `build/exe.win-amd64-3.x/`

---

## الطريقة 3: البناء اليدوي مع PyInstaller

```bash
pyinstaller --onefile --name GeniusStepCashDrawerAgent --console app.py
```

---

## ملاحظات مهمة

1. **نافذة Console**: 
   - إذا أردت إخفاء نافذة console، غيّر `console=True` إلى `console=False` في ملف `.spec`
   - أو استخدم `--windowed` بدلاً من `--console` في الأوامر

2. **الأيقونة**:
   - يمكنك إضافة أيقونة بتنسيق `.ico` عبر تعديل `icon=None` في الملفات

3. **اختبار الملف**:
   - بعد البناء، اختبر الملف على جهاز Windows
   - تأكد من أن جميع المكتبات متوفرة

4. **توزيع الملف**:
   - الملف `.exe` الناتج يمكن توزيعه مباشرة
   - لا حاجة لتثبيت Python على الجهاز المستهدف

---

## إنشاء Installer احترافي (اختياري)

لإنشاء installer احترافي مع واجهة رسومية، يمكنك استخدام:
- **Inno Setup** (مجاني)
- **NSIS** (مجاني)
- **WiX Toolset** (مجاني من Microsoft)
