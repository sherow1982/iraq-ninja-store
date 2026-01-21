
import os
import re

# Woodmart Theme Style Constants
WOODMART_STYLE = """
/* Theme Overhaul: Woodmart Style */
:root {
    --primary-color: #764ba2;
    --secondary-color: #667eea;
    --text-dark: #2d3748;
    --text-muted: #718096;
    --bg-light: #f8fafc;
    --white: #ffffff;
    --accent: #25d366;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    --radius: 8px;
}

body {
    font-family: 'Inter', 'Segoe UI', Tahoma, sans-serif !important;
    background-color: var(--bg-light) !important;
    color: var(--text-dark) !important;
}

/* Header Refinement */
.site-header {
    background: var(--white) !important;
    color: var(--text-dark) !important;
    border-bottom: 1px solid #e2e8f0;
    box-shadow: var(--shadow-sm) !important;
}
.logo a, .main-nav a, .dropdown .dropbtn {
    color: var(--text-dark) !important;
}
.main-nav {
    border-top: 1px solid #f1f5f9 !important;
}
.main-nav a:hover {
    background: #f8fafc !important;
    color: var(--primary-color) !important;
}
.search-input {
    background: #f1f5f9 !important;
    border: 1px solid #e2e8f0 !important;
    color: var(--text-dark) !important;
}
.search-btn {
    background: var(--primary-color) !important;
}

/* Hero Section */
.hero-section {
    background: var(--white) !important;
    color: var(--text-dark) !important;
    padding: 80px 20px !important;
    border-bottom: 1px solid #e2e8f0;
}
.hero-section h1 {
    font-weight: 800;
    letter-spacing: -1px;
}

/* Product Cards */
.product-card {
    border: 1px solid #e2e8f0 !important;
    box-shadow: none !important;
    border-radius: var(--radius) !important;
}
.product-card:hover {
    box-shadow: var(--shadow-lg) !important;
    border-color: var(--primary-color) !important;
}
.btn-details {
    background: var(--primary-color) !important;
}

/* Content Sections */
.product-section, .reviews-section, .faq-section {
    background: var(--white) !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: var(--shadow-sm) !important;
    border-radius: var(--radius) !important;
}

/* FAQ Section Woodmart Style */
.faq-section {
    padding: 50px !important;
}
.faq-title {
    background: none !important;
    -webkit-text-fill-color: initial !important;
    color: var(--text-dark) !important;
    font-weight: 800 !important;
    border-bottom: 2px solid var(--primary-color);
    display: inline-block;
    margin-bottom: 40px !important;
}
.faq-item {
    background: var(--white) !important;
    border: 1px solid #f1f5f9 !important;
    border-right: 4px solid var(--primary-color) !important;
}

/* Professional Typography */
h1, h2, h3 {
    font-weight: 700 !important;
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
            <div class="faq-answer">يستغرق توصيل {product_name} عادةً من 2 إلى 4 أيام عمل حسب محافظتك (بغداد والمحافظات).</div>
        </div>
        <div class="faq-item">
            <div class="faq-question">🔍 هل يمكنني فحص المنتج قبل الدفع؟</div>
            <div class="faq-answer">بكل تأكيد! نضمن لك حق فحص {product_name} والتأكد من جودته ومطابقته قبل تسليم المبلغ للمندوب.</div>
        </div>
        <div class="faq-item">
            <div class="faq-question">🔄 ما هي سياسة الاستبدال؟</div>
            <div class="faq-answer">نوفر سياسة استبدال مرنة لـ {product_name} خلال 14 يوماً في حال وجود أي خلل مصنعي. رضاكم هو أولويتنا.</div>
        </div>
    </div>
</section>
"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Inject or Update Style
    if 'WOODMART_STYLE' in content or 'Theme Overhaul: Woodmart Style' in content:
        # Update existing style block
        content = re.sub(r'/\* Theme Overhaul: Woodmart Style \*/.*?</style>', WOODMART_STYLE + '</style>', content, flags=re.DOTALL)
    else:
        # Add inside head
        if '</head>' in content:
            content = content.replace('</head>', WOODMART_STYLE + '\n</head>')

    # 2. Add/Reposition FAQ (Only for product pages)
    if 'products' in filepath:
        # Extract product name from <h1 class="product-title">
        title_match = re.search(r'<h1 class="product-title">(.*?)</h1>', content)
        product_name = title_match.group(1).strip() if title_match else "هذا المنتج"
        
        # Customize FAQ
        faq_html = FAQ_TEMPLATE.format(product_name=product_name)

        # Remove old FAQ if exists
        content = re.sub(r'<section class="faq-section">.*?</section>', '', content, flags=re.DOTALL)
        
        # Insert before reviews-section if it exists, else before footer
        if '<div class="reviews-section">' in content:
            content = content.replace('<div class="reviews-section">', faq_html + '\n<div class="reviews-section">')
        elif '<footer' in content:
            content = content.replace('<footer', faq_html + '\n<footer')
        else:
            content = content.replace('</body>', faq_html + '\n</body>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def overhaul_theme():
    # Root level files
    for root_file in ['index.html', 'categories.html', '404.html']:
        if os.path.exists(root_file):
            print(f"Processing root file: {root_file}...")
            process_file(root_file)

    # Folders
    for folder in ['products', 'categories', 'legal']:
        if os.path.exists(folder):
            print(f"Processing folder: {folder}...")
            for filename in os.listdir(folder):
                if filename.endswith('.html'):
                    filepath = os.path.join(folder, filename)
                    process_file(filepath)
    
    print("Theme overhaul complete! 🚀")

if __name__ == "__main__":
    overhaul_theme()
