# dashboard.py
from config import APP_VERSION

def get_dashboard_html() -> str:
    return DASHBOARD_HTML.replace("{{VERSION}}", APP_VERSION)


DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl" x-data="app()" :class="{ 'dark': darkMode }">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GeniusStep CashDrawer Agent</title>
<script src="https://cdn.tailwindcss.com"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
<script>
tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: { sans: ['Segoe UI', 'Tahoma', 'Arial', 'sans-serif'] },
    }
  }
}
</script>
<style>
[x-cloak] { display: none !important; }
.fade-in { animation: fadeIn 0.3s ease-in; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
.pulse-dot { animation: pulse-dot 1.5s ease-in-out infinite; }
@keyframes drawer-open { 0% { transform: scaleX(1); } 50% { transform: scaleX(1.15); } 100% { transform: scaleX(1); } }
.drawer-anim { animation: drawer-open 0.5s ease-in-out; }
.toast-enter { animation: fadeIn 0.3s ease-in; }
/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #888; border-radius: 3px; }
</style>
</head>
<body class="bg-gray-50 dark:bg-gray-900 min-h-screen transition-colors duration-300">

<!-- Toast Notifications -->
<div class="fixed top-4 left-4 right-4 z-50 flex flex-col items-center gap-2 pointer-events-none" x-cloak>
  <template x-for="(toast, i) in toasts" :key="i">
    <div class="pointer-events-auto toast-enter px-4 py-3 rounded-lg shadow-lg text-sm font-medium max-w-md"
         :class="{
           'bg-green-500 text-white': toast.type==='success',
           'bg-red-500 text-white': toast.type==='error',
           'bg-blue-500 text-white': toast.type==='info',
           'bg-yellow-500 text-white': toast.type==='warning'
         }"
         x-text="toast.message"
         x-init="setTimeout(() => toasts.splice(i,1), 3500)">
    </div>
  </template>
</div>

<!-- Setup Wizard Overlay -->
<div x-show="showWizard" x-cloak
     class="fixed inset-0 bg-black/60 z-40 flex items-center justify-center p-4"
     x-transition:enter="transition ease-out duration-300"
     x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100">
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-lg w-full p-6 fade-in"
       @click.away="showWizard=false">

    <!-- Wizard Header -->
    <div class="text-center mb-6">
      <div class="text-4xl mb-2">⚙️</div>
      <h2 class="text-xl font-bold text-gray-800 dark:text-white" x-text="lang==='ar' ? 'مرحباً! إعداد أولي' : 'Welcome! Initial Setup'"></h2>
      <p class="text-gray-500 dark:text-gray-400 text-sm mt-1" x-text="lang==='ar' ? 'الخطوة ' + wizardStep + ' من 3' : 'Step ' + wizardStep + ' of 3'"></p>
      <!-- Progress -->
      <div class="flex gap-2 justify-center mt-3">
        <template x-for="s in 3">
          <div class="h-1.5 w-12 rounded-full transition-colors" :class="s <= wizardStep ? 'bg-blue-500' : 'bg-gray-200 dark:bg-gray-600'"></div>
        </template>
      </div>
    </div>

    <!-- Step 1: Printer -->
    <div x-show="wizardStep===1" class="space-y-4">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300" x-text="lang==='ar' ? 'اختر الطابعة' : 'Select Printer'"></label>
      <select x-model="config.printer_name"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2.5 bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent">
        <option value="" x-text="lang==='ar' ? '-- اختر طابعة --' : '-- Select Printer --'"></option>
        <template x-for="p in printers" :key="p">
          <option :value="p" x-text="p"></option>
        </template>
      </select>
      <button @click="loadPrinters()" class="text-sm text-blue-500 hover:text-blue-700" x-text="lang==='ar' ? '↻ تحديث القائمة' : '↻ Refresh List'"></button>
    </div>

    <!-- Step 2: Device Info -->
    <div x-show="wizardStep===2" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" x-text="lang==='ar' ? 'معرف الجهاز' : 'Device ID'"></label>
        <input type="text" x-model="config.device_id"
               class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2.5 bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500">
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" x-text="lang==='ar' ? 'رمز المصادقة' : 'Device Token'"></label>
        <input type="password" x-model="config.device_token"
               class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2.5 bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500">
      </div>
    </div>

    <!-- Step 3: Test -->
    <div x-show="wizardStep===3" class="text-center space-y-4">
      <p class="text-gray-600 dark:text-gray-300" x-text="lang==='ar' ? 'جرّب فتح درج النقدية للتأكد من أن كل شيء يعمل' : 'Test opening the cash drawer to verify everything works'"></p>
      <button @click="testDrawer()"
              class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              :disabled="testing">
        <span x-show="!testing" x-text="lang==='ar' ? '🔓 اختبار فتح الدرج' : '🔓 Test Open Drawer'"></span>
        <span x-show="testing" x-text="lang==='ar' ? '⏳ جارٍ...' : '⏳ Testing...'"></span>
      </button>
    </div>

    <!-- Wizard Navigation -->
    <div class="flex justify-between mt-6 pt-4 border-t dark:border-gray-700">
      <button x-show="wizardStep > 1" @click="wizardStep--"
              class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              x-text="lang==='ar' ? '← السابق' : '← Previous'"></button>
      <div x-show="wizardStep === 1"></div>
      <button x-show="wizardStep < 3" @click="wizardStep++"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              x-text="lang==='ar' ? 'التالي →' : 'Next →'"></button>
      <button x-show="wizardStep === 3" @click="finishWizard()"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              x-text="lang==='ar' ? '✓ إنهاء وحفظ' : '✓ Finish & Save'"></button>
    </div>
  </div>
</div>

<!-- Main App -->
<div class="max-w-4xl mx-auto px-4 py-6">

  <!-- Header -->
  <header class="flex items-center justify-between mb-6">
    <div class="flex items-center gap-3">
      <div class="bg-blue-500 text-white w-10 h-10 rounded-xl flex items-center justify-center text-lg font-bold shadow-lg">G</div>
      <div>
        <h1 class="text-lg font-bold text-gray-800 dark:text-white">GeniusStep CashDrawer</h1>
        <span class="text-xs text-gray-400" x-text="'v{{VERSION}}'"></span>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <!-- Language Toggle -->
      <button @click="toggleLang()"
              class="px-2 py-1.5 text-xs rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              x-text="lang==='ar' ? 'EN' : 'عربي'"></button>
      <!-- Dark Mode Toggle -->
      <button @click="darkMode = !darkMode; localStorage.setItem('darkMode', darkMode)"
              class="p-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
        <svg x-show="!darkMode" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
        <svg x-show="darkMode" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
      </button>
    </div>
  </header>

  <!-- Connection Status Bar -->
  <div class="mb-6 p-3 rounded-xl border transition-colors"
       :class="health.ws_connected ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="w-2.5 h-2.5 rounded-full pulse-dot"
             :class="health.ws_connected ? 'bg-green-500' : 'bg-red-500'"></div>
        <span class="text-sm font-medium"
              :class="health.ws_connected ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'"
              x-text="health.ws_connected ? (lang==='ar' ? 'متصل بالسيرفر' : 'Connected to server') : (lang==='ar' ? 'غير متصل' : 'Disconnected')"></span>
      </div>
      <div class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
        <span x-text="(lang==='ar' ? 'التشغيل: ' : 'Uptime: ') + health.uptime"></span>
        <span x-text="(lang==='ar' ? 'إعادات الاتصال: ' : 'Reconnects: ') + health.ws_reconnect_count"></span>
      </div>
    </div>
  </div>

  <!-- Stats Cards -->
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 shadow-sm">
      <div class="text-2xl font-bold text-blue-600 dark:text-blue-400" x-text="health.today_opens || 0"></div>
      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1" x-text="lang==='ar' ? 'عمليات اليوم' : 'Today Opens'"></div>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 shadow-sm">
      <div class="text-2xl font-bold text-purple-600 dark:text-purple-400" x-text="health.total_opens || 0"></div>
      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1" x-text="lang==='ar' ? 'إجمالي العمليات' : 'Total Opens'"></div>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 shadow-sm">
      <div class="text-2xl font-bold" :class="health.ws_connected ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'"
           x-text="health.ws_connected ? (lang==='ar' ? 'متصل' : 'Online') : (lang==='ar' ? 'منقطع' : 'Offline')"></div>
      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1" x-text="lang==='ar' ? 'حالة WebSocket' : 'WebSocket Status'"></div>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 shadow-sm">
      <div class="text-2xl font-bold text-orange-600 dark:text-orange-400" x-text="health.uptime || '0s'"></div>
      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1" x-text="lang==='ar' ? 'مدة التشغيل' : 'Uptime'"></div>
    </div>
  </div>

  <!-- Main Grid: Settings + Test -->
  <div class="grid md:grid-cols-3 gap-6 mb-6">

    <!-- Settings Card (2 cols) -->
    <div class="md:col-span-2 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <div class="p-4 border-b border-gray-100 dark:border-gray-700">
        <h2 class="font-semibold text-gray-800 dark:text-white flex items-center gap-2">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          <span x-text="lang==='ar' ? 'الإعدادات' : 'Settings'"></span>
        </h2>
      </div>
      <div class="p-4 space-y-4">
        <!-- Device ID -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1" x-text="lang==='ar' ? 'معرف الجهاز' : 'Device ID'"></label>
            <input type="text" x-model="config.device_id"
                   class="w-full border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow">
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1" x-text="lang==='ar' ? 'رمز المصادقة' : 'Device Token'"></label>
            <div class="relative">
              <input :type="showToken ? 'text' : 'password'" x-model="config.device_token"
                     class="w-full border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent pe-10 transition-shadow">
              <button @click="showToken = !showToken" class="absolute top-1/2 -translate-y-1/2 end-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                <svg x-show="!showToken" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                <svg x-show="showToken" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/></svg>
              </button>
            </div>
          </div>
        </div>

        <!-- WSS URL -->
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1" x-text="lang==='ar' ? 'عنوان خادم WebSocket' : 'WebSocket Server URL'"></label>
          <input type="url" x-model="config.wss_url" dir="ltr"
                 class="w-full border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow font-mono">
        </div>

        <!-- Printer -->
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1" x-text="lang==='ar' ? 'الطابعة' : 'Printer'"></label>
          <div class="flex gap-2">
            <select x-model="config.printer_name"
                    class="flex-1 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              <option value="" x-text="lang==='ar' ? '-- اختر طابعة --' : '-- Select Printer --'"></option>
              <template x-for="p in printers" :key="p">
                <option :value="p" x-text="p"></option>
              </template>
            </select>
            <button @click="loadPrinters()"
                    class="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    :disabled="loadingPrinters">
              <svg class="w-4 h-4" :class="loadingPrinters && 'animate-spin'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            </button>
          </div>
        </div>

        <!-- Drawer Pin + Pulse -->
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1" x-text="lang==='ar' ? 'منفذ الدرج' : 'Drawer Pin'"></label>
            <div class="flex gap-2">
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input type="radio" x-model.number="config.drawer_pin" value="0" class="text-blue-500 focus:ring-blue-500">
                <span class="text-sm text-gray-700 dark:text-gray-300">Pin 0</span>
              </label>
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input type="radio" x-model.number="config.drawer_pin" value="1" class="text-blue-500 focus:ring-blue-500">
                <span class="text-sm text-gray-700 dark:text-gray-300">Pin 1</span>
              </label>
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1" x-text="lang==='ar' ? 'نبضة ON (ms)' : 'Pulse ON (ms)'"></label>
            <input type="number" x-model.number="config.pulse_on" min="1" max="255"
                   class="w-full border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent">
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1" x-text="lang==='ar' ? 'نبضة OFF (ms)' : 'Pulse OFF (ms)'"></label>
            <input type="number" x-model.number="config.pulse_off" min="1" max="255"
                   class="w-full border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent">
          </div>
        </div>

        <!-- Save Button -->
        <button @click="saveConfig()"
                class="w-full bg-blue-500 hover:bg-blue-600 text-white py-2.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                :disabled="saving">
          <svg x-show="!saving" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
          <svg x-show="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
          <span x-text="saving ? (lang==='ar' ? 'جارٍ الحفظ...' : 'Saving...') : (lang==='ar' ? 'حفظ الإعدادات' : 'Save Settings')"></span>
        </button>
      </div>
    </div>

    <!-- Test & Diagnostics Card (1 col) -->
    <div class="space-y-4">
      <!-- Test Drawer -->
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm p-4">
        <h3 class="font-semibold text-gray-800 dark:text-white mb-3 flex items-center gap-2">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span x-text="lang==='ar' ? 'اختبار' : 'Test'"></span>
        </h3>
        <button @click="testDrawer()"
                class="w-full bg-green-500 hover:bg-green-600 active:bg-green-700 text-white py-4 rounded-lg font-bold text-lg transition-all"
                :class="drawerAnim && 'drawer-anim'"
                :disabled="testing">
          <span x-show="!testing">🔓 <span x-text="lang==='ar' ? 'فتح الدرج' : 'Open Drawer'"></span></span>
          <span x-show="testing">⏳ <span x-text="lang==='ar' ? 'جارٍ...' : 'Opening...'"></span></span>
        </button>
        <p class="text-xs text-gray-400 text-center mt-2" x-text="lang==='ar' ? 'اضغط لاختبار فتح درج النقدية' : 'Press to test the cash drawer'"></p>
      </div>

      <!-- Quick Diagnostics -->
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm p-4">
        <h3 class="font-semibold text-gray-800 dark:text-white mb-3 flex items-center gap-2">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
          <span x-text="lang==='ar' ? 'تشخيص سريع' : 'Diagnostics'"></span>
        </h3>
        <div class="space-y-2 text-sm">
          <div class="flex items-center justify-between py-1.5">
            <span class="text-gray-600 dark:text-gray-400" x-text="lang==='ar' ? 'API Server' : 'API Server'"></span>
            <span class="text-green-500 font-medium">● OK</span>
          </div>
          <div class="flex items-center justify-between py-1.5">
            <span class="text-gray-600 dark:text-gray-400">WebSocket</span>
            <span :class="health.ws_connected ? 'text-green-500' : 'text-red-500'" class="font-medium"
                  x-text="health.ws_connected ? '● OK' : '● ' + (lang==='ar' ? 'منقطع' : 'Down')"></span>
          </div>
          <div class="flex items-center justify-between py-1.5">
            <span class="text-gray-600 dark:text-gray-400" x-text="lang==='ar' ? 'الطابعة' : 'Printer'"></span>
            <span :class="config.printer_name ? 'text-green-500' : 'text-yellow-500'" class="font-medium"
                  x-text="config.printer_name ? '● ' + config.printer_name.substring(0,15) : '● ' + (lang==='ar' ? 'غير محدد' : 'Not set')"></span>
          </div>
          <div class="flex items-center justify-between py-1.5">
            <span class="text-gray-600 dark:text-gray-400" x-text="lang==='ar' ? 'المصادقة' : 'Auth'"></span>
            <span :class="config.device_token && config.device_token !== 'CHANGE_ME' ? 'text-green-500' : 'text-red-500'" class="font-medium"
                  x-text="config.device_token && config.device_token !== 'CHANGE_ME' ? '● OK' : '● ' + (lang==='ar' ? 'غير مُعدّ' : 'Not set')"></span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Activity Log -->
  <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm mb-6">
    <div class="p-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
      <h2 class="font-semibold text-gray-800 dark:text-white flex items-center gap-2">
        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <span x-text="lang==='ar' ? 'سجل العمليات' : 'Activity Log'"></span>
      </h2>
      <span class="text-xs text-gray-400" x-text="lang==='ar' ? 'تحديث تلقائي كل 5 ثوانٍ' : 'Auto-refresh every 5s'"></span>
    </div>
    <div class="max-h-72 overflow-y-auto">
      <div x-show="history.length === 0" class="p-8 text-center text-gray-400">
        <svg class="w-10 h-10 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/></svg>
        <span x-text="lang==='ar' ? 'لا توجد عمليات بعد' : 'No operations yet'"></span>
      </div>
      <template x-for="(entry, idx) in history" :key="idx">
        <div class="flex items-center gap-3 px-4 py-2.5 border-b border-gray-50 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
             :class="idx === 0 && 'fade-in'">
          <!-- Icon -->
          <div class="flex-shrink-0">
            <span x-show="entry.status==='ok' && entry.action==='OPEN_DRAWER'" class="text-green-500">✅</span>
            <span x-show="entry.status==='ok' && entry.action==='WS_CONNECT'" class="text-blue-500">🔗</span>
            <span x-show="entry.status==='ok' && entry.action==='UPDATE_CONFIG'" class="text-purple-500">⚙️</span>
            <span x-show="entry.status==='error'" class="text-red-500">❌</span>
            <span x-show="entry.action==='WS_DISCONNECT'" class="text-orange-500">🔌</span>
            <span x-show="entry.action==='WS_ERROR'" class="text-red-500">⚠️</span>
          </div>
          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div class="text-sm text-gray-700 dark:text-gray-300">
              <span class="font-medium" x-text="actionLabel(entry.action)"></span>
              <span x-show="entry.source" class="text-gray-400 text-xs" x-text="' — ' + sourceLabel(entry.source)"></span>
            </div>
            <div x-show="entry.detail" class="text-xs text-gray-400 truncate" x-text="entry.detail"></div>
          </div>
          <!-- Time -->
          <div class="flex-shrink-0 text-xs text-gray-400" x-text="entry.time_str"></div>
        </div>
      </template>
    </div>
  </div>

  <!-- Footer -->
  <footer class="text-center text-xs text-gray-400 dark:text-gray-600 py-4">
    GeniusStep CashDrawer Agent v{{VERSION}} &bull;
    <span x-text="lang==='ar' ? 'يعمل على' : 'Running on'"></span> http://127.0.0.1:16732
  </footer>
</div>

<script>
function app() {
  return {
    // State
    darkMode: localStorage.getItem('darkMode') === 'true' || window.matchMedia('(prefers-color-scheme: dark)').matches,
    lang: localStorage.getItem('lang') || 'ar',
    showWizard: false,
    wizardStep: 1,
    showToken: false,
    saving: false,
    testing: false,
    drawerAnim: false,
    loadingPrinters: false,
    toasts: [],

    // Data
    config: { device_id: '', device_token: '', wss_url: '', printer_name: '', drawer_pin: 0, pulse_on: 60, pulse_off: 120 },
    printers: [],
    health: { ws_connected: false, uptime: '0s', uptime_seconds: 0, total_opens: 0, today_opens: 0, ws_reconnect_count: 0, ws_last_error: '' },
    history: [],

    // Init
    init() {
      this.loadConfig();
      this.loadPrinters();
      this.loadHealth();
      this.loadHistory();
      // Auto-refresh
      setInterval(() => this.loadHealth(), 5000);
      setInterval(() => this.loadHistory(), 5000);
    },

    // Language
    toggleLang() {
      this.lang = this.lang === 'ar' ? 'en' : 'ar';
      localStorage.setItem('lang', this.lang);
      document.documentElement.dir = this.lang === 'ar' ? 'rtl' : 'ltr';
      document.documentElement.lang = this.lang;
    },

    // Toast
    toast(message, type = 'info') {
      this.toasts.push({ message, type });
    },

    // API calls
    async loadConfig() {
      try {
        const res = await fetch('/config');
        const data = await res.json();
        this.config = {
          device_id: data.device_id || '',
          device_token: data.device_token || '',
          wss_url: data.wss_url || '',
          printer_name: data.printer_name || '',
          drawer_pin: data.drawer_pin ?? 0,
          pulse_on: data.pulse_on ?? 60,
          pulse_off: data.pulse_off ?? 120,
        };
        // Show wizard if first run
        if (!data.printer_name && data.device_token === 'CHANGE_ME') {
          this.showWizard = true;
        }
      } catch (e) {
        this.toast(this.lang === 'ar' ? 'خطأ في تحميل الإعدادات' : 'Failed to load config', 'error');
      }
    },

    async loadPrinters() {
      this.loadingPrinters = true;
      try {
        const res = await fetch('/printers');
        const data = await res.json();
        this.printers = data.printers || [];
      } catch (e) {
        this.toast(this.lang === 'ar' ? 'خطأ في تحميل قائمة الطابعات' : 'Failed to load printers', 'error');
      } finally {
        this.loadingPrinters = false;
      }
    },

    async loadHealth() {
      try {
        const res = await fetch('/health');
        this.health = await res.json();
      } catch (e) { /* silent */ }
    },

    async loadHistory() {
      try {
        const res = await fetch('/history?limit=50');
        const data = await res.json();
        this.history = data.history || [];
      } catch (e) { /* silent */ }
    },

    async saveConfig() {
      this.saving = true;
      try {
        const body = {};
        for (const [k, v] of Object.entries(this.config)) {
          if (v !== '' && v !== null && v !== undefined) body[k] = v;
        }
        const res = await fetch('/config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        if (res.ok) {
          this.toast(this.lang === 'ar' ? 'تم حفظ الإعدادات بنجاح' : 'Settings saved successfully', 'success');
          this.loadHistory();
        } else {
          const err = await res.json();
          this.toast(err.detail || (this.lang === 'ar' ? 'خطأ في الحفظ' : 'Save failed'), 'error');
        }
      } catch (e) {
        this.toast(this.lang === 'ar' ? 'خطأ في الاتصال' : 'Connection error', 'error');
      } finally {
        this.saving = false;
      }
    },

    async testDrawer() {
      this.testing = true;
      try {
        const res = await fetch('/test/open_drawer', { method: 'POST' });
        if (res.ok) {
          this.drawerAnim = true;
          setTimeout(() => this.drawerAnim = false, 600);
          this.toast(this.lang === 'ar' ? 'تم فتح الدرج بنجاح!' : 'Drawer opened successfully!', 'success');
          this.loadHistory();
        } else {
          const err = await res.json();
          let msg = err.detail || '';
          if (msg.includes('empty')) {
            msg = this.lang === 'ar' ? 'الطابعة غير محددة. اختر طابعة من الإعدادات أولاً.' : 'Printer not set. Select a printer first.';
          } else if (msg.includes('not found') || msg.includes('Invalid')) {
            msg = this.lang === 'ar' ? 'الطابعة غير موجودة. تأكد من أنها متصلة ومُشغّلة.' : 'Printer not found. Make sure it is connected and powered on.';
          } else if (msg.includes('Rate limit')) {
            msg = this.lang === 'ar' ? 'تم تجاوز الحد الأقصى. انتظر قليلاً.' : 'Rate limit exceeded. Please wait.';
          }
          this.toast(msg, 'error');
        }
      } catch (e) {
        this.toast(this.lang === 'ar' ? 'خطأ في الاتصال بالخدمة' : 'Service connection error', 'error');
      } finally {
        this.testing = false;
      }
    },

    async finishWizard() {
      await this.saveConfig();
      this.showWizard = false;
    },

    // Labels
    actionLabel(action) {
      const labels = {
        'OPEN_DRAWER': this.lang === 'ar' ? 'فتح درج النقدية' : 'Open Cash Drawer',
        'WS_CONNECT': this.lang === 'ar' ? 'اتصال بالسيرفر' : 'Connected to Server',
        'WS_DISCONNECT': this.lang === 'ar' ? 'انقطاع الاتصال' : 'Disconnected',
        'WS_ERROR': this.lang === 'ar' ? 'خطأ في الاتصال' : 'Connection Error',
        'UPDATE_CONFIG': this.lang === 'ar' ? 'تحديث الإعدادات' : 'Config Updated',
      };
      return labels[action] || action;
    },

    sourceLabel(source) {
      const labels = {
        'websocket': 'WebSocket',
        'rest_api': 'REST API',
        'test': this.lang === 'ar' ? 'اختبار يدوي' : 'Manual Test',
      };
      return labels[source] || source;
    },
  };
}
</script>
</body>
</html>"""
