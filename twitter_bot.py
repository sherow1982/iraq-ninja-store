#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter Auto-Post Bot for Iraq Ninja Store
Automatically tweets random products from products.json
"""

import json
import random
import requests
import os
from datetime import datetime

# Twitter API v2 Configuration
API_KEY = os.getenv('TWITTER_API_KEY', '')  # من المتغيرات البيئية
API_KEY_SECRET = os.getenv('TWITTER_API_KEY_SECRET', '')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')

# Twitter API v2 endpoint
TWITTER_API_URL = "https://api.twitter.com/2/tweets"

def load_products(file_path='products.json'):
    """تحميل المنتجات من ملف JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        print(f"✓ تم تحميل {len(products)} منتج")
        return products
    except Exception as e:
        print(f"✗ خطأ في تحميل المنتجات: {e}")
        return []

def select_random_product(products):
    """اختيار منتج عشوائي"""
    if not products:
        return None
    product = random.choice(products)
    print(f"✓ تم اختيار: {product['title']}")
    return product

def format_tweet(product):
    """تنسيق التغريدة من بيانات المنتج"""
    
    # حساب نسبة الخصم
    if product.get('price') and product.get('sale_price'):
        discount = round(((product['price'] - product['sale_price']) / product['price']) * 100)
    else:
        discount = 0
    
    # تنسيق السعر
    price_iqd = f"{int(product.get('sale_price', 0)):,} د.ع"
    original_price_iqd = f"{int(product.get('price', 0)):,} د.ع" if discount > 0 else ""
    
    # بناء التغريدة
    tweet_parts = []
    
    # العنوان
    tweet_parts.append(f"🛒 {product.get('title', 'منتج مميز')}")
    
    # السعر والخصم
    if discount > 0:
        tweet_parts.append(f"\n💰 السعر: {price_iqd}")
        tweet_parts.append(f"❌ بدلاً من: {original_price_iqd}")
        tweet_parts.append(f"🔥 خصم {discount}%")
    else:
        tweet_parts.append(f"\n💰 السعر: {price_iqd}")
    
    # رابط المنتج
    product_url = f"https://sherow1982.github.io/iraq-ninja-store/#{product.get('id', '')}"
    tweet_parts.append(f"\n\n🔗 {product_url}")
    
    # هاشتاجات
    tweet_parts.append("\n\n#العراق #تسوق_اونلاين #عروض #تخفيضات")
    
    tweet_text = "".join(tweet_parts)
    
    # التأكد من عدم تجاوز حد تويتر (280 حرف)
    if len(tweet_text) > 280:
        # تقليص الوصف إذا كان طويل
        tweet_text = tweet_text[:277] + "..."
    
    return tweet_text

def post_tweet(tweet_text):
    """نشر التغريدة على Twitter باستخدام API v2"""
    
    if not all([API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("✗ خطأ: مفاتيح Twitter API غير موجودة")
        print("قم بتعيين المتغيرات البيئية:")
        print("  TWITTER_API_KEY")
        print("  TWITTER_API_KEY_SECRET")
        print("  TWITTER_ACCESS_TOKEN")
        print("  TWITTER_ACCESS_TOKEN_SECRET")
        return False
    
    try:
        # إنشاء OAuth 1.0a authentication
        from requests_oauthlib import OAuth1
        
        auth = OAuth1(
            API_KEY,
            API_KEY_SECRET,
            ACCESS_TOKEN,
            ACCESS_TOKEN_SECRET
        )
        
        # البيانات المراد نشرها
        payload = {"text": tweet_text}
        
        # إرسال الطلب
        response = requests.post(
            TWITTER_API_URL,
            auth=auth,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            tweet_data = response.json()
            tweet_id = tweet_data.get('data', {}).get('id')
            print(f"✓ تم نشر التغريدة بنجاح!")
            print(f"  ID: {tweet_id}")
            print(f"  الرابط: https://twitter.com/user/status/{tweet_id}")
            return True
        else:
            print(f"✗ فشل النشر. كود الخطأ: {response.status_code}")
            print(f"  التفاصيل: {response.text}")
            return False
            
    except ImportError:
        print("✗ خطأ: المكتبة requests_oauthlib غير مثبتة")
        print("قم بتثبيتها: pip install requests-oauthlib")
        return False
    except Exception as e:
        print(f"✗ خطأ في النشر: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("=" * 50)
    print("Twitter Auto-Post Bot - Iraq Ninja Store")
    print(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # تحميل المنتجات
    products = load_products()
    if not products:
        print("✗ لا توجد منتجات للنشر")
        return
    
    # اختيار منتج عشوائي
    product = select_random_product(products)
    if not product:
        print("✗ فشل اختيار المنتج")
        return
    
    # تنسيق التغريدة
    tweet_text = format_tweet(product)
    print("\n" + "-" * 50)
    print("التغريدة:")
    print("-" * 50)
    print(tweet_text)
    print("-" * 50)
    
    # نشر التغريدة
    success = post_tweet(tweet_text)
    
    if success:
        print("\n✓ تمت العملية بنجاح!")
    else:
        print("\n✗ فشلت العملية")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
