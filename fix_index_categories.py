# fix_index_categories.py
from pathlib import Path
import json
import urllib.parse
import re

BASE_URL = "https://iraq-ninja-store.arabsad.com"
WHATSAPP_NUMBER = "201110760081"

with open('products.json', 'r', encoding='utf-8') as f:
    products_data = json.load(f)

used_slugs = {}

def create_slug(text):
    if not text:
        return "product"
    slug = str(text).strip().lower()
    slug = re.sub(r'[^\w\s\-أ-ي]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    original_slug = slug
    counter = 1
    while slug in used_slugs:
        slug = f"{original_slug}-{counter}"
        counter += 1
    used_slugs[slug] = True
    return slug

# Header مع البحث
header_html = """
<header class="site-header">
    <div class="header-container">
        <div class="logo">
            <a href="/index.html">🛒 متجر نينجا العراق</a>
        </div>
        <div class="search-box">
            <form action="/404.html" method="get" class="search-form">
                <input type="text" name="q" placeholder="ابحث عن منتج..." class="search-input" required>
                <button type="submit" class="search-btn">🔍 بحث</button>
            </form>
        </div>
        <nav class="main-nav">
            <a href="/index.html">الرئيسية</a>
            <a href="/categories.html">الفئات</a>
            <a href="/legal/about.html">من نحن</a>
            <a href="/legal/contact.html">اتصل بنا</a>
            <a href="/legal/shipping.html">الشحن</a>
            <a href="/legal/returns.html">الاسترجاع</a>
            <a href="/legal/privacy.html">الخصوصية</a>
        </nav>
        <div class="header-actions">
            <a href="https://wa.me/201110760081" class="whatsapp-btn" target="_blank">📱 واتساب</a>
        </div>
    </div>
</header>
"""

footer_html = """
<footer class="site-footer">
    <div class="footer-container">
        <div class="footer-section">
            <h3>متجر نينجا العراق</h3>
            <p>أفضل المنتجات بأسعار منافسة مع توصيل مجاني</p>
        </div>
        <div class="footer-section">
            <h3>روابط سريعة</h3>
            <ul>
                <li><a href="/index.html">الرئيسية</a></li>
                <li><a href="/categories.html">الفئات</a></li>
                <li><a href="/legal/contact.html">اتصل بنا</a></li>
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
body{font-family:'Segoe UI',Tahoma,sans-serif;background:#f5f5f5;color:#333;direction:rtl}
.site-header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:20px 0;box-shadow:0 2px 10px rgba(0,0,0,0.1);position:sticky;top:0;z-index:1000}
.header-container{max-width:1200px;margin:0 auto;padding:0 20px;display:flex;flex-direction:column;gap:15px}
.logo a{color:white;text-decoration:none;font-size:24px;font-weight:bold;display:inline-block}
.search-box{width:100%}
.search-form{display:flex;gap:10px;max-width:600px;margin:0 auto}
.search-input{flex:1;padding:12px 20px;border:none;border-radius:25px;font-size:16px;outline:none}
.search-btn{background:#25d366;color:white;padding:12px 30px;border:none;border-radius:25px;font-weight:bold;cursor:pointer;transition:all 0.3s}
.search-btn:hover{background:#128c7e;transform:translateY(-2px)}
.main-nav{display:flex;gap:15px;flex-wrap:wrap;justify-content:center}
.main-nav a{color:white;text-decoration:none;padding:8px 16px;border-radius:5px;transition:background 0.3s}
.main-nav a:hover{background:rgba(255,255,255,0.2)}
.header-actions{text-align:center}
.whatsapp-btn{background:#25d366;color:white;padding:10px 20px;border-radius:25px;text-decoration:none;font-weight:bold;transition:transform 0.2s;display:inline-block}
.whatsapp-btn:hover{transform:translateY(-2px)}
.site-footer{background:#2d3748;color:white;padding:40px 0 20px;margin-top:60px}
.footer-container{max-width:1200px;margin:0 auto;padding:0 20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:30px}
.footer-section h3{color:#667eea;margin-bottom:15px}
.footer-section ul{list-style:none}
.footer-section li{margin-bottom:10px}
.footer-section a{color:#e2e8f0;text-decoration:none}
.footer-bottom{text-align:center;padding-top:20px;color:#a0aec0}
.hero-section{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:60px 20px;text-align:center}
.hero-section h1{font-size:48px;margin-bottom:20px}
.products-section{max-width:1400px;margin:40px auto;padding:0 20px}
.section-title{text-align:center;font-size:36px;color:#2d3748;margin-bottom:40px}
.products-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:25px;margin-bottom:30px}
.product-card{background:white;border-radius:15px;overflow:hidden;box-shadow:0 5px 20px rgba(0,0,0,0.1);transition:all 0.3s;cursor:pointer;display:flex;flex-direction:column}
.product-card:hover{transform:translateY(-5px);box-shadow:0 10px 30px rgba(0,0,0,0.15)}
.product-image{width:100%;height:250px;object-fit:cover;background:#f5f5f5}
.product-info{padding:20px;flex-grow:1;display:flex;flex-direction:column}
.product-title{font-size:16px;font-weight:bold;color:#2d3748;margin-bottom:10px;min-height:40px}
.product-price{font-size:24px;font-weight:bold;color:#667eea;margin-bottom:15px}
.product-sku{font-size:12px;color:#6b7280;margin-bottom:15px}
.product-actions{display:flex;gap:10px;margin-top:auto}
.btn-details{flex:1;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:12px;border:none;border-radius:8px;font-weight:bold;text-decoration:none;text-align:center}
.btn-whatsapp{flex:1;background:linear-gradient(135deg,#25d366 0%,#128c7e 100%);color:white;padding:12px;border:none;border-radius:8px;font-weight:bold;text-decoration:none;text-align:center}
.load-more{text-align:center;margin:40px 0}
.load-more-btn{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 40px;border:none;border-radius:25px;font-size:18px;font-weight:bold;cursor:pointer}
.hidden{display:none}
"""

products_cards = ""
for i, product in enumerate(products_data):
    title = product.get('title', 'منتج')
    price = product.get('price', 0)
    image_url = product.get('image_link', '')
    sku = product.get('sku', '')
    
    product_slug = create_slug(title)
    
    whatsapp_msg = f"مرحباً، أريد طلب: {title} - SKU: {sku} - السعر: {price:,.0f} د.ع - الرابط: {BASE_URL}/products/{product_slug}.html"
    whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(whatsapp_msg)}"
    
    card_class = "product-card" if i < 24 else "product-card hidden product-hidden"
    
    products_cards += f"""
    <div class="{card_class}" onclick="window.location.href='/products/{product_slug}.html'">
        <img src="{image_url}" alt="{title}" class="product-image" loading="lazy">
        <div class="product-info">
            <h3 class="product-title">{title}</h3>
            <div class="product-sku">SKU: {sku}</div>
            <div class="product-price">{price:,.0f} د.ع</div>
            <div class="product-actions">
                <a href="/products/{product_slug}.html" class="btn-details" onclick="event.stopPropagation()">شاهد التفاصيل</a>
                <a href="{whatsapp_link}" class="btn-whatsapp" target="_blank" onclick="event.stopPropagation()">📱 واتساب</a>
            </div>
        </div>
    </div>
    """

index_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>متجر نينجا العراق - أفضل المنتجات بأسعار منافسة | توصيل مجاني</title>
<meta name="description" content="تسوق أفضل {len(products_data)} منتج في العراق مع توصيل مجاني">
<link rel="canonical" href="{BASE_URL}/">
<style>{common_css}</style>
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
{products_cards}
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

print("✅ تم تحديث index.html مع البحث والتحميل المتقدم")
