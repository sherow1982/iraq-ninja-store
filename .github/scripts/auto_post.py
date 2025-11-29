#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
import tweepy
import requests
from urllib.parse import quote
from pathlib import Path
from io import BytesIO

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

# إنشاء slug للمنتج (بنفس طريقة السايت ماب)
def create_product_slug(title, sku):
    # إزالة بادئة SKU (A. أو a.)
    sku_clean = re.sub(r'^[Aa]\.', '', sku).lower()
    
    # تحويل العنوان إلى slug
    # إزالة الأحرف الخاصة وترك الحروف العربية والشرطات فقط
    title_slug = title.strip()
    # استبدال المسافات بشرطات
    title_slug = re.sub(r'\s+', '-', title_slug)
    # إزالة أي شيء غير عربي أو شرطات
    title_slug = re.sub(r'[^\u0600-\u06FF\-]', '', title_slug)
    # إزالة الشرطات المتكررة
    title_slug = re.sub(r'-+', '-', title_slug)
    # إزالة الشرطات من البداية والنهاية
    title_slug = title_slug.strip('-')
    
    # تركيب الـ slug: اسم-المنتج-sku.html
    return f"{title_slug}-{sku_clean}.html"

# إنشاء هاشتاج من العنوان (مع underscore)
def generate_product_hashtag(title):
    # استخدام العنوان كامل مع underscore
    hashtag = title.strip()
    # استبدال المسافات بـ underscore
    hashtag = re.sub(r'\s+', '_', hashtag)
    # إزالة أي أحرف خاصة وترك العربية والـ underscore فقط
    hashtag = re.sub(r'[^\u0600-\u06FF_a-zA-Z0-9]', '', hashtag)
    # إزالة underscores المتكررة
    hashtag = re.sub(r'_+', '_', hashtag)
    # إزالة underscores من البداية والنهاية
    hashtag = hashtag.strip('_')
    return f'#{hashtag}'

# محافظات العراق
iraq_cities = '#بغداد #البصرة #الموصل #أربيل #كربلاء #النجف #السليمانية #الأنبار #ديالى #ذي_قار #واسط #صلاح_الدين #بابل #كركوك #القادسية #ميسان #المثنى #دهوك'

# إنشاء رابط المنتج
product_slug = create_product_slug(product['title'], product['sku'])
product_url = f"https://iraq-ninja-store.arabsad.com/products/{product_slug}"
product_hashtag = generate_product_hashtag(product['title'])

# نص التغريدة
tweet_text = f"""{product['title']}

{product_hashtag} #العراق {iraq_cities}

{product_url}"""

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
    
    # تحميل صورة المنتج
    print("\n📥 تحميل صورة المنتج...")
    image_response = requests.get(product['image_link'])
    if image_response.status_code != 200:
        print(f"⚠️  فشل تحميل الصورة: {image_response.status_code}")
        media_id = None
    else:
        # رفع الصورة باستخدام API v1.1 (media endpoint متاح في Free tier)
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret,
            access_token, access_secret
        )
        api_v1 = tweepy.API(auth)
        
        # رفع الصورة
        media = api_v1.media_upload(
            filename='product.jpg',
            file=BytesIO(image_response.content)
        )
        media_id = media.media_id_string
        print(f"✅ تم رفع الصورة: {media_id}")
    
    # استخدام Twitter API v2 (متوافق مع Free tier)
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )
    
    # نشر التغريدة مع الصورة
    if media_id:
        response = client.create_tweet(text=tweet_text, media_ids=[media_id])
    else:
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
    import traceback
    traceback.print_exc()
    exit(1)
