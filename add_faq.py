import os
import re

# FAQ HTML and CSS
FAQ_STYLE = """
<style>
.faq-section {
    background: white;
    border-radius: 15px;
    box-shadow: 0 5px 25px rgba(0,0,0,0.1);
    padding: 40px;
    margin-top: 30px;
    margin-bottom: 30px;
}
.faq-title {
    font-size: 32px;
    font-weight: bold;
    color: #2d3748;
    margin-bottom: 30px;
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.faq-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 25px;
}
.faq-item {
    background: #f9fafb;
    padding: 25px;
    border-radius: 12px;
    border-right: 4px solid #667eea;
    transition: transform 0.3s ease;
}
.faq-item:hover {
    transform: translateY(-5px);
}
.faq-question {
    font-weight: bold;
    color: #2d3748;
    margin-bottom: 12px;
    font-size: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.faq-answer {
    color: #4b5563;
    line-height: 1.6;
}
</style>
"""

FAQ_HTML = """
<section class="faq-section">
    <h2 class="faq-title">🤔 الأسئلة الشائعة</h2>
    <div class="faq-grid">
        <div class="faq-item">
            <div class="faq-question">🚚 هل التوصيل مجاني؟</div>
            <div class="faq-answer">نعم، نوفر خدمة التوصيل المجاني والسريع لجميع محافظات العراق الحبيبة لجميع الطلبات.</div>
        </div>
        <div class="faq-item">
            <div class="faq-question">⏱️ كم يستغرق وصول الطلب؟</div>
            <div class="faq-answer">يستغرق التوصيل عادةً من 2 إلى 4 أيام عمل حسب محافظتك (بغداد والمحافظات).</div>
        </div>
        <div class="faq-item">
            <div class="faq-question">🔍 هل يمكنني فحص المنتج قبل الدفع؟</div>
            <div class="faq-answer">بكل تأكيد! نضمن لك حق فحص المنتج والتأكد من جودته ومطابقته قبل تسليم المبلغ للمندوب.</div>
        </div>
        <div class="faq-item">
            <div class="faq-question">🔄 ما هي سياسة الاستبدال؟</div>
            <div class="faq-answer">نوفر سياسة استبدال مرنة خلال 14 يوماً في حال وجود أي خلل مصنعي. رضاكم هو أولويتنا.</div>
        </div>
    </div>
</section>
"""

def update_product_pages():
    products_dir = 'products'
    if not os.path.exists(products_dir):
        print(f"Error: {products_dir} group not found.")
        return

    count = 0
    for filename in os.listdir(products_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(products_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip if FAQ already exists
            if 'faq-section' in content:
                continue

            # Insert CSS in head
            if '</style>' in content:
                content = content.replace('</style>', FAQ_STYLE + '</style>', 1)
            
            # Insert FAQ before footer
            if '<footer' in content:
                content = content.replace('<footer', FAQ_HTML + '<footer', 1)
            elif '</body>' in content:
                content = content.replace('</body>', FAQ_HTML + '</body>', 1)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            count += 1
            if count % 50 == 0:
                print(f"Updated {count} files...")

    print(f"Successfully updated {count} product pages with FAQ section!")

if __name__ == "__main__":
    update_product_pages()
