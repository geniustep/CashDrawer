# GeniusStep CashDrawer Agent v2.0

وكيل يعمل على **Windows** للتحكم في **درج النقدية (Cash Drawer)** عبر طابعة ESC/POS، ومتكامل مع نظام نقاط البيع GeniusStep.

---

## المميزات

| الميزة | الوصف |
|--------|--------|
| التحكم في درج النقدية | فتح الدرج عبر أوامر ESC/POS المرسلة للطابعة |
| التواصل مع الخادم | اتصال WebSocket مستمر مع خادم GeniusStep |
| لوحة تحكم ويب مدمجة | واجهة مستخدم كاملة على المنفذ 16732 |
| معالج الإعداد الأول | wizard تفاعلي عند أول تشغيل |
| سجل العمليات | تتبع آخر 200 عملية مع تحديث لحظي |
| نظام تسجيل متقدم | ملفات log دوارة مع تتبع كامل |
| إعادة اتصال ذكية | Exponential backoff (3s → 30s) |
| حماية Rate Limiting | حد أقصى 10 عمليات/دقيقة |
| دعم RTL كامل | واجهة عربية/إنجليزية مع تبديل اللغة |
| الوضع المظلم | تبديل تلقائي أو يدوي |
| تشخيص سريع | فحص حالة كل المكونات |
| فتح المتصفح تلقائياً | يفتح لوحة التحكم عند التشغيل |
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
3. سيفتح المتصفح تلقائياً على لوحة التحكم.
4. إذا كانت هذه المرة الأولى، سيظهر **معالج الإعداد**:
   - **الخطوة 1:** اختر الطابعة من القائمة.
   - **الخطوة 2:** أدخل **device_id** و **device_token** من نظام GeniusStep.
   - **الخطوة 3:** اختبر فتح درج النقدية.
5. بعد الإعداد، يعمل البرنامج في الخلفية ويستجيب لأوامر السيرفر تلقائياً.

> **ملاحظة:** الملف EXE مستقل ولا يحتاج تثبيت Python أو أي برامج إضافية.

---

## لوحة التحكم

عند فتح المتصفح على **http://127.0.0.1:16732** ستجد:

- **شريط الحالة**: مؤشر اتصال لحظي (أخضر/أحمر)
- **بطاقات الإحصائيات**: عمليات اليوم، الإجمالي، حالة الاتصال، مدة التشغيل
- **نموذج الإعدادات**: تعديل كل الإعدادات مع حفظ فوري
- **زر الاختبار**: فتح الدرج يدوياً للتأكد من العمل
- **التشخيص السريع**: حالة API، WebSocket، الطابعة، المصادقة
- **سجل العمليات**: آخر 50 عملية مع تحديث تلقائي كل 5 ثوانٍ

---

## واجهة API (REST)

| الطريقة | المسار | الوصف |
|---------|--------|--------|
| GET | `/` | لوحة التحكم (Dashboard) |
| GET | `/printers` | قائمة الطابعات المتاحة على Windows |
| GET | `/config` | قراءة الإعدادات الحالية (Token مخفي جزئياً) |
| POST | `/config` | تحديث الإعدادات (body: JSON مع Pydantic validation) |
| POST | `/test/open_drawer` | اختبار فتح درج النقدية (مع rate limiting) |
| GET | `/health` | حالة التطبيق وكل المكونات |
| GET | `/history` | سجل العمليات الأخيرة (?limit=50) |
| GET | `/version` | إصدار التطبيق |

**مثال قراءة الإعدادات:**
```bash
curl http://127.0.0.1:16732/config
```

**مثال تحديث الإعدادات:**
```bash
curl -X POST http://127.0.0.1:16732/config \
  -H "Content-Type: application/json" \
  -d "{\"printer_name\": \"EPSON TM-T88VI\", \"device_id\": \"POS-001\"}"
```

**مثال فحص الصحة:**
```bash
curl http://127.0.0.1:16732/health
```

---

## الإعدادات

الإعدادات تُحفظ في الملف:

```
C:\ProgramData\GeniusStep\CashDrawerAgent\config.json
```

| الحقل | الوصف | القيمة الافتراضية | التحقق |
|-------|--------|-------------------|--------|
| device_id | معرف الجهاز في GeniusStep | POS-001 | نص |
| device_token | رمز المصادقة | CHANGE_ME | نص |
| wss_url | عنوان خادم WebSocket | wss://app.propanel.ma/hardware/ws | URL |
| printer_name | اسم الطابعة كما في Windows | (فارغ) | نص |
| drawer_pin | منفذ الدرج | 0 | 0 أو 1 |
| pulse_on | مدة النبضة الأولى (ms) | 60 | 1-255 |
| pulse_off | مدة النبضة الثانية (ms) | 120 | 1-255 |

---

## السجلات (Logs)

```
C:\ProgramData\GeniusStep\CashDrawerAgent\logs\agent.log
```

- ملفات دوارة: 5 MB × 3 ملفات
- تسجيل في Console + ملف
- مستويات: INFO, WARNING, ERROR, DEBUG

---

## أوامر WebSocket المدعومة

| الأمر | الاتجاه | الوصف |
|-------|---------|--------|
| HELLO | Client → Server | تعريف الجهاز عند الاتصال |
| OPEN_DRAWER | Server → Client | فتح درج النقدية |
| PING | Server → Client | فحص الاتصال |
| GET_STATUS | Server → Client | طلب حالة الجهاز |
| UPDATE_CONFIG | Server → Client | تحديث الإعدادات عن بُعد |
| ACK | Client → Server | تأكيد تنفيذ الأمر |

---

## البناء من المصدر (للمطورين)

### المتطلبات

- Windows 10 أو أحدث
- Python 3.10+
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
CashDrawer/
├── app.py              # نقطة الدخول: إدارة الخيوط + graceful shutdown
├── web_ui.py           # FastAPI: كل endpoints + تقديم لوحة التحكم
├── ws_client.py        # عميل WebSocket: اتصال ذكي + أوامر متعددة
├── printer_raw.py      # إرسال أوامر ESC/POS للطابعة
├── config.py           # إعدادات: Pydantic validation + تخزين مؤقت thread-safe
├── logger.py           # نظام تسجيل مركزي (RotatingFileHandler)
├── state.py            # حالة مشتركة: سجل + rate limiter + إحصائيات
├── dashboard.py        # واجهة HTML مدمجة (Alpine.js + Tailwind CSS)
├── requirements.txt    # مكتبات Python
├── GeniusStepCashDrawerAgent.spec  # إعدادات PyInstaller
├── build_installer.py  # سكريبت بناء PyInstaller
├── setup_windows.py    # سكريبت بناء cx_Freeze (بديل)
├── build.bat           # سكريبت بناء Windows Batch
├── build.ps1           # سكريبت بناء PowerShell
└── dist/
    └── GeniusStepCashDrawerAgent.exe
```

---

## استكشاف الأخطاء

| المشكلة | الحل المقترح |
|---------|---------------|
| الملف EXE لا يبدأ | تشغيله من Command Prompt لرؤية رسائل الخطأ |
| لا يفتح المتصفح | انتقل يدوياً إلى http://127.0.0.1:16732 |
| لا يفتح درج النقدية | تحقق من اسم الطابعة + جرب تغيير drawer_pin (0 أو 1) |
| انقطاع WebSocket | تحقق من الإنترنت + تحقق من device_id و device_token |
| Rate limit exceeded | انتظر دقيقة واحدة (الحد: 10 عمليات/دقيقة) |
| خطأ في السجلات | راجع `C:\ProgramData\GeniusStep\CashDrawerAgent\logs\agent.log` |

---

## الترخيص والاستخدام

يمكن توزيع ملف **GeniusStepCashDrawerAgent.exe** واستخدامه على أجهزة Windows دون الحاجة إلى ملفات إضافية.
