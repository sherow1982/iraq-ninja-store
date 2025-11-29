// قاعدة بيانات المنتجات
const products = [
    {name: 'جهاز اعداد الفشار', sku: 'A.000161', price: '73,400', url: '/products/جهاز-اعداد-الفشار-a000161.html'},
    {name: 'الشورت الحراري', sku: 'A.002102', price: '73,400', url: '/products/الشورت-الحراري-a002102.html'},
    {name: 'نظارة القراءة وحماية العين من الاشعة', sku: 'A.000855', price: '75,100', url: '/products/نظارة-القراءة-وحماية-العين-من-الاشعة-a000855.html'},
    {name: 'منظف ​​اسطوانة الغسالة', sku: 'A.001433', price: '75,131', url: '/products/منظف-اسطوانة-الغسالة-a001433.html'},
    {name: 'قلم اللحية لملئ الفراغات و تحديد', sku: 'A.002225', price: '75,481', url: '/products/قلم-اللحية-لملئ-الفراغات-و-تحديد-a002225.html'},
    {name: 'زيت أوميغا لتطويل اللحية وتعبئة الفراغات', sku: 'A.000185', price: '75,901', url: '/products/زيت-أوميغا-لتطويل-اللحية-وتعبئة-الفراغات-a000185.html'},
    {name: 'ميزان الطعام', sku: 'A.001247', price: '76,030', url: '/products/ميزان-الطعام-a001247.html'},
    {name: 'حزام الرقبة المغناطيسي', sku: 'A.001299', price: '76,190', url: '/products/حزام-الرقبة-المغناطيسي-a001299.html'},
    {name: 'بخاخ و لوشن لإزالة الشعر من مذهلة', sku: 'A.002151', price: '76,540', url: '/products/بخاخ-و-لوشن-لإزالة-الشعر-من-مذهلة-a002151.html'},
    {name: 'معجون أسنان لتبييض الأسنان', sku: 'A.000856', price: '77,250', url: '/products/معجون-أسنان-لتبييض-الأسنان-و-ازالة-البقع-بشكل-احترافي-a000856.html'},
    {name: 'قطاعة متعددة الوظائف', sku: 'A.001147', price: '89,381', url: '/products/قطاعة-متعددة-الوظائف-a001147.html'},
    {name: 'داعم الظهر السحري', sku: 'A.001316', price: '100,440', url: '/products/داعم-الظهر-السحري-a001316.html'},
    {name: 'معجون تنظيف الفرن والاواني', sku: 'A.001730', price: '100,846', url: '/products/معجون-تنظيف-الفرن-والاواني-a001730.html'},
    {name: 'مجففة الملابس العجبية', sku: 'A.000416', price: '89,381', url: '/products/مجففة-الملابس-العجبية-a000416.html'},
    {name: 'خلاط عصير محمول', sku: 'A.000154', price: '100,540', url: '/products/خلاط-عصير-محمول-يعمل-على-بطارية-قابلة-للشحن-a000154.html'}
];

// الكلمات المفتاحية للأسئلة
const keywordMap = {
    'سعر': 'أسعارنا تتراوح من 73,000 إلى 100,000 دينار عراقي حسب المنتج. استخدم زر "شاهد التفاصيل" لمعرفة سعر المنتج بالضبط.',
    'توصيل': 'نوفر توصيل مجاني لجميع المحافظات العراقية! 🚚 اطلب الآن عبر واتساب.',
    'واتساب': 'تواصل معنا عبر واتساب: https://wa.me/201110760081 📱',
    'منتج': 'لدينا أكثر من 300 منتج متنوع! ما المنتج الذي تبحث عنه؟',
    'دفع': 'الدفع عند الاستلام متاح لجميع المحافظات. يمكنك الطلب عبر واتساب.',
    'جودة': 'جميع منتجاتنا أصلية ومضمونة بجودة عالية ✅',
    'ضمان': 'نوفر ضمان استرجاع واستبدال حسب سياسة المتجر.',
    'مرحبا': 'مرحباً بك! 👋 كيف يمكنني مساعدتك؟',
    'شكرا': 'العفو! سعداء بخدمتك 😊'
};

// البحث عن منتج بالاسم أو SKU
function searchProduct(query) {
    query = query.toLowerCase();
    return products.filter(p => 
        p.name.toLowerCase().includes(query) || 
        p.sku.toLowerCase().includes(query)
    );
}

// توليد رد الروبوت
function getBotResponse(userMessage) {
    userMessage = userMessage.trim();
    
    // البحث في المنتجات أولاً
    const foundProducts = searchProduct(userMessage);
    if (foundProducts.length > 0) {
        let response = `وجدت ${foundProducts.length} منتج:\n\n`;
        foundProducts.forEach(p => {
            response += `🛍️ ${p.name}\n`;
            response += `💰 السعر: ${p.price} د.ع\n`;
            response += `📦 SKU: ${p.sku}\n`;
            response += `🔗 <a href="${p.url}" target="_blank">شاهد التفاصيل</a>\n\n`;
        });
        return response;
    }
    
    // البحث في الكلمات المفتاحية
    for (const [keyword, response] of Object.entries(keywordMap)) {
        if (userMessage.includes(keyword)) {
            return response;
        }
    }
    
    return 'عذراً، لم أفهم سؤالك. يمكنك:\n• سؤالي عن منتج معين\n• سؤالي عن الأسعار أو التوصيل\n• التواصل مع خدمة العملاء: https://wa.me/201110760081';
}

// إضافة رسالة للشات
function addMessage(text, isBot = false) {
    const messagesContainer = document.getElementById('chatbot-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isBot ? 'bot-message' : 'user-message'}`;
    messageDiv.innerHTML = text;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// إرسال رسالة
function sendMessage() {
    const input = document.getElementById('user-input');
    const userMessage = input.value.trim();
    
    if (userMessage === '') return;
    
    // إضافة رسالة المستخدم
    addMessage(userMessage, false);
    input.value = '';
    
    // الحصول على رد الروبوت
    setTimeout(() => {
        const botResponse = getBotResponse(userMessage);
        addMessage(botResponse, true);
    }, 500);
}

// تهيئة الروبوت
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('chatbot-toggle');
    const closeBtn = document.getElementById('chatbot-close');
    const chatWindow = document.getElementById('chatbot-window');
    const sendBtn = document.getElementById('send-button');
    const input = document.getElementById('user-input');
    
    // فتح/إغلاق النافذة
    toggleBtn.addEventListener('click', () => {
        chatWindow.classList.toggle('hidden');
        toggleBtn.setAttribute('aria-expanded', !chatWindow.classList.contains('hidden'));
    });
    
    closeBtn.addEventListener('click', () => {
        chatWindow.classList.add('hidden');
        toggleBtn.setAttribute('aria-expanded', 'false');
    });
    
    // إرسال رسالة
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});