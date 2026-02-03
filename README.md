# GeniusStep CashDrawer Agent

وكيل يعمل على **Windows** للتحكم في **درج النقدية (Cash Drawer)** عبر طابعة ESC/POS، ومتكامل مع نظام نقاط البيع GeniusStep.

---

## المميزات

| الميزة | الوصف |
|--------|--------|
| التحكم في درج النقدية | فتح الدرج عبر أوامر ESC/POS المرسلة للطابعة |
| التواصل مع الخادم | اتصال WebSocket مستمر مع خادم GeniusStep |
| واجهة REST API | إعدادات واختبار من المتصفح على المنفذ 16732 |
| إعادة الاتصال التلقائي | إعادة المحاولة تلقائياً عند انقطاع WebSocket |
| ملف EXE مستقل | لا يحتاج تثبيت Python أو أي مكتبات إضافية |

---

## المتطلبات

- **Windows 10** أو أحدث
- طابعة **ESC/POS** متصلة (لدرج النقدية)
- اتصال إنترنت (للاتصال بخادم WebSocket)

---

## التثبيت والاستخدام (للمستخدم النهائي)

1. انسخ الملف **`GeniusStepCashDrawerAgent.exe`** من مجلد `dist\` إلى أي مكان على الجهاز.
2. شغّل الملف بالنقر المزدوج عليه.
3. عند ظهور نافذة سوداء (Console) فهذا يعني أن البرنامج يعمل.
4. افتح المتصفح وانتقل إلى: **http://127.0.0.1:16732**
5. من واجهة الويب:
   - اختر الطابعة من القائمة.
   - أدخل **device_id** و **device_token** من نظام GeniusStep.
   - اضبط **drawer_pin** (0 أو 1) حسب الطابعة إن لزم.
   - استخدم **اختبار فتح درج النقدية** للتأكد من العمل.

> **ملاحظة:** الملف EXE مستقل ولا يحتاج تثبيت Python أو أي برامج إضافية.

---

## واجهة API (REST)

| الطريقة | المسار | الوصف |
|---------|--------|--------|
| GET | `/printers` | قائمة الطابعات المتاحة على Windows |
| GET | `/config` | قراءة الإعدادات الحالية |
| POST | `/config` | تحديث الإعدادات (body: JSON) |
| POST | `/test/open_drawer` | اختبار فتح درج النقدية |

**مثال قراءة الإعدادات:**
```bash
curl http://127.0.0.1:16732/config
```

**مثال تحديث الإعدادات:**
```bash
curl -X POST http://127.0.0.1:16732/config -H "Content-Type: application/json" -d "{\"printer_name\": \"اسم الطابعة\", \"device_id\": \"POS-001\"}"
```

---

## الإعدادات

الإعدادات تُحفظ في الملف:

```
C:\ProgramData\GeniusStep\CashDrawerAgent\config.json
```

| الحقل | الوصف | القيمة الافتراضية |
|-------|--------|-------------------|
| device_id | معرف الجهاز في GeniusStep | POS-001 |
| device_token | رمز المصادقة | CHANGE_ME |
| wss_url | عنوان خادم WebSocket | wss://app.propanel.ma/hardware/ws |
| printer_name | اسم الطابعة كما في Windows | (فارغ) |
| drawer_pin | منفذ الدرج (0 أو 1) | 0 |
| pulse_on | مدة النبضة الأولى (ms) | 60 |
| pulse_off | مدة النبضة الثانية (ms) | 120 |

---

## البناء من المصدر (للمطورين)

### المتطلبات

- Windows 10 أو أحدث
- Python 3.8+
- اتصال إنترنت

### خطوات البناء

1. تثبيت المتطلبات:
   ```cmd
   python -m pip install -r requirements.txt
   ```

2. بناء ملف EXE:
   ```cmd
   python -m PyInstaller GeniusStepCashDrawerAgent.spec --clean --noconfirm
   ```

3. الملف الناتج:
   ```
   dist\GeniusStepCashDrawerAgent.exe
   ```

### التشغيل للتطوير

```cmd
pip install -r requirements.txt
python app.py
```

ثم افتح المتصفح على: http://127.0.0.1:16732

---

## هيكل المشروع

```
agent windows/
├── app.py              # نقطة الدخول الرئيسية
├── web_ui.py           # واجهة FastAPI (REST)
├── ws_client.py        # عميل WebSocket
├── printer_raw.py      # إرسال أوامر RAW للطابعة (ESC/POS)
├── config.py           # تحميل وحفظ الإعدادات
├── requirements.txt    # مكتبات Python
├── GeniusStepCashDrawerAgent.spec  # إعدادات PyInstaller
├── build.bat / build.ps1   # سكربتات البناء
└── dist/
    └── GeniusStepCashDrawerAgent.exe   # الملف التنفيذي
```

---

## استكشاف الأخطاء

| المشكلة | الحل المقترح |
|---------|---------------|
| الملف EXE لا يبدأ | تشغيله من Command Prompt لرؤية رسائل الخطأ |
| لا يفتح المتصفح الصفحة | التأكد من أن البرنامج يعمل وظهور "Uvicorn running on http://127.0.0.1:16732" |
| لا يفتح درج النقدية | التحقق من اسم الطابعة وتجربة تغيير `drawer_pin` (0 أو 1) |
| انقطاع WebSocket | التحقق من الإنترنت و`device_id` و`device_token` و`wss_url` |

---

## الترخيص والاستخدام

يمكن توزيع ملف **GeniusStepCashDrawerAgent.exe** واستخدامه على أجهزة Windows دون الحاجة إلى ملفات إضافية.
