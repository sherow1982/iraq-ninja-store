#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter Auto-Post Bot for Iraq Ninja Store
Posts random products with images using tweepy
"""
import os
import random
import json
import requests
from datetime import datetime
from urllib.parse import quote
import tweepy

# ==============================
# إعداد مفاتيح تويتر من المتغيرات البيئية
# ==============================

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_KEY_SECRET") or os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET") or os.getenv("TWITTER_ACCESS_SECRET")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    print("✗ خطأ: مفاتيح Twitter API غير موجودة")
    print("قم بتعيين المتغيرات البيئية:")
    print("  TWITTER_API_KEY")
    print("  TWITTER_API_KEY_SECRET")
    print("  TWITTER_ACCESS_TOKEN")
    print("  TWITTER_ACCESS_TOKEN_SECRET")
    raise SystemExit(1)

# ==============================
# إعداد عميل تويتر (tweepy)
# ==============================

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api_v1 = tweepy.API(auth)

# ==============================
# إعدادات عامة
# ==============================

BASE_URL = "https://iraq-ninja-store.arabsad.com"
SITEMAP_URL = f"{BASE_URL}/sitemap.xml"
PRODUCTS_JSON_PATH = "products.json"

# المحافظات
IRAQ_GOVS = [
    "بغداد", "البصرة", "الموصل", "أربيل", "كركوك", "النجف",
    "كربلاء", "السليمانية", "الأنبار", "ديالى", "دهوك",
    "بابل", "ذي_قار", "واسط", "ميسان", "المثنى", "القادسية", "صلاح_الدين"
]

def load_products():
    if not os.path.exists(PRODUCTS_JSON_PATH):
        print(f"✗ ملف المنتجات غير موجود: {PRODUCTS_JSON_PATH}")
        raise SystemExit(1)

    with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        products = data
    else:
        products = data

    print(f"✓ تم تحميل {len(products)} منتج")
    return products

def fetch_sitemap_links():
    print(f"⏳ جاري تحميل السايت ماب من: {SITEMAP_URL}")
    try:
        resp = requests.get(SITEMAP_URL, timeout=20)
        if resp.status_code != 200:
            print(f"✗ فشل تحميل السايت ماب. كود: {resp.status_code}")
            return {}

        text = resp.text
        links = {}

        for line in text.splitlines():
            line = line.strip()
            if line.startswith("<loc>") and line.endswith("</loc>"):
                url = line.replace("<loc>", "").replace("</loc>", "").strip()
                if "/products/" in url and url.endswith(".html"):
                    slug = url.split("/products/")[-1].replace(".html", "")
                    links[slug] = url

        print(f"✓ تم سحب روابط المنتجات ({len(links)}) من السايت ماب")
        return links
    except Exception as e:
        print(f"✗ خطأ في تحميل السايت ماب: {e}")
        return {}

def normalize_slug(name):
    slug = name.strip()
    for ch in ["(", ")", "[", "]", "{", "}", "/", "\\", "|", ",", "،", ".", "!", "؟", ":", ";", "'", '"']:
        slug = slug.replace(ch, "")
    slug = slug.replace(" ", "-")
    return slug

def choose_random_product(products, sitemap_links):
    product = random.choice(products)

    name = product.get("name") or product.get("title") or "منتج بدون اسم"
    price = product.get("price") or product.get("sale_price") or ""
    old_price = product.get("old_price") or product.get("compare_at_price") or ""
    image_url = product.get("image") or product.get("image_url") or ""

    slug_guess = normalize_slug(name)
    encoded_slug = quote(slug_guess, safe="-")

    product_url = None
    if slug_guess in sitemap_links:
        product_url = sitemap_links[slug_guess]
    elif encoded_slug in sitemap_links:
        product_url = sitemap_links[encoded_slug]
    else:
        product_url = f"{BASE_URL}/products/{encoded_slug}.html"

    return {
        "name": name,
        "price": price,
        "old_price": old_price,
        "image_url": image_url,
        "product_url": product_url
    }

def calc_discount(price, old_price):
    try:
        p = float(str(price).replace(",", "").replace(" ", ""))
        op = float(str(old_price).replace(",", "").replace(" ", ""))
        if op > p > 0:
            disc = round((op - p) / op * 100)
            if disc > 0:
                return disc
    except Exception:
        return None
    return None

def shorten_url(url):
    try:
        res = requests.get(f"http://tinyurl.com/api-create.php?url={url}", timeout=10)
        if res.status_code == 200:
            short = res.text.strip()
            if short.startswith("http"):
                print(f"✓ تم اختصار الرابط: {short}")
                return short
    except Exception as e:
        print(f"⚠ تعذر اختصار الرابط: {e}")
    return url

def make_hashtag_from_name(name):
    cleaned = ""
    for ch in name:
        if "\u0600" <= ch <= "\u06FF" or ch == " ":
            cleaned += ch

    cleaned = cleaned.strip()
    if not cleaned:
        return None

    words = cleaned.split()[:3]
    hashtag = "_".join(words)
    hashtag = hashtag.replace("__", "_").strip("_")

    if not hashtag:
        return None

    return f"#{hashtag}"

def build_hashtags(product_name):
    base_tags = ["العراق", "تسوق_اونلاين", "عروض", "تخفيضات"]
    govs_sample = random.sample(IRAQ_GOVS, k=min(5, len(IRAQ_GOVS)))

    name_tag = make_hashtag_from_name(product_name)

    tags = []
    if name_tag:
        tags.append(name_tag)

    for t in base_tags:
        tags.append(f"#{t}")

    for g in govs_sample:
        if " " in g:
            g = g.replace(" ", "_")
        if not g.startswith("#"):
            g = f"#{g}"
        tags.append(g)

    return tags

def download_image(image_url, filename="product_image.jpg"):
    if not image_url:
        print("⚠ لا يوجد رابط صورة في بيانات المنتج")
        return None

    try:
        print(f"⏳ جاري تحميل الصورة من: {image_url}")
        headers = {"User-Agent": "Mozilla/5.0 (compatible; TwitterBot/1.0)"}
        response = requests.get(image_url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"✗ فشل تحميل الصورة. كود: {response.status_code}")
            return None

        size = len(response.content)
        print(f"✓ تم تحميل الصورة ({size} بايت)")

        with open(filename, "wb") as f:
            f.write(response.content)

        return filename
    except Exception as e:
        print(f"✗ خطأ أثناء تحميل الصورة: {e}")
        return None

def upload_media_to_twitter(image_path):
    try:
        print(f"⏳ جاري رفع الصورة إلى تويتر: {image_path}")
        media = api_v1.media_upload(image_path)
        print(f"✓ تم رفع صورة المنتج بنجاح (Media ID: {media.media_id})")
        return media.media_id
    except Exception as e:
        print(f"✗ خطأ أثناء رفع الصورة إلى تويتر: {e}")
        import traceback
        traceback.print_exc()
        return None

def build_tweet_text(product):
    name = product["name"]
    price = product["price"]
    old_price = product["old_price"]
    url = product["product_url"]

    discount = None
    if price and old_price:
        discount = calc_discount(price, old_price)

    short_url = shorten_url(url)

    lines = []
    lines.append(f"🛒 {name}")

    price_line = ""
    if price:
        price_line += f"💰 السعر: {price} د.ع"
    if old_price:
        price_line += f" ❌ بدلاً من: {old_price} د.ع"
    if discount:
        price_line += f" 🔥 خصم {discount}%"

    if price_line:
        lines.append(price_line)

    lines.append("")
    lines.append(f"🔗 {short_url}")
    lines.append("")

    hashtags = build_hashtags(name)

    base_text = "\n".join(lines)
    remaining = 280 - len(base_text) - 1

    tags_text = ""
    for tag in hashtags:
        add = f"{tag} "
        if len(tags_text) + len(add) <= remaining:
            tags_text += add
        else:
            break

    full_text = base_text + "\n" + tags_text.strip()
    if len(full_text) > 280:
        full_text = full_text[:279]

    print("--------------------------------------------------")
    print("التغريدة:")
    print("--------------------------------------------------")
    print(full_text)
    print("--------------------------------------------------")
    print(f"الطول: {len(full_text)} حرف")

    return full_text

def post_tweet_with_image(text, media_id=None):
    try:
        if media_id:
            print("⏳ جاري نشر التغريدة مع الصورة...")
            status = api_v1.update_status(status=text, media_ids=[media_id])
        else:
            print("⏳ جاري نشر التغريدة بدون صورة...")
            status = api_v1.update_status(status=text)

        print("✓ تم نشر التغريدة بنجاح!")
        print(f"Tweet ID: {status.id}")
        print(f"الرابط: https://twitter.com/user/status/{status.id}")
        return True
    except Exception as e:
        print(f"✗ خطأ أثناء نشر التغريدة: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("Twitter Auto-Post Bot - Iraq Ninja Store")
    print(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    products = load_products()
    sitemap_links = fetch_sitemap_links()

    product = choose_random_product(products, sitemap_links)

    print("")
    print("📦 المنتج المختار:")
    print(f"  الاسم: {product['name']}")
    print(f"  السعر: {product['price']}")
    print(f"  السعر القديم: {product['old_price']}")
    print(f"  رابط المنتج: {product['product_url']}")
    print(f"  رابط الصورة: {product['image_url']}")
    print("")

    image_path = download_image(product["image_url"])

    media_id = None
    if image_path:
        media_id = upload_media_to_twitter(image_path)
    else:
        print("⚠ لن يتم إرفاق صورة لأن الصورة لم تُحمّل بنجاح.")

    tweet_text = build_tweet_text(product)

    success = post_tweet_with_image(tweet_text, media_id=media_id)

    if success:
        print("=" * 50)
        print("✓ العملية اكتملت بنجاح")
        print("=" * 50)
    else:
        print("=" * 50)
        print("✗ فشلت العملية")
        print("=" * 50)

    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except Exception:
            pass

if __name__ == "__main__":
    main()
