#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter Auto-Post Bot for Iraq Ninja Store
Tweets random product with image, shortened URL, and comprehensive hashtags
"""
import json
import random
import requests
import os
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote, quote
import tempfile
import re

# Twitter API v2 Configuration
API_KEY = os.getenv('TWITTER_API_KEY', '')
API_KEY_SECRET = os.getenv('TWITTER_API_KEY_SECRET', '')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
TWITTER_API_URL = "https://api.twitter.com/2/tweets"
TWITTER_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"

SITEMAP_URL = 'https://iraq-ninja-store.arabsad.com/sitemap.xml'
SITE_BASE = 'https://iraq-ninja-store.arabsad.com/products/'

# هاشتاجات محافظات العراق
IRAQ_PROVINCES = [
    '#بغداد', '#البصرة', '#الموصل', '#أربيل', '#كركوك', '#النجف',
    '#كربلاء', '#السليمانية', '#الأنبار', '#ديالى', '#دهوك',
    '#بابل', '#ذي_قار', '#واسط', '#ميسان', '#المثنى', '#القادسية', '#صلاح_الدين'
]


def load_products(file_path='products.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        print(f"✓ تم تحميل {len(products)} منتج")
        return products
    except Exception as e:
        print(f"✗ خطأ في تحميل المنتجات: {e}")
        return []


def select_random_product(products):
    if not products:
        return None
    return random.choice(products)


def fetch_url_map():
    url_map = {}
    try:
        resp = requests.get(SITEMAP_URL, timeout=15)
        resp.raise_for_status()
        tree = ET.fromstring(resp.text)
        ns = {'n': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for url in tree.findall('n:url', ns):
            loc = url.find('n:loc', ns)
            if loc is not None and loc.text and loc.text.startswith(SITE_BASE):
                parsed = urlparse(loc.text)
                path = unquote(parsed.path)
                if path.endswith('.html'):
                    slug = path.split('/products/')[-1].replace('.html', '').replace('-', ' ')
                    slug = slug.replace('ـ','').strip()
                    url_map[slug] = loc.text
        print(f"✓ تم سحب روابط المنتجات ({len(url_map)}) من السايت ماب")
    except Exception as e:
        print(f"✗ خطأ قراءة sitemap من الموقع: {e}")
    return url_map


def find_product_url(product, url_map):
    product_title = product.get('title', '').replace('-', ' ').replace('ـ','').replace('%20',' ').strip()
    for k in url_map.keys():
        if product_title == k:
            return url_map[k]
    for k in url_map.keys():
        if product_title in k or k in product_title:
            return url_map[k]
    return ''


def shorten_url(long_url):
    """اختصار الرابط باستخدام TinyURL"""
    try:
        api_url = f"http://tinyurl.com/api-create.php?url={quote(long_url)}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200 and response.text.startswith('http'):
            short_url = response.text.strip()
            print(f"✓ تم اختصار الرابط: {short_url}")
            return short_url
        else:
            print("⚠ فشل اختصار الرابط، استخدام الرابط الأصلي")
            return long_url
    except Exception as e:
        print(f"⚠ خطأ في اختصار الرابط: {e}")
        return long_url


def create_product_hashtag(product_title):
    """إنشاء هاشتاج من اسم المنتج"""
    # إزالة الرموز الخاصة والأرقام والحروف الإنجليزية
    clean_title = re.sub(r'[a-zA-Z0-9\-_.،؛!؟()\[\]{}"\']', '', product_title)
    # تحويل المسافات إلى underscore
    hashtag = clean_title.strip().replace(' ', '_')
    # تحديد بحد أقصى 3 كلمات
    words = hashtag.split('_')[:3]
    hashtag = '_'.join(words)
    return f"#{hashtag}" if hashtag else ""


def upload_image(image_url, auth):
    """تحميل صورة المنتج على Twitter باستخدام API v1.1"""
    try:
        print(f"⏳ جاري تحميل الصورة من: {image_url}")
        
        # تحميل الصورة
        headers = {'User-Agent': 'Mozilla/5.0'}
        img_resp = requests.get(image_url, timeout=15, headers=headers)
        img_resp.raise_for_status()
        
        print(f"✓ تم تحميل الصورة ({len(img_resp.content)} بايت)")
        
        # رفع مباشر على Twitter
        files = {'media': ('product.jpg', img_resp.content, 'image/jpeg')}
        upload_resp = requests.post(TWITTER_UPLOAD_URL, auth=auth, files=files)
        
        if upload_resp.status_code == 200:
            media_id = upload_resp.json().get('media_id_string')
            print(f"✓ تم رفع صورة المنتج بنجاح (Media ID: {media_id})")
            return media_id
        else:
            print(f"✗ فشل رفع الصورة: {upload_resp.status_code}")
            print(f"  التفاصيل: {upload_resp.text}")
            return None
    except Exception as e:
        print(f"✗ خطأ في رفع الصورة: {e}")
        import traceback
        traceback.print_exc()
        return None


def format_tweet(product, url_map):
    if product.get('price') and product.get('sale_price'):
        discount = round(((product['price'] - product['sale_price']) / product['price']) * 100)
    else:
        discount = 0
    
    price_iqd = f"{int(product.get('sale_price', 0)):,} د.ع"
    original_price_iqd = f"{int(product.get('price', 0)):,} د.ع" if discount > 0 else ""
    
    tweet_parts = []
    tweet_parts.append(f"🛒 {product.get('title', 'منتج مميز')}")
    
    if discount > 0:
        tweet_parts.append(f"\n💰 السعر: {price_iqd} ❌ بدلاً من: {original_price_iqd} 🔥 خصم {discount}%")
    else:
        tweet_parts.append(f"\n💰 السعر: {price_iqd}")
    
    # اختصار الرابط
    long_url = find_product_url(product, url_map)
    if long_url:
        short_url = shorten_url(long_url)
        tweet_parts.append(f"\n\n🔗 {short_url}")
    
    # إضافة هاشتاج اسم المنتج
    product_hashtag = create_product_hashtag(product.get('title', ''))
    
    # هاشتاجات عامة
    general_tags = ['#العراق', '#تسوق_اونلاين', '#عروض', '#تخفيضات']
    
    # اختيار عشوائي من 5-7 محافظات
    num_provinces = random.randint(5, 7)
    selected_provinces = random.sample(IRAQ_PROVINCES, num_provinces)
    
    # دمج الهاشتاجات
    all_hashtags = []
    if product_hashtag:
        all_hashtags.append(product_hashtag)
    all_hashtags.extend(general_tags)
    all_hashtags.extend(selected_provinces)
    
    tweet_parts.append(f"\n\n{' '.join(all_hashtags)}")
    
    tweet_text = "".join(tweet_parts)
    
    # التحقق من طول التغريدة
    if len(tweet_text) > 280:
        # تقليل عدد المحافظات
        selected_provinces = random.sample(IRAQ_PROVINCES, 3)
        all_hashtags = []
        if product_hashtag:
            all_hashtags.append(product_hashtag)
        all_hashtags.extend(general_tags)
        all_hashtags.extend(selected_provinces)
        
        tweet_parts[-1] = f"\n\n{' '.join(all_hashtags)}"
        tweet_text = "".join(tweet_parts)
        
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."
    
    return tweet_text


def post_tweet(tweet_text, product):
    if not all([API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("✗ خطأ: مفاتيح Twitter API غير موجودة")
        return False
    
    try:
        from requests_oauthlib import OAuth1
        auth = OAuth1(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        
        # رفع صورة المنتج
        media_id = None
        if product.get('image'):
            media_id = upload_image(product['image'], auth)
        else:
            print("⚠ لا توجد صورة للمنتج")
        
        # إنشاء التغريدة
        payload = {"text": tweet_text}
        if media_id:
            payload["media"] = {"media_ids": [media_id]}
        
        print("⏳ جاري نشر التغريدة...")
        response = requests.post(TWITTER_API_URL, auth=auth, json=payload, headers={"Content-Type": "application/json"})
        
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
        print("✗ خطأ: requests_oauthlib غير مثبتة")
        return False
    except Exception as e:
        print(f"✗ خطأ في النشر: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 50)
    print("Twitter Auto-Post Bot - Iraq Ninja Store")
    print(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    products = load_products()
    if not products:
        print("✗ لا توجد منتجات للنشر")
        return
    
    url_map = fetch_url_map()
    if not url_map:
        print("✗ لم يتم جلب روابط المنتجات")
        return
    
    product = select_random_product(products)
    if not product:
        print("✗ فشل اختيار المنتج")
        return
    
    print(f"\n📦 المنتج المختار: {product.get('title')}")
    if product.get('image'):
        print(f"🖼  رابط الصورة: {product.get('image')}")
    else:
        print("⚠  تحذير: المنتج لا يحتوي على صورة")
    
    tweet_text = format_tweet(product, url_map)
    
    print("\n" + "-" * 50)
    print("التغريدة:")
    print("-" * 50)
    print(tweet_text)
    print("-" * 50)
    print(f"الطول: {len(tweet_text)} حرف")
    
    success = post_tweet(tweet_text, product)
    
    if success:
        print("\n✓ تمت العملية بنجاح!")
    else:
        print("\n✗ فشلت العملية")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
