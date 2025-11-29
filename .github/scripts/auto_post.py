#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter Auto-Posting Script for Iraq Ninja Store
Posts products every 7 hours with images and hashtags
"""

import os
import json
import re
import sys
import tweepy
import requests
from io import BytesIO


def load_products():
    """Load products from JSON file"""
    with open('products.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def load_tracking():
    """Load or create tracking file"""
    tracking_file = 'posted_products.json'
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r', encoding='utf-8') as f:
            return json.load(f), tracking_file
    return {'last_index': -1}, tracking_file


def save_tracking(tracking, tracking_file):
    """Save tracking data"""
    with open(tracking_file, 'w', encoding='utf-8') as f:
        json.dump(tracking, f, ensure_ascii=False, indent=2)


def create_product_slug(title, sku):
    """
    Create product URL slug matching sitemap pattern
    Example: "الشورت-الحراري-002102.html"
    """
    # Remove SKU prefix (A. or a.)
    sku_clean = re.sub(r'^[Aa]\.', '', sku).lower()
    
    # Convert title to slug
    title_slug = title.strip()
    title_slug = re.sub(r'\s+', '-', title_slug)  # Spaces to hyphens
    title_slug = re.sub(r'[^\u0600-\u06FF\-]', '', title_slug)  # Keep Arabic and hyphens only
    title_slug = re.sub(r'-+', '-', title_slug)  # Remove duplicate hyphens
    title_slug = title_slug.strip('-')  # Remove leading/trailing hyphens
    
    return f"{title_slug}-{sku_clean}.html"


def create_product_hashtag(title):
    """
    Create hashtag from product title with underscores
    Example: #جهاز_اعداد_الفشار
    """
    hashtag = title.strip()
    hashtag = re.sub(r'\s+', '_', hashtag)  # Spaces to underscores
    hashtag = re.sub(r'[^\u0600-\u06FF_a-zA-Z0-9]', '', hashtag)  # Keep Arabic, letters, numbers, underscores
    hashtag = re.sub(r'_+', '_', hashtag)  # Remove duplicate underscores
    hashtag = hashtag.strip('_')  # Remove leading/trailing underscores
    return f'#{hashtag}'


def upload_image(api, image_url):
    """
    Download and upload product image to Twitter
    Returns media_id or None
    """
    try:
        print(f"  📥 تحميل الصورة...")
        response = requests.get(image_url, timeout=10)
        
        if response.status_code != 200:
            print(f"  ⚠️  فشل تحميل الصورة: {response.status_code}")
            return None
        
        print(f"  📤 رفع الصورة إلى Twitter...")
        media = api.media_upload(
            filename='product.jpg',
            file=BytesIO(response.content)
        )
        print(f"  ✅ تم رفع الصورة: {media.media_id_string}")
        return media.media_id_string
        
    except Exception as e:
        print(f"  ⚠️  خطأ في رفع الصورة: {e}")
        return None


def main():
    print("🚀 ===========================================")
    print("🚀 Twitter Auto-Posting Script")
    print("🚀 ===========================================")
    
    # Load data
    products = load_products()
    tracking, tracking_file = load_tracking()
    
    # Get next product
    tracking['last_index'] = (tracking['last_index'] + 1) % len(products)
    product = products[tracking['last_index']]
    
    print(f"\n📦 المنتج: {product['title']}")
    print(f"🔢 رقم: {tracking['last_index'] + 1}/{len(products)}")
    
    # Save tracking
    save_tracking(tracking, tracking_file)
    
    # Create product URL and hashtag
    product_slug = create_product_slug(product['title'], product['sku'])
    product_url = f"https://iraq-ninja-store.arabsad.com/products/{product_slug}"
    product_hashtag = create_product_hashtag(product['title'])
    
    # Iraqi cities hashtags
    iraq_cities = '#بغداد #البصرة #الموصل #أربيل #كربلاء #النجف #السليمانية #الأنبار #ديالى #ذي_قار #واسط #صلاح_الدين #بابل #كركوك #القادسية #ميسان #المثنى #دهوك'
    
    # Create tweet text
    tweet_text = f"""{product['title']}

{product_hashtag} #العراق {iraq_cities}

{product_url}"""
    
    print(f"\n🔗 الرابط: {product_url}")
    print(f"📊 طول التغريدة: {len(tweet_text)} حرف")
    
    # Check for required credentials
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_secret = os.getenv('TWITTER_ACCESS_SECRET')
    
    if not all([api_key, api_secret, access_token, access_secret]):
        print("\n❌ خطأ: مفاتيح Twitter غير موجودة!")
        print("⚠️  تأكد من إضافة GitHub Secrets:")
        print("  - TWITTER_API_KEY")
        print("  - TWITTER_API_SECRET")
        print("  - TWITTER_ACCESS_TOKEN")
        print("  - TWITTER_ACCESS_SECRET")
        sys.exit(1)
    
    try:
        print("\n🔐 الاتصال بـ Twitter...")
        
        # Create authentication for v1.1 (for media upload)
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret,
            access_token, access_secret
        )
        api_v1 = tweepy.API(auth)
        
        # Upload image
        media_id = upload_image(api_v1, product['image_link'])
        
        # Create Twitter API v2 client
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
        
        # Post tweet
        print("\n📤 نشر التغريدة...")
        if media_id:
            response = client.create_tweet(text=tweet_text, media_ids=[media_id])
        else:
            response = client.create_tweet(text=tweet_text)
        
        tweet_id = response.data['id']
        tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
        
        print("\n" + "="*50)
        print("✅ تم نشر التغريدة بنجاح!")
        print(f"🔗 {tweet_url}")
        print("="*50)
        
    except tweepy.TweepyException as e:
        error_msg = str(e)
        print(f"\n❌ خطأ في Twitter API:")
        print(f"   {error_msg}")
        
        if "403" in error_msg or "Forbidden" in error_msg:
            print("\n⚠️  خطأ 403 Forbidden")
            print("\n💡 الأسباب المحتملة:")
            print("  1. Free tier لا يدعم نشر التغريدات")
            print("  2. تحتاج Elevated Access أو Basic plan")
            print("  3. صلاحيات التطبيق غير صحيحة")
            print("\n🔧 الحلول:")
            print("  • اطلب Elevated Access (مجاني):")
            print("    https://developer.x.com/en/portal/products/elevated")
            print("  • تأكد أن App permissions = 'Read and Write'")
            print("  • أعد توليد Access Token بعد تغيير الصلاحيات")
        
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
