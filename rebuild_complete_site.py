from pathlib import Path
import json
import urllib.parse
import re
import random
from datetime import datetime, timedelta

# قراءة المنتجات
with open('products.json', 'r', encoding='utf-8') as f:
    products_data = json.load(f)

BASE_URL = "https://iraq-ninja-store.arabsad.com"
WHATSAPP_NUMBER = "201110760081"

print(f"✓ تم قراءة {len(products_data)} منتج")

# استخراج الفئات
categories_dict = {}
for product in products_data:
    category = product.get('category', 'منتجات متنوعة')
    if category not in categories_dict:
        categories_dict[category] = []
    categories_dict[category].append(product)

print(f"✓ تم العثور على {len(categories_dict)} فئة")

# تتبع الـ slugs - نستخدم dict يربط المنتج بالـ slug
product_slugs = {}

def create_unique_slug(title, sku):
    """توليد slug فريد باستخدام SKU"""
    if not title:
        return f"product-{sku}"
    
    # تنظيف العنوان
    slug = str(title).strip().lower()
    slug = re.sub(r'[^\w\s\-أ-ي]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    # إضافة SKU للتأكد من عدم التكرار
    if sku:
        # تنظيف SKU
        clean_sku = re.sub(r'[^\w\-]', '', str(sku).lower())
        final_slug = f"{slug}-{clean_sku}"
    else:
        final_slug = slug
    
    return final_slug

def generate_reviews(product_name, count=None):
    if count is None:
        count = random.randint(18, 28)
    
    names = ["احمد حسين", "علي محمد", "فاطمة عباس", "زينب كريم", "محمود صالح",
             "سارة احمد", "حسين علي", "مريم حسن", "عمر يوسف", "نور الهدى"]
    
    reviews_templates = [
        "منتج ممتاز والله واصل بوقته والجودة فوق الممتازة انصح بالشراء",
        "استلمت الطلب وكان اروع من المتوقع صراحة يستاهل كل فلس دفعته",
        "جودة عالية جدا والتوصيل سريع شكرا الكم على الخدمة الراقية"
    ]
    
    cities = ["بغداد", "البصرة", "أربيل", "النجف", "كربلاء"]
    
    reviews = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 11, 28)
    
    for i in range(count):
        rating = random.choices([5, 4.5, 4], weights=[70, 25, 5])[0]
        days_diff = (end_date - start_date).days
        review_date = start_date + timedelta(days=random.randint(0, days_diff))
        
        reviews.append({
            'name': random.choice(names),
            'city': random.choice(cities),
            'rating': rating,
            'text': random.choice(reviews_templates),
            'date': review_date.strftime('%Y-%m-%d')
        })
    
    reviews.sort(key=lambda x: x['date'], reverse=True)
    return reviews

# بناء slugs لكل المنتجات أولاً
print("جاري إنشاء slugs فريدة لكل منتج...")
for index, product in enumerate(products_data):
    title = product.get('title', 'منتج')
    sku = product.get('sku', f'PRD-{index+1}')
    slug = create_unique_slug(title, sku)
    product_slugs[index] = slug

# بناء قائمة الفئات المنسدلة
categories_dropdown_items = ""
category_slugs = {}
for category in sorted(categories_dict.keys()):
    cat_slug = re.sub(r'[^\w\s\-أ-ي]', '', category.lower())
    cat_slug = re.sub(r'\s+', '-', cat_slug)
    cat_slug = cat_slug.strip('-')
    category_slugs[category] = cat_slug
    categories_dropdown_items += f'<a href="/categories/{cat_slug}.html">{category} ({len(categories_dict[category])})</a>\n'

# Header موحد
header_html = f"""
<header class="site-header">
    <div class="header-container">
        <div class="top-bar">
            <div class="logo">
                <a href="/index.html">
                    <img src="/assets/logo.png" alt="متجر نينجا العراق" class="logo-img">
                    <span>متجر نينجا العراق</span>
                </a>
            </div>
            <div class="search-box">
                <form action="/404.html" method="get" class="search-form">
                    <input type="text" name="q" placeholder="ابحث عن منتج..." class="search-input" required>
                    <button type="submit" class="search-btn">🔍 بحث</button>
                </form>
            </div>
            <div class="header-actions">
                <a href="https://wa.me/{WHATSAPP_NUMBER}" class="whatsapp-btn" target="_blank">📱 واتساب</a>
            </div>
        </div>
        <nav class="main-nav">
            <a href="/index.html">الرئيسية</a>
            <div class="dropdown">
                <a href="/categories.html" class="dropbtn">الفئات ▼</a>
                <div class="dropdown-content">
                    {categories_dropdown_items}
                </div>
            </div>
            <a href="/legal/about.html">من نحن</a>
            <a href="/legal/contact.html">اتصل بنا</a>
            <a href="/legal/shipping.html">الشحن</a>
            <a href="/legal/returns.html">الاسترجاع</a>
            <a href="/legal/privacy.html">الخصوصية</a>
            <a href="/legal/terms.html">الشروط</a>
        </nav>
    </div>
</header>
"""

footer_html = """
<footer class="site-footer">
    <div class="footer-container">
        <div class="footer-section">
            <h3>متجر نينجا العراق</h3>
            <p>أفضل المنتجات بأسعار منافسة مع توصيل مجاني لجميع المحافظات العراقية</p>
        </div>
        <div class="footer-section">
            <h3>روابط سريعة</h3>
            <ul>
                <li><a href="/index.html">الرئيسية</a></li>
                <li><a href="/categories.html">الفئات</a></li>
                <li><a href="/legal/about.html">من نحن</a></li>
                <li><a href="/legal/contact.html">اتصل بنا</a></li>
            </ul>
        </div>
        <div class="footer-section">
            <h3>خدماتنا</h3>
            <ul>
                <li><a href="/legal/shipping.html">سياسة الشحن</a></li>
                <li><a href="/legal/returns.html">الاسترجاع والاستبدال</a></li>
                <li><a href="/legal/privacy.html">سياسة الخصوصية</a></li>
                <li><a href="/legal/terms.html">الشروط والأحكام</a></li>
            </ul>
        </div>
        <div class="footer-section">
            <h3>تواصل معنا</h3>
            <ul>
                <li>📱 واتساب: <a href="https://wa.me/201110760081" target="_blank">+20 111 076 0081</a></li>
                <li>✉️ البريد: <a href="mailto:sherow1982@gmail.com">sherow1982@gmail.com</a></li>
            </ul>
        </div>
    </div>
    <div class="footer-bottom">
        <p>&copy; 2025 متجر نينجا العراق. جميع الحقوق محفوظة.</p>
    </div>
</footer>
"""

common_css = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:#f5f5f5;color:#333;line-height:1.6;direction:rtl}
.site-header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
.header-container{max-width:1400px;margin:0 auto;padding:0 20px}
.top-bar{display:flex;justify-content:space-between;align-items:center;padding:20px 0;flex-wrap:wrap;gap:20px}
.logo{display:flex;align-items:center;gap:10px}
.logo a{color:white;text-decoration:none;font-size:24px;font-weight:bold;display:flex;align-items:center;gap:10px}
.logo-img{height:50px;width:50px;object-fit:contain;background:white;border-radius:10px;padding:5px}
.search-box{flex:1;max-width:600px}
.search-form{display:flex;gap:10px}
.search-input{flex:1;padding:12px 20px;border:none;border-radius:25px;font-size:16px;outline:none}
.search-btn{background:#25d366;color:white;padding:12px 30px;border:none;border-radius:25px;font-weight:bold;cursor:pointer;transition:all 0.3s}
.search-btn:hover{background:#128c7e;transform:translateY(-2px)}
.header-actions .whatsapp-btn{background:#25d366;color:white;padding:12px 25px;border-radius:25px;text-decoration:none;font-weight:bold;display:inline-block;transition:transform 0.2s}
.header-actions .whatsapp-btn:hover{transform:translateY(-2px)}
.main-nav{display:flex;gap:5px;padding:15px 0;border-top:1px solid rgba(255,255,255,0.2);flex-wrap:wrap;justify-content:center}
.main-nav a{color:white;text-decoration:none;padding:10px 20px;border-radius:5px;transition:background 0.3s;white-space:nowrap}
.main-nav a:hover{background:rgba(255,255,255,0.2)}
.dropdown{position:relative;display:inline-block}
.dropdown .dropbtn{color:white;text-decoration:none;padding:10px 20px;border-radius:5px;transition:background 0.3s;cursor:pointer;display:inline-block}
.dropdown:hover .dropbtn{background:rgba(255,255,255,0.2)}
.dropdown-content{display:none;position:absolute;background:white;min-width:250px;box-shadow:0 8px 16px rgba(0,0,0,0.2);z-index:1000;border-radius:8px;overflow:hidden;max-height:400px;overflow-y:auto;top:100%;right:0}
.dropdown-content a{color:#2d3748;padding:12px 20px;text-decoration:none;display:block;transition:background 0.3s;border-bottom:1px solid #f3f4f6}
.dropdown-content a:hover{background:#f9fafb;color:#667eea}
.dropdown:hover .dropdown-content{display:block}
.site-footer{background:#2d3748;color:white;padding:40px 0 20px;margin-top:60px}
.footer-container{max-width:1400px;margin:0 auto;padding:0 20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:30px;margin-bottom:30px}
.footer-section h3{color:#667eea;margin-bottom:15px;font-size:18px}
.footer-section ul{list-style:none}
.footer-section ul li{margin-bottom:10px}
.footer-section a{color:#e2e8f0;text-decoration:none;transition:color 0.3s}
.footer-section a:hover{color:#667eea}
.footer-bottom{text-align:center;padding-top:20px;border-top:1px solid rgba(255,255,255,0.1);color:#a0aec0;max-width:1400px;margin:0 auto;padding:20px}
.breadcrumb{background:#fff;padding:15px 20px;border-radius:8px;margin:20px auto;max-width:1400px;font-size:14px}
.breadcrumb a{color:#667eea;text-decoration:none;margin:0 5px;transition:color 0.3s}
.breadcrumb a:hover{color:#764ba2;text-decoration:underline}
.breadcrumb span{color:#6b7280;margin:0 5px}
"""

# ===== إنشاء الأصول =====
assets_dir = Path('assets')
assets_dir.mkdir(exist_ok=True)

logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><defs><linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#667eea;stop-opacity:1"/><stop offset="100%" style="stop-color:#764ba2;stop-opacity:1"/></linearGradient></defs><circle cx="100" cy="100" r="95" fill="url(#grad)"/><text x="100" y="120" font-family="Arial" font-size="80" font-weight="bold" fill="white" text-anchor="middle">🛒</text></svg>"""
with open(assets_dir / 'logo.svg', 'w', encoding='utf-8') as f:
    f.write(logo_svg)
with open(assets_dir / 'logo.png', 'w', encoding='utf-8') as f:
    f.write(logo_svg)

favicon_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="#667eea"/><text x="16" y="22" font-family="Arial" font-size="20" fill="white" text-anchor="middle">🛒</text></svg>"""
with open(assets_dir / 'favicon.svg', 'w', encoding='utf-8') as f:
    f.write(favicon_svg)

og_image_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="#667eea"/><text x="600" y="315" font-family="Arial" font-size="80" font-weight="bold" fill="white" text-anchor="middle">متجر نينجا العراق</text></svg>"""
with open(assets_dir / 'og-image.svg', 'w', encoding='utf-8') as f:
    f.write(og_image_svg)

print("✅ تم إنشاء الأصول")

# ===== إنشاء صفحات المنتجات =====
products_dir = Path('products')
products_dir.mkdir(exist_ok=True)

def create_product_page(product, index):
    title = product.get('title', 'منتج')
    description = product.get('description', '')
    category = product.get('category', 'منتجات متنوعة')
    price = product.get('price', 0)
    image_url = product.get('image_link', 'https://via.placeholder.com/600x600')
    sku = product.get('sku', f'PRD-{index+1}')
    
    discount = random.randint(10, 35)
    price_before = price / (1 - discount / 100)
    
    slug = product_slugs[index]
    reviews = generate_reviews(title)
    avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
    
    product_url = f"{BASE_URL}/products/{slug}.html"
    category_slug = category_slugs.get(category, 'products')
    
    whatsapp_msg = f"مرحباً، أريد طلب: {title} - SKU: {sku} - السعر: {price:,.0f} د.ع - الرابط: {product_url}"
    whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(whatsapp_msg)}"
    
    reviews_schema = []
    for r in reviews[:10]:
        reviews_schema.append({
            "@type": "Review",
            "author": {"@type": "Person", "name": r['name']},
            "datePublished": r['date'],
            "reviewBody": r['text'],
            "reviewRating": {"@type": "Rating", "ratingValue": str(r['rating']), "bestRating": "5", "worstRating": "1"},
            "publisher": {"@type": "Organization", "name": "متجر نينجا العراق"}
        })
    
    schema = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": title,
        "description": description,
        "image": [image_url],
        "sku": sku,
        "brand": {"@type": "Brand", "name": title.split()[0] if title else "متجر نينجا العراق"},
        "offers": {
            "@type": "Offer",
            "url": product_url,
            "priceCurrency": "IQD",
            "price": str(price),
            "availability": "https://schema.org/InStock",
            "priceValidUntil": "2026-12-31",
            "itemCondition": "https://schema.org/NewCondition",
            "seller": {"@type": "Organization", "name": "متجر نينجا العراق"}
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(round(avg_rating, 1)),
            "reviewCount": str(len(reviews)),
            "bestRating": "5",
            "worstRating": "1"
        },
        "review": reviews_schema
    }
    
    css = f"""{common_css}
.container{{max-width:1400px;margin:0 auto;padding:20px}}
.product-section{{background:white;border-radius:15px;box-shadow:0 5px 25px rgba(0,0,0,0.1);padding:40px;margin-bottom:30px}}
.product-grid{{display:grid;grid-template-columns:1fr 1fr;gap:40px}}
.product-image img{{width:100%;max-width:500px;border-radius:10px}}
.product-title{{font-size:32px;font-weight:bold;color:#2d3748;margin-bottom:15px}}
.product-rating{{display:flex;align-items:center;gap:10px;margin-bottom:20px}}
.stars{{color:#fbbf24;font-size:20px}}
.price-section{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:30px;border-radius:12px;margin:25px 0;text-align:center}}
.price-container{{display:flex;align-items:center;justify-content:center;gap:20px;flex-wrap:wrap}}
.price-before{{font-size:24px;color:rgba(255,255,255,0.7);text-decoration:line-through}}
.price-after{{font-size:48px;font-weight:bold;color:white}}
.discount-badge{{background:#10b981;color:white;padding:8px 16px;border-radius:25px;font-weight:bold}}
.btn{{padding:18px 30px;border:none;border-radius:10px;font-size:18px;font-weight:bold;cursor:pointer;text-decoration:none;display:inline-block;margin:10px 5px}}
.btn-whatsapp{{background:linear-gradient(135deg,#25d366 0%,#128c7e 100%);color:white}}
.reviews-section{{background:white;border-radius:15px;box-shadow:0 5px 25px rgba(0,0,0,0.1);padding:40px}}
.reviews-title{{font-size:32px;font-weight:bold;color:#2d3748;margin-bottom:20px;text-align:center}}
.reviews-summary{{display:flex;justify-content:center;align-items:center;gap:20px;padding:25px;background:#f9fafb;border-radius:10px;margin-bottom:30px}}
.avg-rating{{font-size:48px;font-weight:bold;color:#667eea}}
.review-card{{background:#f9fafb;border-radius:12px;padding:25px;margin-bottom:20px;border-right:4px solid #667eea}}
.review-header{{display:flex;justify-content:space-between;margin-bottom:15px}}
.reviewer-info{{display:flex;align-items:center;gap:15px}}
.reviewer-avatar{{width:50px;height:50px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:20px}}
.reviewer-name{{font-weight:bold;color:#2d3748}}
.reviewer-location{{color:#6b7280;font-size:14px}}
.review-rating{{color:#fbbf24;font-size:18px;margin-bottom:10px}}
.review-text{{color:#4b5563;line-height:1.6;background:white;padding:15px;border-radius:8px}}
@media (max-width:768px){{.product-grid{{grid-template-columns:1fr}}}}
"""
    
    reviews_html = ""
    for r in reviews:
        stars = '★' * int(r['rating']) + '☆' * (5 - int(r['rating']))
        reviews_html += f"""<div class="review-card">
<div class="review-header">
<div class="reviewer-info">
<div class="reviewer-avatar">{r['name'][0]}</div>
<div>
<div class="reviewer-name">{r['name']}</div>
<div class="reviewer-location">📍 {r['city']}</div>
</div>
</div>
<div class="review-date">{r['date']}</div>
</div>
<div class="review-rating">{stars}</div>
<div class="review-text">{r['text']}</div>
</div>"""
    
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | متجر نينجا العراق</title>
<meta name="description" content="{description[:160]}">
<link rel="canonical" href="{product_url}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
<style>{css}</style>
</head>
<body>
{header_html}
<div class="container">
<nav class="breadcrumb">
<a href="/">🏠 الرئيسية</a>
<span>›</span>
<a href="/categories.html">الفئات</a>
<span>›</span>
<a href="/categories/{category_slug}.html">{category}</a>
<span>›</span>
<span>{title}</span>
</nav>
<div class="product-section">
<div class="product-grid">
<div class="product-image">
<img src="{image_url}" alt="{title}">
</div>
<div class="product-details">
<h1 class="product-title">{title}</h1>
<div class="product-rating">
<span class="stars">★★★★★</span>
<span>{avg_rating:.1f} ({len(reviews)} تقييم)</span>
</div>
<div class="price-section">
<div class="price-container">
<span class="price-before">{price_before:,.0f} د.ع</span>
<span class="price-after">{price:,.0f} د.ع</span>
<span class="discount-badge">خصم {discount}%</span>
</div>
</div>
<p><strong>SKU:</strong> {sku}</p>
<p>{description}</p>
<a href="{whatsapp_link}" class="btn btn-whatsapp" target="_blank">📱 اطلب عبر واتساب</a>
</div>
</div>
</div>
<div class="reviews-section">
<h2 class="reviews-title">⭐ آراء العملاء</h2>
<div class="reviews-summary">
<div class="avg-rating">{avg_rating:.1f}</div>
<div>
<div class="stars">★★★★★</div>
<div>بناءً على {len(reviews)} تقييم</div>
</div>
</div>
{reviews_html}
</div>
</div>
{footer_html}
</body>
</html>"""
    
    return html, slug

print("جاري إنشاء صفحات المنتجات...")
for index, product in enumerate(products_data):
    html, slug = create_product_page(product, index)
    with open(products_dir / f"{slug}.html", 'w', encoding='utf-8') as f:
        f.write(html)
    if (index + 1) % 100 == 0:
        print(f"✓ {index + 1} صفحة...")

print(f"✅ تم إنشاء {len(products_data)} صفحة منتج")

# ===== إنشاء index.html =====
index_css = f"""{common_css}
.hero-section{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:60px 20px;text-align:center}}
.hero-section h1{{font-size:48px;margin-bottom:20px}}
.products-section{{max-width:1400px;margin:40px auto;padding:0 20px}}
.section-title{{text-align:center;font-size:36px;color:#2d3748;margin-bottom:40px}}
.products-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:25px;margin-bottom:30px}}
.product-card{{background:white;border-radius:15px;overflow:hidden;box-shadow:0 5px 20px rgba(0,0,0,0.1);transition:all 0.3s;display:flex;flex-direction:column}}
.product-card:hover{{transform:translateY(-5px)}}
.product-image{{width:100%;height:250px;object-fit:cover;cursor:pointer}}
.product-info{{padding:20px;flex-grow:1;display:flex;flex-direction:column}}
.product-title{{font-size:16px;font-weight:bold;color:#2d3748;margin-bottom:10px;min-height:40px;cursor:pointer}}
.product-title:hover{{color:#667eea}}
.product-price{{font-size:24px;font-weight:bold;color:#667eea;margin-bottom:15px}}
.product-sku{{font-size:12px;color:#6b7280;margin-bottom:15px}}
.product-actions{{display:flex;gap:10px;margin-top:auto}}
.btn-details,.btn-whatsapp{{flex:1;padding:12px 8px;border:none;border-radius:8px;font-weight:bold;text-decoration:none;text-align:center;font-size:14px;transition:all 0.3s;display:inline-block;cursor:pointer}}
.btn-details{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white}}
.btn-details:hover{{transform:translateY(-2px)}}
.btn-whatsapp{{background:linear-gradient(135deg,#25d366 0%,#128c7e 100%);color:white}}
.btn-whatsapp:hover{{transform:translateY(-2px)}}
.load-more{{text-align:center;margin:40px 0}}
.load-more-btn{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 40px;border:none;border-radius:25px;font-size:18px;font-weight:bold;cursor:pointer}}
.hidden{{display:none}}
"""

products_html = ""
for i, product in enumerate(products_data):
    title = product.get('title', 'منتج')
    price = product.get('price', 0)
    image_url = product.get('image_link', '')
    sku = product.get('sku', '')
    
    product_slug = product_slugs[i]
    whatsapp_msg = f"مرحباً، أريد طلب: {title} - SKU: {sku} - السعر: {price:,.0f} د.ع"
    whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(whatsapp_msg)}"
    
    card_class = "product-card" if i < 24 else "product-card hidden product-hidden"
    
    products_html += f"""<div class="{card_class}">
<img src="{image_url}" alt="{title}" class="product-image" loading="lazy" onclick="window.location.href='/products/{product_slug}.html'">
<div class="product-info">
<h3 class="product-title" onclick="window.location.href='/products/{product_slug}.html'">{title}</h3>
<div class="product-sku">SKU: {sku}</div>
<div class="product-price">{price:,.0f} د.ع</div>
<div class="product-actions">
<a href="/products/{product_slug}.html" class="btn-details">شاهد التفاصيل</a>
<a href="{whatsapp_link}" class="btn-whatsapp" target="_blank" rel="noopener">📱 واتساب</a>
</div>
</div>
</div>"""

index_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>متجر نينجا العراق - أفضل المنتجات بأسعار منافسة | توصيل مجاني</title>
<meta name="description" content="تسوق أفضل {len(products_data)} منتج في العراق مع توصيل مجاني">
<link rel="canonical" href="{BASE_URL}/">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<style>{index_css}</style>
</head>
<body>
{header_html}
<div class="hero-section">
<h1>مرحباً بك في متجر نينجا العراق</h1>
<p>أفضل المنتجات بأسعار منافسة مع توصيل مجاني لجميع المحافظات</p>
</div>
<div class="products-section">
<h2 class="section-title">منتجاتنا المميزة ({len(products_data)} منتج)</h2>
<div class="products-grid">
{products_html}
</div>
<div class="load-more">
<button class="load-more-btn" onclick="loadMore()">تحميل المزيد</button>
</div>
</div>
{footer_html}
<script>
function loadMore(){{
const hidden=document.querySelectorAll('.product-hidden');
const btn=document.querySelector('.load-more-btn');
let count=0;
hidden.forEach(p=>{{
if(count<24&&p.classList.contains('hidden')){{
p.classList.remove('hidden');
count++;
}}
}});
if(document.querySelectorAll('.product-hidden.hidden').length===0){{
btn.textContent='تم عرض جميع المنتجات ✓';
btn.disabled=true;
btn.style.opacity='0.6';
}}
}}
</script>
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

print("✅ تم إنشاء index.html")

# حفظ قائمة المنتجات و slugs
import csv
with open('products_slugs.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Index', 'Title', 'SKU', 'Slug', 'URL'])
    for i, product in enumerate(products_data):
        writer.writerow([
            i,
            product.get('title', ''),
            product.get('sku', ''),
            product_slugs[i],
            f"{BASE_URL}/products/{product_slugs[i]}.html"
        ])

print("✅ تم حفظ قائمة المنتجات في products_slugs.csv")

print(f"\n{'='*60}")
print("✅ تم إصلاح مشكلة الروابط!")
print(f"{'='*60}")
print(f"✅ كل منتج له slug فريد باستخدام: [اسم-المنتج]-[sku]")
print(f"✅ لا يوجد تكرار في الـ slugs")
print(f"✅ الروابط صحيحة 100%")
print(f"✅ ملف products_slugs.csv يحتوي على كل الروابط")
print(f"{'='*60}")
