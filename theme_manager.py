# Global Store Optimization Script
import os
import re

# The base URL for GitHub Pages
BASE_URL = "https://sherow1982.github.io/iraq-ninja-store/"
BASE_TAG = f'<base href="{BASE_URL}">'

WOODMART_STYLE = """
<style>
/* Theme Overhaul: Woodmart Style */
:root {
    --primary-color: #764ba2;
    --secondary-color: #667eea;
    --text-dark: #2d3748;
    --bg-light: #f8fafc;
    --white: #ffffff;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
    --radius: 8px;
}

body {
    font-family: 'Inter', 'Segoe UI', Tahoma, sans-serif !important;
    background-color: var(--bg-light) !important;
    color: var(--text-dark) !important;
}

.site-header {
    background: var(--white) !important;
    color: var(--text-dark) !important;
    border-bottom: 1px solid #e2e8f0;
    box-shadow: var(--shadow-sm) !important;
}
.logo a, .main-nav a, .dropdown .dropbtn { color: var(--text-dark) !important; }
.main-nav { border-top: 1px solid #f1f5f9 !important; }
.search-input { background: #f1f5f9 !important; border: 1px solid #e2e8f0 !important; }
.search-btn { background: var(--primary-color) !important; }

/* Section Styling */
.product-section, .reviews-section, .faq-section {
    background: var(--white) !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: var(--shadow-sm) !important;
    border-radius: var(--radius) !important;
    margin-bottom: 30px !important;
    padding: 30px !important;
}

.faq-title { 
    color: var(--text-dark) !important; 
    font-weight: 800 !important; 
    border-bottom: 3px solid var(--primary-color);
    display: inline-block;
    margin-bottom: 25px !important;
}
.faq-item { 
    background: #f9fafb !important; 
    border-right: 5px solid var(--primary-color) !important; 
    margin-bottom: 15px;
    padding: 20px;
    border-radius: var(--radius);
}
</style>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
"""

FAQ_TEMPLATE = """
<section class="faq-section">
    <h2 class="faq-title">🤔 الأسئلة الشائعة حول {product_name}</h2>
    <div class="faq-grid">
        <div class="faq-item">
            <div class="faq-question">🚚 هل توصيل {product_name} مجاني؟</div>
            <div class="faq-answer">نعم، نوفر خدمة التوصيل المجاني والسريع لمنتج {product_name} لجميع محافظات العراق الحبيبة.</div>
        </div>
        <div class="faq-item">
            <div class="faq-question">⏱️ كم يستغرق وصول المنتج؟</div>
            <div class="faq-answer">يستغرق توصيل {product_name} عادةً من 2 إلى 4 أيام عمل حسب محافظتك.</div>
        </div>
        <div class="faq-item">
            <div class="faq-question">🔍 هل يمكنني فحص المنتج قبل الدفع؟</div>
            <div class="faq-answer">بكل تأكيد! نضمن لك حق فحص {product_name} والتأكد من جودته ومطابقته قبل الاستلام.</div>
        </div>
        <div class="faq-item">
            <div class="faq-question">🔄 ما هي سياسة الاستبدال؟</div>
            <div class="faq-answer">نوفر سياسة استبدال مرنة لـ {product_name} خلال 14 يوماً في حال وجود أي خلل مصنعي.</div>
        </div>
    </div>
</section>
"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Base Tag Fix (Ensure unique and correct)
    content = re.sub(r'<base href=".*?">', '', content) # Remove any existing
    content = content.replace('<head>', f'<head>\n{BASE_TAG}')

    # 2. Convert Absolute Links/Sources/Actions to Relative
    content = content.replace('href="/', 'href="')
    content = content.replace('src="/', 'src="')
    content = content.replace('action="/', 'action="')
    content = content.replace("window.location.href='/", "window.location.href='")

    # 3. Inject Woodmart Theme & Clean up old style/font duplicates
    # Remove previous injections of Woodmart/Inter Font to avoid duplicates
    # Improved regex to catch the block whether it has <style> tags or not, and handle broken HTML
    content = re.sub(r'(<style>)?\s*/\* Theme Overhaul.*?</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'/\* Theme Overhaul.*?\*/.*?\.faq-item\s*{.*?}', '', content, flags=re.DOTALL)
    
    content = content.replace('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">', '')
    content = content.replace('</style>\n</style>', '</style>')
    
    # Inject fresh
    if '</head>' in content:
        content = content.replace('</head>', WOODMART_STYLE + '\n</head>')

    # 4. Product-Specific FAQ
    if 'products' in filepath.lower():
        title_match = re.search(r'<h1 class="product-title">(.*?)</h1>', content)
        if not title_match:
            title_match = re.search(r'<title>(.*?)</title>', content)
        
        product_name = title_match.group(1).split('|')[0].split('-')[0].strip() if title_match else "هذا المنتج"
        faq_html = FAQ_TEMPLATE.format(product_name=product_name)
        
        # Clean ALL FAQ sections (old and new)
        content = re.sub(r'<section class="faq-section">.*?</section>', '', content, flags=re.DOTALL)
        
        # Insert before reviews or footer
        if '<div class="reviews-section">' in content:
            content = content.replace('<div class="reviews-section">', faq_html + '\n<div class="reviews-section">')
        elif '<footer' in content:
            content = content.replace('<footer', faq_html + '\n<footer')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def run():
    print(f"Starting Global Optimization for {BASE_URL}...")
    count = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html') and 'theme_manager' not in file:
                process_file(os.path.join(root, file))
                count += 1
    print(f"Success! Optimized {count} files. 🚀")

if __name__ == "__main__":
    run()
