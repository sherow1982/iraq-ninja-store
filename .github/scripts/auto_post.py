#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
import tweepy
import requests
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

# إنشاء slug للمنتج
def create_product_slug(title, sku):
    sku_clean = re.sub(r'^[Aa]\.', '', sku).lower()
    title_slug = title.strip()
    title_slug = re.sub(r'\s+', '-', title_slug)
    title_slug = re.sub(r'[^\u0600-\u06FF\-]', '', title_slug)
    title_slug = re.sub(r'-+', '-', title_slug)
    title_slug = title_slug.strip('-')
    return f"{title_slug}-{sku_clean}.html"

# إنشاء هاشتاج من العنوان
def generate_product_hashtag(title):
    hashtag = title.strip()
    hashtag = re.sub(r'\s+', '_', hashtag)
    hashtag = re.sub(r'[^\u0600-\u06FF_a-zA-Z0-9]', '', hashtag)
    hashtag = re.sub(r'_+', '_', hashtag)
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
print(f"📊 طول التغريدة: {len(tweet_text)} حرف")

# التحقق من وجود المفاتيح
api_key = os.getenv('TWITTER_API_KEY')
api_secret = os.getenv('TWITTER_API_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_secret = os.getenv('TWITTER_ACCESS_SECRET')

if not all([api_key, api_secret, access_token, access_secret]):
    print("❌ خطأ: مفاتيح Twitter غير موجودة!")
    exit(1)

try:
    # رفع الصورة باستخدام API v1.1
    print("\n📥 تحميل ورفع الصورة...")
    auth = tweepy.OAuth1UserHandler(
        api_key, api_secret,
        access_token, access_secret
    )
    api_v1 = tweepy.API(auth)
    
    # تحميل الصورة
    image_response = requests.get(product['image_link'])
    media_id = None
    
    if image_response.status_code == 200:
        media = api_v1.media_upload(
            filename='product.jpg',
            file=BytesIO(image_response.content)
        )
        media_id = media.media_id_string
        print(f"✅ تم رفع الصورة")
    
    # نشر التغريدة باستخدام API v2
    print("📤 نشر التغريدة...")
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )
    
    if media_id:
        response = client.create_tweet(text=tweet_text, media_ids=[media_id])
    else:
        response = client.create_tweet(text=tweet_text)
    
    print(f"\n✅ تم نشر التغريدة بنجاح!")
    print(f"🔗 https://twitter.com/i/web/status/{response.data['id']}")
    
except Exception as e:
    print(f"\n❌ خطأ: {str(e)}")
    exit(1)
