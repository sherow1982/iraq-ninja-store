#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import json
import requests
from datetime import datetime
from urllib.parse import quote
import tweepy

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_KEY_SECRET") or os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET") or os.getenv("TWITTER_ACCESS_SECRET")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    print("✗ خطأ: مفاتيح Twitter API غير موجودة")
    raise SystemExit(1)

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api_v1 = tweepy.API(auth)
client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)

BASE_URL = "https://iraq-ninja-store.arabsad.com"
SITEMAP_URL = f"{BASE_URL}/sitemap.xml"
PRODUCTS_JSON_PATH = "products.json"
TRACKING_FILE = "posted_products.json"
MAX_POSTS_PER_MONTH = 95

IRAQ_GOVS = ["بغداد", "البصرة", "الموصل", "أربيل", "كركوك", "النجف", "كربلاء", "السليمانية", "الأنبار", "ديالى", "دهوك", "بابل", "ذي_قار", "واسط", "ميسان", "المثنى", "القادسية", "صلاح_الدين"]

def load_products():
    with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    products = data if isinstance(data, list) else data
    print(f"✓ تم تحميل {len(products)} منتج")
    return products

def fetch_sitemap_links():
    try:
        resp = requests.get(SITEMAP_URL, timeout=20)
        if resp.status_code != 200:
            return {}
        links = {}
        for line in resp.text.splitlines():
            line = line.strip()
            if line.startswith("<loc>") and line.endswith("</loc>"):
                url = line.replace("<loc>", "").replace("</loc>", "").strip()
                if "/products/" in url and url.endswith(".html"):
                    slug = url.split("/products/")[-1].replace(".html", "")
                    links[slug] = url
        print(f"✓ تم سحب روابط المنتجات ({len(links)}) من السايت ماب")
        return links
    except Exception:
        return {}

def normalize_slug(name):
    slug = name.strip()
    for ch in ["(", ")", "[", "]", "{", "}", "/", "\\", "|", ",", "،", ".", "!", "؟", ":", ";", "'", '"']:
        slug = slug.replace(ch, "")
    return slug.replace(" ", "-")

def make_product_key(product):
    pid = product.get("id") or product.get("handle") or product.get("slug")
    if pid:
        return str(pid)
    name = product.get("name") or product.get("title") or ""
    return normalize_slug(name)

def extract_image_url(product):
    if product.get("image"):
        return product["image"]
    if product.get("image_url"):
        return product["image_url"]
    if product.get("featured_image"):
        return product["featured_image"]
    if isinstance(product.get("images"), list) and product["images"]:
        first = product["images"][0]
        if isinstance(first, dict):
            return first.get("src") or first.get("url") or ""
        return first if isinstance(first, str) else ""
    if isinstance(product.get("variants"), list) and product["variants"]:
        v0 = product["variants"][0]
        if isinstance(v0, dict):
            return v0.get("image") or v0.get("image_url") or ""
    return ""

def load_tracking():
    current_month = datetime.now().strftime("%Y-%m")
    if not os.path.exists(TRACKING_FILE):
        return {"posted_products": [], "current_month": current_month, "posts_this_month": 0, "cycle_count": 0}
    try:
        with open(TRACKING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    tracking = {
        "posted_products": data.get("posted_products", []),
        "current_month": data.get("current_month", current_month),
        "posts_this_month": data.get("posts_this_month", 0),
        "cycle_count": data.get("cycle_count", 0)
    }
    if tracking["current_month"] != current_month:
        print("📅 شهر جديد! إعادة تعيين العداد.")
        tracking["current_month"] = current_month
        tracking["posts_this_month"] = 0
    return tracking

def save_tracking(tracking):
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(tracking, f, ensure_ascii=False, indent=2)

def choose_product_for_post(products, sitemap_links, tracking):
    posted_set = set(tracking["posted_products"])
    unposted = [p for p in products if make_product_key(p) not in posted_set]
    if not unposted:
        tracking["cycle_count"] += 1
        tracking["posted_products"] = []
        unposted = products
        print(f"🔄 تم إنهاء دورة نشر كاملة، بدء دورة جديدة. (الدورة رقم: {tracking['cycle_count']})")
    product = random.choice(unposted)
    key = make_product_key(product)
    name = product.get("name") or product.get("title") or "منتج بدون اسم"
    price = product.get("price") or product.get("sale_price") or ""
    old_price = product.get("old_price") or product.get("compare_at_price") or ""
    image_url = extract_image_url(product)
    slug_guess = normalize_slug(name)
    encoded_slug = quote(slug_guess, safe="-")
    product_url = sitemap_links.get(slug_guess) or sitemap_links.get(encoded_slug) or f"{BASE_URL}/products/{encoded_slug}.html"
    tracking["posted_products"].append(key)
    return {"name": name, "price": price, "old_price": old_price, "image_url": image_url, "product_url": product_url, "product_key": key}

def calc_discount(price, old_price):
    try:
        p = float(str(price).replace(",", "").replace(" ", ""))
        op = float(str(old_price).replace(",", "").replace(" ", ""))
        if op > p > 0:
            return round((op - p) / op * 100)
    except Exception:
        pass
    return None

def shorten_url_disabled(url):
    try:
        res = requests.get(f"http://tinyurl.com/api-create.php?url={url}", timeout=10)
        if res.status_code == 200 and res.text.startswith("http"):
            print(f"✓ تم اختصار الرابط: {res.text.strip()}")
            return res.text.strip()
    except Exception:
        pass
    return url

def make_hashtag_from_name(name):
    cleaned = "".join([ch for ch in name if "\u0600" <= ch <= "\u06FF" or ch == " "]).strip()
    if not cleaned:
        return None
    words = cleaned.split()[:3]
    hashtag = "_".join(words).replace("__", "_").strip("_")
    return f"#{hashtag}" if hashtag else None

def build_hashtags(product_name):
    tags = []
    name_tag = make_hashtag_from_name(product_name)
    if name_tag:
        tags.append(name_tag)
    for t in ["العراق", "تسوق_اونلاين", "عروض", "تخفيضات"]:
        tags.append(f"#{t}")
    for g in random.sample(IRAQ_GOVS, k=5):
        tags.append(f"#{g.replace(' ', '_')}")
    return tags

def format_price(val):
    if not val:
        return ""
    try:
        return f"{float(str(val)):,.0f}"
    except Exception:
        return str(val)

def download_image(image_url):
    if not image_url:
        print("⚠ لا يوجد رابط صورة")
        return None
    try:
        print(f"⏳ جاري تحميل الصورة من: {image_url}")
        resp = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        if resp.status_code != 200:
            return None
        print(f"✓ تم تحميل الصورة ({len(resp.content)} بايت)")
        with open("product_image.jpg", "wb") as f:
            f.write(resp.content)
        return "product_image.jpg"
    except Exception:
        return None

def upload_media_to_twitter(image_path):
    try:
        print(f"⏳ جاري رفع الصورة إلى تويتر")
        media = api_v1.media_upload(image_path)
        print(f"✓ تم رفع صورة المنتج (Media ID: {media.media_id})")
        return str(media.media_id)
    except Exception:
        return None

def build_tweet_text(product):
    lines = [f"🛒 {product['name']}"]
    price = format_price(product["price"])
    old_price = format_price(product["old_price"])
    discount = calc_discount(product["price"], product["old_price"]) if price and old_price else None
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
    lines.append(f"🔗 {product['product_url']}")
    lines.append(f"📱 واتساب: https://wa.me/201110760081")
    lines.append("")
    base_text = "\n".join(lines)
    tags_text = " ".join(build_hashtags(product["name"]))
    full_text = base_text + "\n" + tags_text
    if len(full_text) > 280:
        full_text = full_text[:279]
    print("--------------------------------------------------")
    print("التغريدة:")
    print("--------------------------------------------------")
    print(full_text)
    print("--------------------------------------------------")
    return full_text

def post_tweet_with_image(text, media_id=None):
    try:
        if media_id:
            print("⏳ جاري نشر التغريدة مع الصورة...")
            response = client.create_tweet(text=text, media_ids=[media_id])
        else:
            print("⏳ جاري نشر التغريدة بدون صورة...")
            response = client.create_tweet(text=text)
        print("✓ تم نشر التغريدة بنجاح!")
        print(f"Tweet ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"✗ خطأ أثناء نشر التغريدة: {e}")
        return False

def main():
    print("=" * 50)
    print("Twitter Auto-Post Bot - Iraq Ninja Store")
    print(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    tracking = load_tracking()
    print(f"\n📊 إحصائيات الشهر الحالي ({tracking['current_month']}):")
    print(f"  - المنشورات هذا الشهر: {tracking['posts_this_month']}/{MAX_POSTS_PER_MONTH}")
    print(f"  - المنتجات المنشورة في هذه الدورة: {len(tracking['posted_products'])}")
    print(f"  - رقم الدورة: {tracking['cycle_count']}\n")
    if tracking["posts_this_month"] >= MAX_POSTS_PER_MONTH:
        print(f"⚠ تم الوصول للحد الأقصى ({MAX_POSTS_PER_MONTH} منشور/شهر)")
        print("⏸ لن يتم النشر حتى بداية الشهر القادم")
        save_tracking(tracking)
        return
    products = load_products()
    sitemap_links = fetch_sitemap_links()
    product = choose_product_for_post(products, sitemap_links, tracking)
    print("📦 المنتج المختار:")
    print(f"  الاسم: {product['name']}")
    print(f"  السعر: {product['price']}")
    print(f"  رابط الصورة: {product['image_url']}\n")
    image_path = download_image(product["image_url"])
    media_id = upload_media_to_twitter(image_path) if image_path else None
    tweet_text = build_tweet_text(product)
    success = post_tweet_with_image(tweet_text, media_id)
    if success:
        tracking["posts_this_month"] += 1
        save_tracking(tracking)
        print("=" * 50)
        print("✓ العملية اكتملت بنجاح")
        print(f"📊 المنشورات المتبقية: {MAX_POSTS_PER_MONTH - tracking['posts_this_month']}")
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
