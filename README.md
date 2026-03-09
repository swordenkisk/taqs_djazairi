```markdown
# الطاقس الجزائري — TAQS DJAZAIRI 🌾🇩🇿  
**التقويم الفلاحي الجزائري + دردشة الذكاء الاصطناعي**  
**Algerian Farming Calendar + AI Chat**  

![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📘 وصف المشروع — Overview  

**الطاقس الجزائري** هو تطبيق ويب يجمع بين **التقويم الفلاحي التقليدي الجزائري** (الليالي، الوسم، مواسم الغرس، الإشارات الطبيعية) و**دردشة ذكاء اصطناعي** متخصصة في التراث الفلاحي والطقس الشعبي.  
يهدف التطبيق إلى حفظ ونقل المعرفة الفلاحية القديمة للأجيال الجديدة، مع إمكانية التفاعل وسؤال خبير افتراضي بالدارجة الجزائرية.

**TAQS DJAZAIRI** is a web application that combines the **Algerian traditional farming calendar** (Layali, Waseem, planting seasons, natural signs) with an **AI chat** specialized in agricultural heritage and folk weather wisdom.  
It aims to preserve and transmit ancient farming knowledge to new generations, with the ability to interact and ask a virtual expert in Algerian Darija.

---

## 🇩🇿 القسم العربي — Arabic Section  

### ✨ الميزات  
- 📅 **التقويم الفلاحي الجزائري** الكامل: الأشهر، الليالي البيض والسود والعجوز، مواسم الغرس.  
- 🌦️ **إشارات الطقس** التقليدية: سلوك الحيوانات، النجوم، الرياح.  
- 📖 **معجم الدارجة** لمصطلحات الطقس والفلاحة.  
- 🤖 **دردشة ذكاء اصطناعي** (Claude, DeepSeek, أو Ollama محلياً) تجيب عن أسئلتك بالعربية والدارجة.  
- 🌙 **واجهة مستخدم** ليلية مستوحاة من تراث الجزائر.  
- 🔌 **عمل دون إنترنت** للمحتوى الثابت، والذكاء الاصطناعي عبر الإنترنت.

### 🛠️ المتطلبات  
- Python 3.6 أو أحدث  
- (اختياري) مفتاح API من Anthropic أو DeepSeek، أو تثبيت Ollama محلياً.

### ⚙️ التثبيت والإعداد  

1. **استنساخ المستودع**  
   ```bash
   git clone https://github.com/swordenkisk/taqs-djazairi.git
   cd taqs-djazairi
```

1. إنشاء بيئة افتراضية (اختياري)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate      # Windows
   ```
2. تثبيت المكتبات المطلوبة
   ```bash
   pip install flask
   ```
   (التطبيق لا يحتاج إلا Flask؛ باقي المكتبات من Python القياسي)
3. إعداد ملف البيئة
      انسخ نموذج .env.example إلى .env وعدّل القيم:
   ```bash
   cp .env.example .env
   ```
   ثم افتح .env وأضف المفاتيح المطلوبة حسب المزود الذي تختاره:
   ```
   # اختر المزود: anthropic, deepseek, ollama
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=your_key_here
   # أو DEEPSEEK_API_KEY=...
   # OLLAMA_URL=http://localhost:11434
   # OLLAMA_MODEL=mistral
   ```

▶️ التشغيل

```bash
python taqs_djazairi.py
```

سيفتح المتصفح تلقائياً على http://localhost:5001.
للإيقاف: Ctrl+C.

🧠 استخدام الدردشة

· انتقل إلى تبويب اسأل AI.
· اكتب سؤالك بالعربية أو الدارجة (مثلاً: "متى نغرس الزيتون؟"، "قصة الليالي البيض").
· اضغط على زر الإرسال أو استخدم Ctrl+Enter.
· يمكنك اختيار الأسئلة السريعة المقترحة.

📚 محتوى التقويم

· الأشهر الـ12: لكل شهر وصفه، طقسه، أعماله، أمثاله، وشعر شعبي.
· الليالي: البيض، السود، العجوز، الوسم — مع أيامها، إشاراتها، وأشعارها.
· الغرس: مواعيد زراعة القمح، الزيتون، الفول، الطماطم، العنب...
· الإشارات: أكثر من 30 علامة طبيعية لتوقع الطقس.
· النجوم: الثريا، الجوزاء، سهيل، العقرب في التراث الجزائري.

🤝 المساهمة

نرحب بالمساهمات! إذا كنت تعرف أمثالاً أو إشارات إضافية، أضفها في ملف taqs_djazairi.py ضمن قواميس KB.

📄 الترخيص

هذا المشروع مرخص تحت MIT License.

---

🇬🇧 English Section

✨ Features

· 📅 Complete Algerian farming calendar: months, Layali (White, Black, Old Woman), planting seasons.
· 🌦️ Traditional weather signs: animal behavior, stars, winds.
· 📖 Darija glossary of weather and farming terms.
· 🤖 AI chat (Claude, DeepSeek, or local Ollama) answering your questions in Arabic/Darija.
· 🌙 Night‑themed UI inspired by Algerian heritage.
· 🔌 Offline‑first for static content; AI requires internet.

🛠️ Requirements

· Python 3.6+
· (Optional) API key from Anthropic or DeepSeek, or a local Ollama installation.

⚙️ Installation & Setup

1. Clone the repository
   ```bash
   git clone https://github.com/swordenkisk/taqs-djazairi.git
   cd taqs-djazairi
   ```
2. Create a virtual environment (optional)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate      # Windows
   ```
3. Install Flask (the only external dependency)
   ```bash
   pip install flask
   ```
4. Set up the environment file
      Copy .env.example to .env and edit it:
   ```bash
   cp .env.example .env
   ```
   Then open .env and add your keys/configuration:
   ```
   # Choose provider: anthropic, deepseek, ollama
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=your_key_here
   # or DEEPSEEK_API_KEY=...
   # OLLAMA_URL=http://localhost:11434
   # OLLAMA_MODEL=mistral
   ```

▶️ Running

```bash
python taqs_djazairi.py
```

Your browser will automatically open http://localhost:5001.
To stop: Ctrl+C.

🧠 Using the Chat

· Go to the Ask AI tab.
· Type your question in Arabic or Darija (e.g., "When to plant olives?", "Story of the White Nights").
· Click send or use Ctrl+Enter.
· Quick questions are provided for convenience.

📚 Calendar Content

· 12 months: each with description, weather, farming tasks, proverbs, and folk poetry.
· Layali: White, Black, Old Woman, Waseem — including dates, signs, and poems.
· Planting: schedules for wheat, olives, fava beans, tomatoes, grapes...
· Signs: over 30 natural indicators for weather prediction.
· Stars: Pleiades, Orion, Canopus, Scorpius in Algerian tradition.

🤝 Contributing

Contributions are welcome! If you know additional proverbs or signs, add them in taqs_djazairi.py inside the KB dictionaries.

📄 License

This project is licensed under the MIT License.
