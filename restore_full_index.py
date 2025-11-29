#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت لاستعادة index.html الأصلي الكامل وإضافة الشات بوت تلقائياً

الاستخدام:
    python restore_full_index.py
"""

import subprocess
import sys
import os

def run_command(cmd):
    """تنفيذ أمر وإرجاع النتيجة"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    print("🚀 بدء عملية الاستعادة...\n")
    
    # 1. التأكد من وجود git
    print("1️⃣ التحقق من Git...")
    success, _, _ = run_command("git --version")
    if not success:
        print("❌ Git غير مثبت! يرجى تثبيته أولاً.")
        sys.exit(1)
    print("   ✅ Git موجود\n")
    
    # 2. جلب آخر التحديثات
    print("2️⃣ جلب آخر التحديثات من الريبو...")
    success, _, err = run_command("git fetch origin")
    if not success:
        print(f"   ⚠️ تحذير: {err}")
    else:
        print("   ✅ تم جلب التحديثات\n")
    
    # 3. استعادة الملف الأصلي من الكوميت القديم
    print("3️⃣ استعادة index.html الأصلي (مع كل المنتجات)...")
    # نستخدم أول كوميت كان فيه الملف كامل
    success, _, err = run_command("git show origin/main:index.html > index_backup.html")
    
    if not success:
        print(f"   ❌ فشل في استعادة الملف: {err}")
        print("   💡 جرب يدوياً: git log --all --full-history -- index.html")
        sys.exit(1)
    
    print("   ✅ تم استعادة النسخة الاحتياطية\n")
    
    # 4. قراءة الملف وإضافة الشات بوت
    print("4️⃣ إضافة الشات بوت للملف...")
    try:
        with open('index_backup.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # التحقق من وجود رابط CSS
        if '<link rel="stylesheet" href="/chatbot.css">' not in content:
            # إضافة في head
            content = content.replace(
                '</head>',
                '<link rel="stylesheet" href="/chatbot.css">\n</head>'
            )
            print("   ✅ تم إضافة رابط chatbot.css")
        
        # التحقق من وجود كود HTML الشات بوت
        chatbot_html = '''<!-- Chatbot Container -->
<div id="chatbot-container">
    <button id="chatbot-toggle" aria-expanded="false" aria-controls="chatbot-window">
        <span>💬</span>
        <span>مساعد نينجا</span>
    </button>

    <div id="chatbot-window" class="hidden">
        <div id="chatbot-header">
            <h3>🤖 مساعد نينجا الذكي</h3>
            <button id="chatbot-close" aria-label="إغلاق">✕</button>
        </div>

        <div id="chatbot-messages">
            <div class="message bot-message">
                مرحباً! 👋 أنا مساعد نينجا الذكي. كيف يمكنني مساعدتك اليوم؟ اسأل عن المنتجات والأسعار والتوصيل! 🛍️
            </div>
        </div>

        <div id="chatbot-input-area">
            <input type="text" id="user-input" placeholder="اكتب سؤالك هنا..." aria-label="إدخال الرسالة">
            <button id="send-button" aria-label="إرسال">📤</button>
        </div>
    </div>
</div>'''
        
        if 'chatbot-container' not in content:
            # إضافة قبل </body>
            content = content.replace('</body>', chatbot_html + '\n\n<script src="/chatbot.js"></script>\n</body>')
            print("   ✅ تم إضافة كود الشات بوت HTML")
        
        # حفظ الملف الجديد
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ تم حفظ index.html المحدث\n")
        
    except Exception as e:
        print(f"   ❌ خطأ في معالجة الملف: {e}")
        sys.exit(1)
    
    # 5. عرض الإحصائيات
    print("📊 الإحصائيات:")
    print(f"   📄 حجم الملف: {os.path.getsize('index.html') / 1024:.2f} KB")
    
    with open('index.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        product_count = sum(1 for line in lines if 'product-card' in line and '<div class="product-card' in line)
    
    print(f"   🛍️ عدد المنتجات: {product_count}")
    print(f"   📝 عدد الأسطر: {len(lines)}")
    
    # 6. رفع على Git
    print("\n5️⃣ رفع التعديلات...")
    response = input("   هل تريد رفع الملف على GitHub؟ (y/n): ")
    
    if response.lower() == 'y':
        run_command("git add index.html")
        run_command('git commit -m "استعادة كل المنتجات + دمج الشات بوت المطور"')
        success, out, err = run_command("git push origin main")
        
        if success:
            print("   ✅ تم الرفع بنجاح!\n")
        else:
            print(f"   ❌ فشل الرفع: {err}\n")
    else:
        print("   ⏭️ تم تخطي الرفع\n")
    
    print("\n" + "="*50)
    print("✨ انتهت العملية بنجاح!")
    print("="*50)
    print("\n📌 الملفات الناتجة:")
    print("   • index.html (محدث مع الشات بوت)")
    print("   • index_backup.html (نسخة احتياطية)")
    print("\n🌐 اختبر الموقع: https://iraq-ninja-store.arabsad.com/")
    print("💬 جرب الشات بوت: اكتب 'فشار' أو 'قطاعة' أو 'A.001147'\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ تم إيقاف السكريبت بواسطة المستخدم")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        sys.exit(1)