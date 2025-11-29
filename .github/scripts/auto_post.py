#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
import tweepy
from pathlib import Path

# قراءة ملف المنتجات
with open('products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# قراءة ملف التتبع
tracking_file = 'posted_products.json'
if os.path.exists(tracking_file):
    with open(tracking_file, 'r', encoding='utf-8') as f:
        tracking = json.load(f)
else:
    tracking = {'last_index': -1}

# اختيار المنتج التالي
tracking['last_index'] = (tracking['last_index'] + 1) % len(products)
product = products[tracking['last_index']]

print(f"📦 المنتج: {product['title']}")
print(f"🔢 {tracking['last_index'] + 1}/{len(products)}")

# حفظ التتبع
with open(tracking_file, 'w', encoding='utf-8') as f:
    json.dump(tracking, f, ensure_ascii=False, indent=2)

# إنشاء slug للمنتج
def create_product_slug(title, sku):
    # إزالة بادئة SKU
    sku_clean = re.sub(r'^[AG]\.', '', sku, flags=re.IGNORECASE).lower()
    
    # تحويل العنوان إلى slug
    title_slug = title.strip()
    title_slug = re.sub(r'\s+', '-', title_slug)  # مسافات إلى شرطات
    title_slug = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\-]', '', title_slug)
    title_slug = re.sub(r'-+', '-', title_slug)  # شرطات متعددة إلى واحدة
    title_slug = title_slug.strip('-')  # إزالة شرطات في البداية والنهاية
    
    return f"{title_slug}-{sku_clean}.html"

# إنشاء هاشتاجات من العنوان
def generate_hashtags(title):
    words = [w for w in title.split() if len(w) > 3][:3]
    hashtags = []
    for word in words:
        clean_word = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z0-9]', '', word)
        if clean_word:
            hashtags.append(f'#{clean_word}')
    return ' '.join(hashtags)

# محافظات العراق
iraq_cities = '#بغداد #البصرة #الموصل #أربيل #كربلاء #النجف #السليمانية #الأنبار #ديالى #ذي_قار #واسط #صلاح_الدين #بابل #كركوك #القادسية #ميسان #المثنى #دهوك'

# إنشاء رابط المنتج
product_slug = create_product_slug(product['title'], product['sku'])
product_url = f"https://iraq-ninja-store.arabsad.com/products/{product_slug}"
product_hashtags = generate_hashtags(product['title'])

# نص التغريدة
tweet_text = f"""{product['title']}

{product_url}

{product_hashtags} #العراق {iraq_cities}"""

print(f"\n🔗 الرابط: {product_url}")
print(f"\n📤 نص التغريدة:")
print(tweet_text)
print(f"\n📊 طول التغريدة: {len(tweet_text)} حرف")

# الاتصال بـ Twitter API v2
try:
    # التحقق من وجود المفاتيح
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_secret = os.getenv('TWITTER_ACCESS_SECRET')
    
    if not all([api_key, api_secret, access_token, access_secret]):
        print("❌ خطأ: مفاتيح Twitter غير موجودة!")
        print("⚠️  تأكد من إضافة Secrets في GitHub:")
        print("  - TWITTER_API_KEY")
        print("  - TWITTER_API_SECRET")
        print("  - TWITTER_ACCESS_TOKEN")
        print("  - TWITTER_ACCESS_SECRET")
        exit(1)
    
    # استخدام Twitter API v2 (متوافق مع Free tier)
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )
    
    # نشر التغريدة باستخدام API v2
    response = client.create_tweet(text=tweet_text)
    
    print("\n✅ تم نشر التغريدة بنجاح!")
    print(f"🔗 رابط التغريدة: https://twitter.com/i/web/status/{response.data['id']}")
    
except tweepy.TweepyException as e:
    print(f"\n❌ خطأ في Twitter API: {str(e)}")
    
    if "403" in str(e) or "Forbidden" in str(e):
        print("\n⚠️  خطأ 403 - الأسباب المحتملة:")
        print("1. صلاحيات التطبيق خاطئة (يجب أن تكون Read and Write)")
        print("2. لم يتم Elevated Access (لكن API v2 يجب أن يعمل مع Free)")
        print("\n🔧 الحل:")
        print("  1. اذهب إلى: https://developer.x.com/")
        print("  2. اختر التطبيق > Settings > User authentication settings")
        print("  3. تأكد أن App permissions = 'Read and Write'")
        print("  4. اذهب إلى Keys and tokens")
        print("  5. اضغط Regenerate على Access Token and Secret")
        print("  6. انسخ المفاتيح الجديدة وضعها في GitHub Secrets")
    
    exit(1)
    
except Exception as e:
    print(f"\n❌ خطأ غير متوقع: {str(e)}")
    exit(1)
