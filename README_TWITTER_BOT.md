# Twitter Auto-Post Bot - دليل التشغيل

بوت أوتوماتيكي لنشر المنتجات على تويتر بشكل عشوائي.

## المتطلبات

- Python 3.7 أو أحدث
- حساب Twitter Developer مع API v2 access

## التثبيت

### 1. تثبيت المكتبات المطلوبة

```bash
pip install -r requirements.txt
```

### 2. الحصول على مفاتيح Twitter API

1. اذهب إلى [Twitter Developer Portal](https://developer.twitter.com/)
2. أنشئ تطبيق جديد (New App)
3. احصل على المفاتيح التالية:
   - API Key
   - API Key Secret
   - Access Token
   - Access Token Secret

### 3. ضبط المتغيرات البيئية

#### على Windows:

```cmd
set TWITTER_API_KEY=your_api_key_here
set TWITTER_API_KEY_SECRET=your_api_secret_here
set TWITTER_ACCESS_TOKEN=your_access_token_here
set TWITTER_ACCESS_TOKEN_SECRET=your_access_secret_here
```

أو استخدم PowerShell:

```powershell
$env:TWITTER_API_KEY="your_api_key_here"
$env:TWITTER_API_KEY_SECRET="your_api_secret_here"
$env:TWITTER_ACCESS_TOKEN="your_access_token_here"
$env:TWITTER_ACCESS_TOKEN_SECRET="your_access_secret_here"
```

#### على Linux/Mac:

```bash
export TWITTER_API_KEY="your_api_key_here"
export TWITTER_API_KEY_SECRET="your_api_secret_here"
export TWITTER_ACCESS_TOKEN="your_access_token_here"
export TWITTER_ACCESS_TOKEN_SECRET="your_access_secret_here"
```

## الاستخدام

### تشغيل يدوي

```bash
python twitter_bot.py
```

### جدولة على Windows (Task Scheduler)

1. افتح Task Scheduler
2. اضغط "Create Basic Task"
3. اختر التكرار (يومي، كل ساعة، إلخ)
4. في Action، اختر "Start a program"
5. Program/script: `python`
6. Add arguments: `"C:\path\to\twitter_bot.py"`
7. في Settings tab:
   - أضف المتغيرات البيئية في "Start in" directory
   - أو استخدم batch file:

**tweet_scheduler.bat:**
```batch
@echo off
set TWITTER_API_KEY=your_key
set TWITTER_API_KEY_SECRET=your_secret
set TWITTER_ACCESS_TOKEN=your_token
set TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
cd C:\path\to\iraq-ninja-store
python twitter_bot.py >> logs\twitter_bot.log 2>&1
```

### جدولة على Linux (Cron)

1. افتح crontab:
```bash
crontab -e
```

2. أضف سطر للتشغيل (مثال: كل 4 ساعات):
```
0 */4 * * * cd /path/to/iraq-ninja-store && /usr/bin/python3 twitter_bot.py >> logs/twitter_bot.log 2>&1
```

3. أو استخدم ملف bash script:

**tweet_scheduler.sh:**
```bash
#!/bin/bash
export TWITTER_API_KEY="your_key"
export TWITTER_API_KEY_SECRET="your_secret"
export TWITTER_ACCESS_TOKEN="your_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_token_secret"

cd /path/to/iraq-ninja-store
python3 twitter_bot.py
```

ثم:
```bash
chmod +x tweet_scheduler.sh
```

## شكل التغريدة

البوت ينشئ تغريدات بهذا الشكل:

```
🛒 جهاز اعداد الفشار

💰 السعر: 48,400 د.ع
❌ بدلاً من: 73,400 د.ع
🔥 خصم 34%

🔗 https://sherow1982.github.io/iraq-ninja-store/#1

#العراق #تسوق_اونلاين #عروض #تخفيضات
```

## الميزات

- ✅ اختيار منتج عشوائي من products.json
- ✅ حساب نسبة الخصم تلقائياً
- ✅ تنسيق جميل مع إيموجي
- ✅ رابط مباشر للمنتج
- ✅ هاشتاجات مناسبة
- ✅ احترام حد 280 حرف
- ✅ معالجة الأخطاء
- ✅ سجل (logs) مفصل

## استكشاف الأخطاء

### خطأ: "مفاتيح Twitter API غير موجودة"

تأكد من ضبط المتغيرات البيئية الأربعة.

### خطأ: "requests_oauthlib غير مثبتة"

```bash
pip install requests-oauthlib
```

### خطأ: "401 Unauthorized"

تحقق من صحة المفاتيح والتوكنز.

### خطأ: "403 Forbidden"

تأكد من أن التطبيق لديه صلاحيات الكتابة (Write permissions).

### خطأ: "429 Too Many Requests"

وصلت لحد الطلبات. انتظر قليلاً قبل المحاولة مرة أخرى.

## نصائح

1. **لا تنشر بشكل متكرر جداً**: Twitter لديه حدود على عدد التغريدات
2. **جدولة ذكية**: مثلاً كل 4-6 ساعات
3. **تنويع المحتوى**: البوت يختار منتجات عشوائية تلقائياً
4. **مراقبة السجلات**: تحقق من logs للتأكد من نجاح النشر

## الدعم

للمساعدة أو الأسئلة، راجع:
- [Twitter API Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [GitHub Issues](https://github.com/sherow1982/iraq-ninja-store/issues)

---

**ملاحظة مهمة**: احفظ مفاتيح API بشكل آمن ولا ترفعها على GitHub!
