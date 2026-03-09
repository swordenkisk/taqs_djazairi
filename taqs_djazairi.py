#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
الطاقس الجزائري — TAQS DJAZAIRI
التقويم الفلاحي الجزائري + دردشة ذكاء اصطناعي
────────────────────────────────────────────
cp .env.example .env  ← أضف مفتاح AI
python taqs_djazairi.py
افتح: http://localhost:5001
"""

import os, json, sys, threading, time, urllib.request, urllib.error, subprocess
from datetime import datetime, date
from flask import Flask, render_template_string, jsonify, request

# ── .env ──────────────────────────────────────────────────────────
def load_env():
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        for line in open(env_file, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
load_env()

AI_PROVIDER   = os.getenv("AI_PROVIDER",   "anthropic")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEEPSEEK_KEY  = os.getenv("DEEPSEEK_API_KEY",  "")
OLLAMA_URL    = os.getenv("OLLAMA_URL",    "http://localhost:11434")
OLLAMA_MODEL  = os.getenv("OLLAMA_MODEL",  "mistral")

# ── AI System prompt ──────────────────────────────────────────────
AI_SYSTEM = """أنت خبير في التقاليد الفلاحية الجزائرية والتقويم الشعبي الأمازيغي القديم.
تعرف جيداً:
- الليالي البيض (13-26 يناير) والليالي السود وليالي العجوز (آخر فبراير)
- الوسم: أول مطر الخريف، أكتوبر-نوفمبر
- مواعيد الغرس: القمح، الزيتون، الفول، الطماطم، العنب
- الأنواء والنجوم: الثريا، الجوزاء، سهيل، العقرب
- الإشارات الطبيعية: النمل، الضفادع، الدخان، القطط...
- الكلمات الدارجة: الصقعة، الشيبة، الشهيلية، القيظ، الوسم، الغيثة، الرعدة

تتحدث بالعربية والدارجة الجزائرية. تستشهد بالأمثال الجزائرية الحقيقية.
أجب بوضوح لا يتجاوز 120 كلمة. لا تستخدم ماركداون."""

# ── AI caller ─────────────────────────────────────────────────────
def call_ai(history: list, question: str) -> str:
    messages = history + [{"role": "user", "content": question}]
    p = AI_PROVIDER.lower()
    try:
        if p == "anthropic":
            if not ANTHROPIC_KEY:
                return "⚠️ أضف ANTHROPIC_API_KEY في .env"
            body = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 500,
                "system": AI_SYSTEM,
                "messages": messages,
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages", data=body,
                headers={"Content-Type": "application/json",
                         "x-api-key": ANTHROPIC_KEY,
                         "anthropic-version": "2023-06-01"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())["content"][0]["text"].strip()

        elif p == "deepseek":
            if not DEEPSEEK_KEY:
                return "⚠️ أضف DEEPSEEK_API_KEY في .env"
            body = json.dumps({
                "model": "deepseek-chat", "max_tokens": 500,
                "messages": [{"role": "system", "content": AI_SYSTEM}] + messages,
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.deepseek.com/v1/chat/completions", data=body,
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer {DEEPSEEK_KEY}"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())["choices"][0]["message"]["content"].strip()

        elif p == "ollama":
            body = json.dumps({
                "model": OLLAMA_MODEL, "stream": False,
                "messages": [{"role": "system", "content": AI_SYSTEM}] + messages,
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{OLLAMA_URL}/api/chat", data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())["message"]["content"].strip()

        else:
            return f"⚠️ مزود غير معروف: {p}"

    except urllib.error.HTTPError as e:
        err = e.read().decode()[:300]
        return f"⚠️ خطأ {e.code}: {err}"
    except Exception as e:
        return f"⚠️ {str(e)}"


# ════════════════════════════════════════════════════════════════════
#  قاعدة المعرفة المدمجة
# ════════════════════════════════════════════════════════════════════
KB = {
  "layali": [
    {
      "name": "الليالي البيض", "darija": "لْيَالِي الْبِيضْ", "icon": "❄️",
      "period": "13 — 26 يناير",
      "gs": (1,13), "ge": (1,26),
      "desc": "ثلاث عشرة ليلة من الصقيع القاسي. الأرض تبيض بالجليد والبرد يتجمد فيه الماء في السواقي. الفلاح لا يغرس ولا يحرث.",
      "farming": "ممنوع الغرس — الجذور الحديثة تموت من الصقيع",
      "signs": ["الضفادع تصمت","النجوم تلمع بشكل مفرط","الدخان يصعد مستقيماً","الكلاب تنام داخل البيوت"],
      "sayings": ["«لْيَالِي الْبِيضْ مَا تْغَرْسْ فِيهَا وَلاَ تِحْرَثْ»","«كِي تْجِي الْبِيضْ دِيرْ رُوحَكْ فِي الدَّارْ»"],
      "poem": "يَا لَيْلَةَ الْبَيْضَاءِ مَا أَشَدَّ قُرَّكِ\nوَالْجَبَلُ الشَّامِخُ يَرْتَجِفُ مِنْ بَرْدِكِ\nوَالنَّارُ مَا تَكْفِيكِ وَالصُّوفُ مَا يَدْفِيكِ\nيَا بِنْتَ يَنَّايِرْ خَلِّي الْفَلاَّحْ يِبْكِي",
      "src": "من شعر الأوراس القديم"
    },
    {
      "name": "الليالي السود", "darija": "لْيَالِي السُّودْ", "icon": "🌧️",
      "period": "1 — 12 يناير",
      "gs": (1,1), "ge": (1,12),
      "desc": "أيام يناير الأولى، باردة مع أمطار غزيرة. السماء مغطاة بالغيوم فسُمّيت سوداء. الأرض ترتوي والفلاح يستعد للحرث.",
      "farming": "وقت جيد للحرث وتهيئة التربة — المطر يليّن الأرض",
      "signs": ["الغيوم تغطي القمر","المطر متقطع","الأودية تجري","الطيور المهاجرة تعود"],
      "sayings": ["«السُّودْ جَابَتْ الْخَيْرْ لِلْوَادْ»","«إِذَا مْطَرَتْ السُّودْ، الرَّبِيعْ مَضْمُونْ»"],
      "poem": "يَا لَيَالِي السُّودْ يَا أُمَّ الْخَيْرَاتْ\nتِجِي بِالْمَطَرْ وَتِجِي بِالْبَرَكَاتْ\nالْفَلاَّحْ يِفْرَحْ وَيِقُولْ الصَّلَوَاتْ\nعَلَى اللِّي جَابَتْ سَوَادِكِ يَا اللَّيْلاَتْ",
      "src": "من الموروث الشفهي القبائلي"
    },
    {
      "name": "ليالي العجوز", "darija": "لْيَالِي الْعَجُّوزْ", "icon": "👵",
      "period": "آخر فبراير — أول مارس (7 أيام)",
      "gs": (2,24), "ge": (3,3),
      "desc": "سبعة أيام من البرد المتأخر. الأسطورة: عجوز خرجت بغنمها ظنّاً أن الشتاء انتهى، فعاقبها الشهر بسبع ليالٍ قارسة. تنبيه: الجو الدافئ خادع!",
      "farming": "خطر — لا تغرس الخضار الحساسة، البرد العائد يقتلها",
      "signs": ["الجو يدفأ فجأة ثم يبرد","الرياح الشمالية تعود","اللوز المزهر يتساقط","الكلاب القديمة تقترب من النار"],
      "sayings": ["«الْعَجُّوزْ سَبْعَةْ وَلاَ تِغَرَّشْ بِيهَا»","«فِبْرَايِرْ فِبْرَايِرْ كِي يِدْفَا يِقَرَّسْ»","«الدِّيبَةْ مَا تِثَقْ فِي فِبْرَايِرْ»"],
      "poem": "جَاءَتْ الْعَجُوزُ فِي آخِرِ الشِّتَاءِ\nتَقُولُ الرَّبِيعُ جَاءَ وَالدِّفَاءُ\nفَخَرَجَتْ بِأَغْنَامِهَا فِي الصَّبَاحِ\nوَعَادَتْ بَاكِيَةً تَنْدُبُ الرِّيَاحَ",
      "src": "مثل شعري منتشر في الشمال الجزائري"
    },
    {
      "name": "الوسم — أول مطر الخريف", "darija": "الْوَسْمْ", "icon": "🌧️",
      "period": "أكتوبر — نوفمبر",
      "gs": (10,1), "ge": (11,30),
      "desc": "الوسم هو أول أمطار الخريف. كلمة «وسم» من التوسيم أي العلامة — علامة بدء الموسم الزراعي. الأرض تفتح وتقبل البذور. المزارع يبدأ الحرث فوراً.",
      "farming": "أفضل وقت للحرث وبذر القمح والشعير — الأرض في أفضل حالاتها",
      "signs": ["رائحة التراب المبتل (البيتريكور)","الضفادع تعود وتصرخ","النمل يبني بالقرب من المسالك"],
      "sayings": ["«جَا الْوَسْمْ، يَلاَّهْ لِلْحَرَثْ»","«اللِّي مَا حَرَثْ فِي الوَسْمْ بَكَى فِي الصَّيْفْ»","«مَطَرْ الوَسْمْ يَكْفِيكْ مَطَرَيْنْ»"],
      "poem": "يَا وَسْمَنَا يَا وَسَمْ يَا بْرَكَةْ اللهِ\nجَيْتَ وِالْأَرْضْ تَاقَتْ لِيكْ يَا الإِلَهِ\nيَا مَطَرْ الْخَيْرْ سَقِّي جِنَانِي\nوَحَيِّيَ الزَّرَعْ فِي كُلِّ مَكَانِ",
      "src": "من أغاني الحصاد — سهل متيجة"
    }
  ],
  "months": [
    {"n":1,"ar":"يناير","dz":"يَنَّايِرْ","amz":"ⵢⵏⵏⴰⵢⵔ","icon":"❄️","season":"شتاء","nick":"شهر الصقيع والليالي البيض",
     "weather":"بارد جداً، صقيع، ثلوج في الجبال","farming":"راحة تامة. حرث أراضي عميقة. تقليم أشجار.",
     "words":["الصَّقْعَةْ","الثَّلَجْ","الشِّيبَةْ","الجَّلِيدْ"],
     "saying":"«يَنَّايِرْ إِذَا دَفَا، وَيْلاَكَ»",
     "poem":"يَنَّايِرْ يَا بَارَدْ\nالأَرْضُ مِنْكَ تَكَادُ تَمُوتُ\nلَكِنَّكَ تَسْقِي جُذُورَهَا\nمَا لاَ يَسْقِيهِ الصَّيْفُ"},
    {"n":2,"ar":"فبراير","dz":"فِبْرَايِرْ","amz":"ⴼⴱⵔⴰⵢⵔ","icon":"🌬️","season":"شتاء-ربيع","nick":"الشهر الخادع — العجوز في نهايته",
     "weather":"متقلب جداً، دفء زائف يعقبه برد شديد","farming":"تهيئة الأرض. حذر من العجوز آخر الشهر.",
     "words":["الرِّيحْ","الدِّفَا الْكَاذِبْ","الضَّبَابْ","الغَيْمَةْ"],
     "saying":"«فِبْرَايِرْ كَذَّابْ، إِذَا صَحَا رَاهْ يَضْرَبْ»",
     "poem":"فِبْرَايِرْ يِضْحَكْ فِي النَّهَارْ\nوَيِبْكِي فِي اللِّيلْ مِنَ الشِّتَا\nلاَ تِوْثَقْ بِدِفَاهُ يَا فَلاَّحْ\nالْعَجُّوزْ بَعْدُهُ تِيجِيكْ بِالْبَلاَ"},
    {"n":3,"ar":"مارس","dz":"مَارِسْ","amz":"ⵎⴰⵔⵙ","icon":"🌱","season":"ربيع","nick":"مارس الغاضب — امحمرش",
     "weather":"رياح قوية، أمطار متقطعة، دفء تدريجي","farming":"غرس ربيعي، تقليم الكرمة، بذر البطاطا.",
     "words":["الرِّيحْ الشَّرْقِيَّةْ","الزَّهْرَةْ","الطِّينْ","الرَّبِيعْ"],
     "saying":"«مَارِسْ امحمرش، مَا يِرْحَمْشْ لاَ الشَّيْخْ وَلاَ الشَّبَابْ»",
     "poem":"مَارِسْ يَجِيءُ بِالرِّيَاحِ وَالأَمَلْ\nيُوقِظُ الأَرْضَ مِنْ نَوْمِهَا الطَّوِيلْ\nوَالشَّجَرُ يَلْبَسُ ثَوْبَهُ الأَخْضَرْ\nوَالْفَلاَّحُ يَنْتَظِرُ الْخَيْرَ الْجَزِيلْ"},
    {"n":4,"ar":"أبريل","dz":"نِيسَانْ","amz":"ⵉⴱⵔⵉⵔ","icon":"🌸","season":"ربيع","nick":"شهر الأمطار والإزهار",
     "weather":"أمطار غزيرة وعواصف. هواء دافئ. أجمل أشهر السنة.","farming":"غرس الخضار الصيفية. اعتناء بالأشجار.",
     "words":["الرَّبِيعْ","الزَّهَارِيفْ","الأَزْهَارْ","الشَّبُّوطْ"],
     "saying":"«نِيسَانْ شَهْرْ الأَمَلْ وَالأَلْوَانْ»",
     "poem":"نِيسَانْ يَا مَلَكَ الزَّهَارِيفْ\nوَالأَرْضُ تِفْرَحْ بِكَ يَا نِيسَانْ\nكُلّ شَيْءٍ يِتْجَدَّدْ فِيكَ وَيِحْيَا\nيَا شَهْرَ الأَمَلْ وَالأَلْوَانْ"},
    {"n":5,"ar":"ماي","dz":"مَايُوا","amz":"ⵎⴰⵢⵢⵓ","icon":"🌻","season":"ربيع-صيف","nick":"شهر الحصاد الأول",
     "weather":"دافئ مشمس. حرارة ترتفع تدريجياً.","farming":"حصاد الفول والحمص. عناية بالقمح.",
     "words":["الدِّفَا","الشَّمْسْ","الحَصَادَةْ","الهَوَا العْلِيلْ"],
     "saying":"«مَايُوا شَهْرْ النَّعَاسْ وَالحَصَادْ»",
     "poem":"مَايُوا يَجِيبْ الدِّفَا وَالزَّهَرْ\nوَالنَّحْلَةْ تِدُورْ عَلَى الزَّهَرْ\nوَالأَرْضُ تِهِبْ مِنْ خَيْرِهَا الوَافِرْ\nشَهْرُ النِّعْمَةِ وَالرِّزْقِ الأَخْضَرْ"},
    {"n":6,"ar":"يونيو","dz":"جُوَانْ","amz":"ⵢⵓⵏⵢⵓ","icon":"☀️","season":"صيف","nick":"بداية القيظ والجفاف",
     "weather":"حر متصاعد. رياح جنوبية حارة (الشهيلية). جفاف يبدأ.","farming":"حصاد القمح والشعير. ري مكثف.",
     "words":["القَيْظْ","الشَّهِيلِيَّةْ","الغَرْبِيَّةْ","السِّيرُوكُو"],
     "saying":"«جُوَانْ بِلاَ مَا، وَيْلاَكَ مِنَ الحَرَّارَةْ»",
     "poem":"جُوَانْ وَالشَّمْسُ تَحْرُقُ بِلاَ رَحْمَةْ\nوَالأَرْضُ تَتَشَقَّقُ مِنَ الْعَطَشْ\nوَالْفَلاَّحُ يَحْصُدُ بِعَرَقِهِ وَدَمِهِ\nشُكْراً لِلأَرْضِ الصَّبُورَةِ الَّتِي لاَ تَنَشْ"},
    {"n":7,"ar":"يوليو","dz":"جُوِيَّلْيِيهْ","amz":"ⵢⵓⵍⵢⵓⵣ","icon":"🔥","season":"صيف","nick":"ذروة الحر والقيظ",
     "weather":"الأشد حرارة. الشهيلية تضرب لأيام. جفاف تام.","farming":"الري فقط. حصاد الطماطم والبطيخ.",
     "words":["الحَرَّاقَةْ","القَيْظَةْ","البَحَرْ يِوَلِّي أَزْرَقْ","الهَجِيرَةْ"],
     "saying":"«جُوِيَّلْيِيهْ، الحَجَرْ يِمِيعْ»",
     "poem":"يُولْيُوزُ يُشْعِلُ النَّارَ فِي السَّمَاءِ\nوَالظِّلُّ أَصْبَحَ أَثْمَنَ مِنَ الْمَاءِ\nتَخْتَبِئُ الْغَنَمُ وَالطَّيْرُ وَالنَّاسُ\nوَالأَرْضُ تَنْتَظِرُ شَمَّةَ الْهَوَاءِ"},
    {"n":8,"ar":"أغسطس","dz":"غُشْتْ","amz":"ⵖⵓⵛⵜ","icon":"🍇","season":"صيف","nick":"غشت المبارك — شهر العنب",
     "weather":"حار لكن يبدأ التخفيف. عواصف رعدية مفاجئة.","farming":"جمع العنب والتين. تجفيف الفواكه.",
     "words":["الصَّيْفِيَّةْ","الرَّعْدَةْ","غُشْتُو مُبَارَكْ","الزَّبُولَةْ"],
     "saying":"«غُشْتْ شَهْرْ التِّينَةْ وَالعِنَبْ»",
     "poem":"غُشْتُ يَأْتِي بِالثِّمَارِ الطَّيِّبَةِ\nوَيُبَشِّرُ بِانْتِهَاءِ الصَّيْفِ الشَّدِيدِ\nالتِّينَةُ تَتَدَلَّى وَالْعِنَبُ يَحْلُو\nوَالْأَرْضُ تَسْتَعِدُّ لِمَوْسِمٍ جَدِيدِ"},
    {"n":9,"ar":"سبتمبر","dz":"شُتَنْبِرْ","amz":"ⵛⵓⵜⴰⵏⴱⵉⵔ","icon":"🍂","season":"خريف","nick":"إيلول — شهر الفول والتهيئة",
     "weather":"اعتدال ممتاز. الليالي تبرد. أمطار خفيفة تبدأ.","farming":"حرث الأراضي. بذر الفول والحمص. جمع الزيتون.",
     "words":["الخْرِيفْ","الطَّلّ","الهَوَا العْلِيلْ","الوَسْمُ يِقْرَبْ"],
     "saying":"«إِيلُولْ شَهْرْ الفُولْ وَتِهْيِيَةْ الأَصُولْ»",
     "poem":"شُتَنْبِرُ يَجِيءُ وَالنَّسِيمُ يُبَشِّرُ\nبِأَنَّ الصَّيْفَ وَلَّى وَالشِّتَاءُ يَنْتَظِرُ\nالأَرْضُ تَشْتَاقُ لِلْمَطَرِ وَالْحَرْثِ\nوَالْفَلاَّحُ يُشَمِّرُ لِلْبَذَارِ يُحَضِّرُ"},
    {"n":10,"ar":"أكتوبر","dz":"أُكْتُوبِرْ","amz":"ⴽⵟⵓⴱⵔ","icon":"🌧️","season":"خريف","nick":"تشرين — شهر الوسم الكبير",
     "weather":"أمطار الوسم تبدأ. برودة ليلية. الجو مثالي للزراعة.","farming":"الحرث الكبير. بذر القمح والشعير. غرس الأشجار.",
     "words":["الوَسْمْ","الطِّينْ","وَقْتْ الحَرْثْ","الغَيْثَةْ"],
     "saying":"«اللِّي مَا حَرَثْ فِي الوَسْمْ بَكَى فِي الصَّيْفْ»",
     "poem":"تِشِيرِينُ يَفْتَحُ بَابَ السَّمَاءِ\nوَيَسْقِي الأَرْضَ الظَّامِئَةَ الصَّبُورَةَ\nيَا وَسْمَنَا يَا بَرَكَةَ اللهِ\nجِئْتَ فِي وَقْتِكَ يَا أَكْرَمَ الدُّورَةِ"},
    {"n":11,"ar":"نوفمبر","dz":"نُوفَنْبِرْ","amz":"ⵏⵓⵡⴰⵏⴱⵉⵔ","icon":"🌱","season":"خريف-شتاء","nick":"شهر الغرس الكبير",
     "weather":"برد يتصاعد. أمطار منتظمة. أول صقيع في الجبال.","farming":"غرس الشتلات. بذر القمح. جمع الزيتون.",
     "words":["البَرْدْ","الضَّبَابْ","الغَرْسَةْ","الشِّتَاءُ يِقْرَبْ"],
     "saying":"«نُوفَنْبِرْ شَهْرْ الشِّتَلاَتْ وَالزَّرَعْ»",
     "poem":"نُوفَنْبِرُ الصَّادِقُ يَأْتِي بِالْبَرَكَةِ\nوَالْأَرْضُ تَفْتَحُ حِضْنَهَا لِلْبَذَارِ\nاغْرِسْ وَابْذُرْ وَلاَ تَتَكَاسَلْ\nمَا زَرَعْتَ الْيَوْمَ تَجْنِيهِ فِي النَّهَارِ"},
    {"n":12,"ar":"ديسمبر","dz":"دِيسَنْبِرْ","amz":"ⴷⵓⵊⴰⵏⴱⵉⵔ","icon":"🌨️","season":"شتاء","nick":"كانون — البرد الحقيقي",
     "weather":"البرد الشديد. ثلوج في الجبال. أمطار غزيرة.","farming":"راحة للأرض. صيانة الأدوات. تخطيط الموسم.",
     "words":["كَانُونْ","الصَّقِيعْ","القَرَّاقَةْ","الجَّلِيدُ يِحْرَقْ"],
     "saying":"«كَانُونْ يِقْطَعْ الزِّيتُونَةْ بِالْبَرْدْ»",
     "poem":"كَانُونُ يَجِيءُ وَالثَّلْجُ يُلَبِّسُ الجَّبَلْ\nوَالنَّارُ فِي الدَّارِ تَجْمَعُ الأَهْلَ وَالعِيَالْ\nيَا شَهْرَ الصَّبْرِ وَالطُّولِ وَالأَمَلِ\nبَعْدَكَ يَجِيءُ الرَّبِيعُ وَيُزِيلُ الثِّقَالْ"},
  ],
  "lexicon": [
    {"w":"الصَّقْعَةْ",    "m":"الصقيع الشديد — Black frost",           "s":"شتاء"},
    {"w":"الشِّيبَةْ",    "m":"الجليد الناعم على الأرض — Hoarfrost",   "s":"شتاء"},
    {"w":"الشِّتِيوَةْ",  "m":"المطر الغزير المتواصل — Heavy rain",     "s":"شتاء"},
    {"w":"الغَبَارَةْ",   "m":"عاصفة رملية — Sandstorm",               "s":"صيف"},
    {"w":"الشَّهِيلِيَّةْ","m":"ريح السيروكو الحارة — Sirocco",        "s":"صيف"},
    {"w":"القَيْظْ",      "m":"حر الصيف الشديد — Scorching heat",      "s":"صيف"},
    {"w":"الدِّفَا",      "m":"الدفء اللطيف — Pleasant warmth",         "s":"ربيع"},
    {"w":"الطَّلّ",       "m":"الندى الصباحي — Morning dew",            "s":"ربيع"},
    {"w":"الغَيْثَةْ",    "m":"المطر المبارك — Blessed rain",           "s":"خريف"},
    {"w":"الوَسْمْ",      "m":"أول مطر الخريف — First autumn rain",    "s":"خريف"},
    {"w":"الزَّبُولَةْ",  "m":"ضربة برق — Lightning strike",            "s":"خريف"},
    {"w":"الرَّعْدَةْ",   "m":"العاصفة الرعدية — Thunderstorm",         "s":"خريف"},
    {"w":"الضَّبَابْ",    "m":"الضباب الكثيف — Dense fog",              "s":"شتاء"},
    {"w":"الحَلِيبِيَّةْ","m":"غيوم بيضاء بلا مطر — Dry white clouds", "s":"صيف"},
    {"w":"الشَّلُّوفَةْ",  "m":"ريح شمالية باردة — Cold north wind",   "s":"شتاء"},
    {"w":"الغَرْبِيَّةْ",  "m":"الريح الغربية الرطبة — Wet west wind", "s":"شتاء"},
    {"w":"البُخَارَةْ",    "m":"الرطوبة — Humidity",                    "s":"صيف"},
    {"w":"المَطَرْ الذَّهَبِيّ","m":"مطر خفيف مع شمس — Sun shower",  "s":"ربيع"},
  ],
  "signs": [
    {"s":"النمل يبني خطوطاً عالية",    "m":"مطر قادم خلال 24-48 ساعة",    "i":"🐜"},
    {"s":"الضفادع تصرخ بكثرة",         "m":"مطر وشيك",                    "i":"🐸"},
    {"s":"الكلاب تأكل العشب",          "m":"تغير الطقس قادم",             "i":"🐕"},
    {"s":"البقر تلطم بذيلها",           "m":"اقتراب عاصفة",               "i":"🐄"},
    {"s":"الطيور تطير منخفضة",         "m":"ضغط جوي منخفض، مطر قريب",   "i":"🐦"},
    {"s":"القطط تنام مجمعة",            "m":"برد شديد قادم",               "i":"🐱"},
    {"s":"الدخان ينزل للأسفل",         "m":"ضغط منخفض، مطر محتمل",       "i":"💨"},
    {"s":"الدخان يصعد مستقيماً",       "m":"جو مستقر وصافٍ",             "i":"🌟"},
    {"s":"النجوم تتلألأ بشدة",         "m":"برد شديد الليلة",             "i":"⭐"},
    {"s":"الشمس تغرب حمراء",          "m":"غد صافٍ وجاف",               "i":"🌅"},
    {"s":"الشمس تطلع حمراء",          "m":"مطر أو رياح قوية قادمة",     "i":"🌄"},
    {"s":"هالة حول القمر",             "m":"مطر خلال 48 ساعة",           "i":"🌙"},
    {"s":"رائحة التراب القوية",         "m":"مطر بعد جفاف طويل",          "i":"🌍"},
    {"s":"النحل يعود مبكراً للخلية",   "m":"عاصفة قادمة",                "i":"🐝"},
    {"s":"رائحة الزعتر تشتد",          "m":"جو جاف وحار",                "i":"🌿"},
    {"s":"تورم أبواب الخشب",           "m":"رطوبة عالية، مطر قادم",      "i":"🚪"},
  ],
  "ghars": [
    {"c":"القمح والشعير","dz":"القَمْح والشَّعِير","i":"🌾","m":[11,12,1],
     "p":"نوفمبر — يناير","desc":"يُغرس بعد أول أمطار الوسم. «زرع في الوحل، اقلع في الرمل»",
     "says":["«زَرَعْ فِي الْوَحَلْ، اقْلَعْ فِي الرَّمَلْ»","«الْقَمْحَةْ تِعِيشْ فِي الطِّينْ»"]},
    {"c":"الزيتون","dz":"الزِّيتُونْ","i":"🫒","m":[11,12,1,3],
     "p":"نوفمبر — مارس","desc":"شجرة الجزائر. الجمع عند تحول الثمار للبنفسجي. «الزيتونة للأحفاد».",
     "says":["«الزِّيتُونَةْ لِلأَحْفَادْ»","«اغْرِسْ وَلَوْ عَلَى حَافَةِ الدَّارْ»"]},
    {"c":"الفول والحمص","dz":"الفُولْ والحُمُّصْ","i":"🫘","m":[11,12,1,2],
     "p":"نوفمبر — فبراير","desc":"«إيلول شهر الفول». يُزرع شتاءً ويُحصد ربيعاً.",
     "says":["«إِيلُولْ شَهْرْ الْفُولْ»","«الْفُولَةْ الشِّتَوِيَّةْ أَحْلَى»"]},
    {"c":"الخوخ والمشمش","dz":"الخُوخْ والمِيشْمَاشْ","i":"🍑","m":[3,4],
     "p":"مارس — أبريل","desc":"تزهر في مارس. خطر العجوز يهدد الأزهار. الفلاح يغطي الأشجار الصغيرة.",
     "says":["«الخُوخَةْ تِزْهَرْ فِي مَارِسْ وَتِتَعَذَّبْ مِنَ الْعَجُّوزْ»"]},
    {"c":"الطماطم والفلفل","dz":"الطُّمَاطِمْ والفْلِيفْلَةْ","i":"🍅","m":[4,5],
     "p":"أبريل — ماي","desc":"خضار الصيف. تُغرس بعد ثبات الحرارة وزوال الليالي الباردة.",
     "says":["«الطُّمَاطِمْ مَا تِحِبْشْ الْبَرْدْ»","«اغْرِسْ الْخُضَارَةْ بَعْدَ نِيسَانْ»"]},
    {"c":"العنب والتين","dz":"الْعِنَبْ والتِّينَةْ","i":"🍇","m":[8,9],
     "p":"أغسطس — سبتمبر","desc":"شهر سبتمبر هو شهر العنب. التينة تُجفَّف للشتاء.",
     "says":["«شُتَنْبِرْ يِخَلِّيكْ تِبِيتْ بِالتِّينَةْ»","«يَا تِينَةْ يَا مُبَارَكَةْ»"]},
  ],
  "nujum": [
    {"n":"الثُّرَيَّا","i":"✨","p":"مايو-يونيو","m":"غيابها في الغرب عند الغروب يعني انتهاء المطر وبداية الصيف","say":"«كِي تِغِيبْ الثُّرَيَّا، خَلِّ الكِسَا عَلَى الشَّيَّا»"},
    {"n":"الجَوْزَاءُ","i":"⚔️","p":"ديسمبر-يناير","m":"ظهور الجوزاء علامة ذروة البرد. الفلاح يستعد للليالي البيض","say":"«كِي تِطْلَعْ الجَوْزَا، الرَّاعِيَّةْ تِخَبَّا»"},
    {"n":"سُهَيْلُ","i":"💫","p":"أغسطس-سبتمبر","m":"طلوع سهيل يعني كسر حدة الصيف وبداية اعتدال الجو","say":"«طَلَعْ سُهَيْلْ، وَتَرَدَّا بِالكَيْلْ»"},
    {"n":"العَقْرَبُ","i":"🦂","p":"يونيو-يوليو","m":"ظهور العقرب يوافق ذروة الحر وموسم الشهيلية","say":"«كِي تِطْلَعْ العَقْرَبْ، الشَّمْسْ تَلْعَبْ بِالرِّقَابْ»"},
  ]
}

# ── Helpers ───────────────────────────────────────────────────────
def cur_month():
    m = datetime.now().month
    return next((x for x in KB["months"] if x["n"]==m), KB["months"][0])

def active_layali():
    t = date.today()
    out = []
    for ly in KB["layali"]:
        ms,ds = ly["gs"]; me,de = ly["ge"]
        try:
            s = date(t.year,ms,ds); e = date(t.year,me,de)
            if s<=t<=e: out.append(ly)
        except: pass
    return out

def cur_crops():
    m = datetime.now().month
    return [g for g in KB["ghars"] if m in g["m"]]

# ════════════════════════════════════════════════════════════════════
#  FLASK APP
# ════════════════════════════════════════════════════════════════════
app = Flask(__name__)

@app.route("/")
def index(): return render_template_string(HTML)

@app.route("/api/today")
def api_today():
    return jsonify({"month":cur_month(),"layali":active_layali(),"crops":cur_crops()})

@app.route("/api/kb")
def api_kb(): return jsonify(KB)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    q    = data.get("question","").strip()
    hist = data.get("history", [])
    if not q:
        return jsonify({"error":"سؤال فارغ"}), 400
    answer = call_ai(hist, q)
    return jsonify({"answer": answer, "provider": AI_PROVIDER})

@app.route("/api/status")
def api_status():
    return jsonify({
        "provider": AI_PROVIDER,
        "has_key": bool(ANTHROPIC_KEY or DEEPSEEK_KEY or AI_PROVIDER=="ollama"),
        "model": {"anthropic":"claude-sonnet-4","deepseek":"deepseek-chat","ollama":OLLAMA_MODEL}.get(AI_PROVIDER,"?")
    })


# ════════════════════════════════════════════════════════════════════
#  HTML — واجهة كاملة مع دردشة الذكاء الاصطناعي
# ════════════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>الطاقس الجزائري</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Tajawal:wght@300;400;700;900&display=swap');
:root{
  --sand:#C9A96E;--gold:#E8B84B;--ochre:#B5762A;
  --deep:#0B0918;--night:#12102A;--ink:#1A1738;--purple:#2D1F5E;
  --cream:#F4E8C1;--terr:#8B3A2A;--mint:#2ECC71;--frost:#7FB3D3;--warm:#E67E22;
  --red:#E74C3C;--blue:#3498DB;
}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--deep);color:var(--cream);font-family:'Tajawal',sans-serif;min-height:100vh;overflow-x:hidden;}

/* Stars bg */
body::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(1px 1px at 8% 12%,rgba(255,255,255,.7) 0%,transparent 100%),
  radial-gradient(1px 1px at 22% 38%,rgba(255,255,255,.4) 0%,transparent 100%),
  radial-gradient(2px 2px at 38% 7%,rgba(255,255,255,.8) 0%,transparent 100%),
  radial-gradient(1px 1px at 55% 28%,rgba(255,255,255,.5) 0%,transparent 100%),
  radial-gradient(1px 1px at 72% 48%,rgba(255,255,255,.3) 0%,transparent 100%),
  radial-gradient(2px 2px at 88% 18%,rgba(255,255,255,.6) 0%,transparent 100%),
  radial-gradient(1px 1px at 14% 68%,rgba(232,184,75,.5) 0%,transparent 100%),
  radial-gradient(1px 1px at 91% 82%,rgba(255,255,255,.5) 0%,transparent 100%),
  radial-gradient(1px 1px at 44% 88%,rgba(255,255,255,.3) 0%,transparent 100%),
  radial-gradient(2px 2px at 3%  4%, rgba(255,255,255,.9) 0%,transparent 100%),
  var(--deep);}

.geo{background:repeating-linear-gradient(90deg,transparent 0,transparent 8px,var(--gold) 8px,var(--gold) 10px,transparent 10px,transparent 18px,var(--ochre) 18px,var(--ochre) 20px);height:4px;}

/* Header */
.hdr{position:relative;z-index:10;background:linear-gradient(180deg,rgba(11,9,24,.98),rgba(26,23,56,.9));border-bottom:1px solid rgba(232,184,75,.3);}
.hdr-inner{max-width:1300px;margin:0 auto;padding:22px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;}
.logo-ar{font-family:'Amiri',serif;font-size:38px;font-weight:700;color:var(--gold);text-shadow:0 0 30px rgba(232,184,75,.4);}
.logo-sub{font-size:11px;letter-spacing:4px;color:var(--sand);margin-top:2px;}
.logo-amz{font-size:15px;color:rgba(232,184,75,.35);margin-top:2px;}
.clock-box{text-align:center;}
.clk{font-size:26px;font-weight:700;color:var(--gold);font-family:monospace;}
.cdate{font-size:10px;color:var(--sand);margin-top:2px;}
.moon{font-size:32px;margin-top:4px;}
.month-badge{text-align:center;}
.mb-icon{font-size:44px;}
.mb-name{font-family:'Amiri',serif;font-size:17px;color:var(--gold);}
.mb-season{font-size:9px;letter-spacing:3px;color:var(--sand);margin-top:2px;}

/* AI badge */
.ai-badge{display:flex;align-items:center;gap:6px;padding:6px 14px;border:1px solid rgba(232,184,75,.3);background:rgba(29,24,56,.8);font-size:11px;letter-spacing:2px;}
.ai-dot{width:8px;height:8px;border-radius:50%;background:var(--mint);box-shadow:0 0 8px var(--mint);}
.ai-dot.warn{background:var(--warm);box-shadow:0 0 8px var(--warm);}

/* Nav */
.nav{display:flex;justify-content:center;gap:3px;flex-wrap:wrap;padding:14px 24px 0;max-width:1300px;margin:0 auto;}
.tab{padding:9px 18px;background:rgba(255,255,255,.04);border:1px solid rgba(232,184,75,.2);color:var(--sand);font-family:'Tajawal',sans-serif;font-size:13px;font-weight:700;cursor:pointer;transition:all .2s;}
.tab:hover{background:rgba(232,184,75,.1);border-color:var(--gold);color:var(--gold);}
.tab.on{background:rgba(232,184,75,.15);border-color:var(--gold);color:var(--gold);}

/* Main */
.main{position:relative;z-index:5;max-width:1300px;margin:0 auto;padding:22px 24px;}
.sec{display:none;animation:fi .3s ease;}
.sec.on{display:block;}
@keyframes fi{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* Section heading */
.sh{font-family:'Amiri',serif;font-size:26px;color:var(--gold);margin-bottom:18px;padding-bottom:10px;border-bottom:1px solid rgba(232,184,75,.2);}

/* Today grid */
.tgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:20px;}
@media(max-width:700px){.tgrid{grid-template-columns:1fr;}}
.tcard{background:linear-gradient(135deg,rgba(26,23,56,.95),rgba(45,31,94,.7));border:1px solid rgba(232,184,75,.2);padding:18px;position:relative;overflow:hidden;}
.tcard::before{content:'';position:absolute;top:0;right:0;width:60px;height:60px;background:radial-gradient(circle,rgba(232,184,75,.07),transparent 70%);}
.tc-lbl{font-size:9px;letter-spacing:3px;color:rgba(232,184,75,.5);margin-bottom:6px;}
.tc-icon{font-size:36px;margin-bottom:6px;}
.tc-title{font-family:'Amiri',serif;font-size:22px;color:var(--gold);}
.tc-sub{font-size:12px;color:var(--sand);margin-top:3px;}
.tc-text{font-size:12px;line-height:1.8;color:rgba(244,232,193,.8);margin-top:8px;}
.tc-say{font-family:'Amiri',serif;font-size:13px;color:var(--gold);font-style:italic;margin-top:8px;padding-top:8px;border-top:1px solid rgba(232,184,75,.15);}
.word-tag{display:inline-block;padding:3px 10px;margin:2px;background:rgba(232,184,75,.1);border:1px solid rgba(232,184,75,.25);font-size:12px;color:var(--gold);}

/* Alert */
.alert{background:linear-gradient(135deg,rgba(139,58,42,.3),rgba(45,31,94,.5));border:1px solid rgba(230,126,34,.5);border-right:4px solid var(--warm);padding:14px 18px;margin-bottom:18px;}
.al-t{font-family:'Amiri',serif;font-size:20px;color:var(--warm);margin-bottom:4px;}
.al-d{font-size:12px;line-height:1.7;}
.al-w{font-size:11px;color:var(--warm);font-weight:700;margin-top:6px;}

/* Month wheel */
.mwheel{display:grid;grid-template-columns:repeat(6,1fr);gap:6px;margin-bottom:18px;}
@media(max-width:700px){.mwheel{grid-template-columns:repeat(4,1fr);}}
.mbtn{padding:10px 4px;text-align:center;background:rgba(26,23,56,.8);border:1px solid rgba(232,184,75,.15);cursor:pointer;transition:all .2s;color:var(--sand);font-family:'Tajawal',sans-serif;}
.mbtn:hover{border-color:var(--gold);color:var(--gold);}
.mbtn.cur{border-color:var(--gold);background:rgba(232,184,75,.12);color:var(--gold);}
.mbtn .mi{font-size:20px;display:block;margin-bottom:2px;}
.mbtn .mn{font-size:10px;font-weight:700;}
.mbtn .md{font-size:8px;opacity:.5;margin-top:1px;}

/* Month detail */
.mdet{background:rgba(26,23,56,.9);border:1px solid rgba(232,184,75,.2);padding:22px;margin-bottom:18px;}
.mdet-h{display:flex;gap:14px;align-items:center;margin-bottom:18px;flex-wrap:wrap;}
.mdet-big{font-size:52px;}
.mdet-ar{font-family:'Amiri',serif;font-size:32px;color:var(--gold);}
.mdet-dz{font-size:13px;color:var(--sand);margin-top:3px;}
.mdet-nick{font-size:12px;color:var(--ochre);font-style:italic;margin-top:3px;}
.mdet-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
@media(max-width:600px){.mdet-grid{grid-template-columns:1fr;}}
.mbox{background:rgba(11,9,24,.5);border:1px solid rgba(232,184,75,.1);padding:14px;}
.mbox-lbl{font-size:9px;letter-spacing:3px;color:rgba(232,184,75,.4);margin-bottom:6px;}
.mbox-txt{font-size:12px;line-height:1.8;}
.poem{font-family:'Amiri',serif;font-size:15px;line-height:2.2;color:var(--cream);text-align:center;border-top:1px solid rgba(232,184,75,.2);border-bottom:1px solid rgba(232,184,75,.2);padding:14px 0;margin:14px 0;}
.saying{font-family:'Amiri',serif;font-size:14px;color:var(--gold);text-align:center;font-style:italic;margin:8px 0;}

/* Layali */
.lgrid{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
@media(max-width:700px){.lgrid{grid-template-columns:1fr;}}
.lcard{background:rgba(26,23,56,.9);border:1px solid rgba(232,184,75,.2);padding:18px;transition:border-color .2s;}
.lcard:hover{border-color:var(--gold);}
.lc-n{font-family:'Amiri',serif;font-size:22px;color:var(--gold);}
.lc-dz{font-size:12px;color:var(--sand);margin-bottom:3px;}
.lc-per{font-size:10px;letter-spacing:2px;color:rgba(232,184,75,.4);margin-bottom:10px;}
.lc-desc{font-size:12px;line-height:1.8;margin-bottom:10px;}
.lc-warn{font-size:11px;color:var(--warm);font-weight:700;padding:5px 8px;border:1px solid rgba(230,126,34,.3);margin-bottom:10px;}
.lc-signs li{font-size:11px;padding:3px 0;border-bottom:1px solid rgba(232,184,75,.08);}
.lc-signs li::before{content:'▸ ';color:var(--gold);}
.lc-say{font-family:'Amiri',serif;font-size:13px;color:var(--gold);font-style:italic;padding:4px 0;border-bottom:1px solid rgba(232,184,75,.08);}
.lc-poem{font-family:'Amiri',serif;font-size:13px;line-height:2;color:rgba(244,232,193,.85);background:rgba(11,9,24,.5);padding:12px;margin-top:10px;border-right:3px solid var(--gold);}
.lc-src{font-size:9px;color:rgba(232,184,75,.3);margin-top:4px;font-style:italic;}

/* Crops */
.cgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}
@media(max-width:800px){.cgrid{grid-template-columns:1fr 1fr;}}
@media(max-width:500px){.cgrid{grid-template-columns:1fr;}}
.ccard{background:rgba(26,23,56,.9);border:1px solid rgba(232,184,75,.15);padding:16px;transition:all .2s;cursor:default;}
.ccard:hover{border-color:var(--gold);transform:translateY(-2px);}
.cc-icon{font-size:32px;margin-bottom:6px;}
.cc-name{font-family:'Amiri',serif;font-size:17px;color:var(--gold);}
.cc-dz{font-size:10px;color:var(--sand);margin-bottom:4px;}
.cc-per{font-size:9px;letter-spacing:2px;color:rgba(232,184,75,.4);margin-bottom:6px;}
.cc-desc{font-size:11px;line-height:1.7;}
.cc-say{font-family:'Amiri',serif;font-size:12px;color:var(--gold);font-style:italic;margin-top:7px;padding-top:7px;border-top:1px solid rgba(232,184,75,.12);}

/* Lexicon */
.srch{width:100%;padding:12px 18px;margin-bottom:16px;background:rgba(26,23,56,.9);border:1px solid rgba(232,184,75,.3);border-right:3px solid var(--gold);color:var(--cream);font-family:'Tajawal',sans-serif;font-size:14px;outline:none;}
.srch::placeholder{color:rgba(232,184,75,.3);}
.lexgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
@media(max-width:700px){.lexgrid{grid-template-columns:1fr 1fr;}}
.lexcard{background:rgba(26,23,56,.9);border:1px solid rgba(232,184,75,.1);padding:12px;}
.lw{font-family:'Amiri',serif;font-size:20px;color:var(--gold);}
.lm{font-size:11px;color:var(--cream);margin-top:3px;line-height:1.5;}
.ls{font-size:8px;letter-spacing:2px;margin-top:5px;}
.stag{display:inline-block;padding:1px 7px;border:1px solid;}
.s-شتاء{color:var(--frost);border-color:var(--frost);}
.s-ربيع{color:var(--mint);border-color:var(--mint);}
.s-صيف{color:var(--warm);border-color:var(--warm);}
.s-خريف{color:var(--sand);border-color:var(--sand);}

/* Signs */
.sgrid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
@media(max-width:600px){.sgrid{grid-template-columns:1fr;}}
.scard{background:rgba(26,23,56,.9);border:1px solid rgba(232,184,75,.1);padding:12px;display:flex;gap:10px;align-items:flex-start;}
.sicon{font-size:24px;min-width:32px;}
.stxt{font-size:12px;font-weight:700;color:var(--cream);}
.smtxt{font-size:11px;color:var(--sand);margin-top:3px;line-height:1.5;}

/* Stars */
.nlist{display:flex;flex-direction:column;gap:12px;}
.ncard{background:rgba(26,23,56,.9);border:1px solid rgba(232,184,75,.15);padding:16px;display:flex;gap:14px;align-items:flex-start;}
.nicon{font-size:36px;min-width:44px;text-align:center;}
.nname{font-family:'Amiri',serif;font-size:20px;color:var(--gold);}
.nper{font-size:10px;letter-spacing:2px;color:rgba(232,184,75,.4);margin-bottom:4px;}
.nmean{font-size:12px;line-height:1.7;}
.nsay{font-family:'Amiri',serif;font-size:13px;color:var(--gold);font-style:italic;margin-top:7px;padding-top:7px;border-top:1px solid rgba(232,184,75,.12);}

/* ══ AI CHAT PANEL ══ */
.chat-wrap{display:grid;grid-template-columns:1fr 340px;gap:16px;height:calc(100vh - 230px);min-height:400px;}
@media(max-width:900px){.chat-wrap{grid-template-columns:1fr;height:auto;}}

.chat-panel{background:rgba(26,23,56,.9);border:1px solid rgba(232,184,75,.2);display:flex;flex-direction:column;overflow:hidden;}
.chat-hdr{padding:12px 16px;border-bottom:1px solid rgba(232,184,75,.15);background:rgba(11,9,24,.5);display:flex;align-items:center;gap:10px;}
.chat-hdr-title{font-family:'Amiri',serif;font-size:17px;color:var(--gold);}
.chat-hdr-sub{font-size:9px;letter-spacing:2px;color:var(--sand);}
.provider-lbl{margin-right:auto;font-size:9px;letter-spacing:2px;padding:2px 8px;border:1px solid rgba(232,184,75,.3);color:var(--sand);}

.chat-msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;}
.msg{max-width:85%;padding:10px 14px;line-height:1.8;font-size:13px;animation:fi .2s ease;}
.msg.user{align-self:flex-start;background:rgba(232,184,75,.12);border:1px solid rgba(232,184,75,.25);border-right:3px solid var(--gold);color:var(--cream);}
.msg.ai{align-self:flex-end;background:rgba(45,31,94,.5);border:1px solid rgba(107,85,180,.4);border-left:3px solid rgba(107,85,180,.8);color:var(--cream);font-family:'Amiri',serif;font-size:14px;}
.msg.err{border-color:rgba(231,76,60,.4);color:var(--red);}
.msg-label{font-size:9px;letter-spacing:2px;margin-bottom:4px;opacity:.6;}

.chat-input-area{padding:12px 16px;border-top:1px solid rgba(232,184,75,.15);background:rgba(11,9,24,.5);display:flex;flex-direction:column;gap:8px;}
.chat-input{width:100%;padding:10px 14px;background:rgba(26,23,56,.9);border:1px solid rgba(232,184,75,.25);border-right:3px solid var(--gold);color:var(--cream);font-family:'Tajawal',sans-serif;font-size:13px;resize:none;height:70px;outline:none;line-height:1.6;}
.chat-input::placeholder{color:rgba(232,184,75,.3);}
.chat-input:focus{border-color:var(--gold);}
.chat-btn{padding:10px 20px;background:rgba(26,23,56,.9);border:1px solid var(--gold);color:var(--gold);font-family:'Tajawal',sans-serif;font-size:13px;font-weight:700;cursor:pointer;transition:all .2s;letter-spacing:2px;}
.chat-btn:hover{background:rgba(232,184,75,.15);}
.chat-btn:disabled{opacity:.4;cursor:not-allowed;}

.quick-panel{display:flex;flex-direction:column;gap:8px;}
.qp-title{font-size:9px;letter-spacing:3px;color:rgba(232,184,75,.4);margin-bottom:4px;}
.qbtn{padding:10px 12px;background:rgba(26,23,56,.9);border:1px solid rgba(232,184,75,.15);color:var(--sand);font-family:'Tajawal',sans-serif;font-size:12px;text-align:right;cursor:pointer;transition:all .15s;line-height:1.5;}
.qbtn:hover{border-color:var(--gold);color:var(--gold);}

/* Thinking animation */
.thinking{display:flex;gap:4px;padding:4px 0;}
.thinking span{width:7px;height:7px;border-radius:50%;background:var(--gold);animation:bounce .8s infinite;}
.thinking span:nth-child(2){animation-delay:.15s;}
.thinking span:nth-child(3){animation-delay:.3s;}
@keyframes bounce{0%,80%,100%{transform:scale(.7);opacity:.5}40%{transform:scale(1);opacity:1}}

/* Offline badge */
.offbadge{position:fixed;bottom:12px;left:12px;z-index:100;padding:5px 12px;background:rgba(46,204,113,.12);border:1px solid rgba(46,204,113,.35);color:var(--mint);font-size:10px;letter-spacing:2px;}

::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:var(--deep);}
::-webkit-scrollbar-thumb{background:var(--ochre);}
</style>
</head>
<body>
<div class="offbadge">⬡ بلا انترنت</div>

<div class="hdr">
  <div class="geo"></div>
  <div class="hdr-inner">
    <div class="clock-box">
      <div class="clk" id="clk">--:--</div>
      <div class="cdate" id="cdate">---</div>
      <div class="moon" id="moon">🌕</div>
    </div>
    <div>
      <div class="logo-ar">الطاقس الجزائري</div>
      <div class="logo-sub">التقويم الفلاحي والحكمة الشعبية</div>
      <div class="logo-amz">ⵜⴰⵏⴻⵣⵣⵓⵜ ⵜⴰⵥⵓⵔⵉⵜ</div>
    </div>
    <div class="month-badge">
      <div class="mb-icon" id="mbIcon">🌙</div>
      <div class="mb-name" id="mbName">---</div>
      <div class="mb-season" id="mbSeason">---</div>
    </div>
    <div>
      <div class="ai-badge"><span class="ai-dot" id="aiDot"></span><span id="aiLbl">يتحقق...</span></div>
    </div>
  </div>
  <div class="nav">
    <button class="tab on" onclick="show('today',this)">📅 اليوم</button>
    <button class="tab" onclick="show('months',this)">📆 الأشهر</button>
    <button class="tab" onclick="show('layali',this)">🌙 الليالي</button>
    <button class="tab" onclick="show('ghars',this)">🌱 الغرس</button>
    <button class="tab" onclick="show('lex',this)">📖 الدارجة</button>
    <button class="tab" onclick="show('signs',this)">🔍 الإشارات</button>
    <button class="tab" onclick="show('stars',this)">⭐ النجوم</button>
    <button class="tab" onclick="show('chat',this)">🤖 اسأل AI</button>
  </div>
  <div class="geo" style="margin-top:10px;"></div>
</div>

<div class="main">

  <!-- TODAY -->
  <div class="sec on" id="sec-today">
    <div id="layaliAlert"></div>
    <div class="tgrid" id="todayGrid"></div>
    <div id="cropsToday"></div>
  </div>

  <!-- MONTHS -->
  <div class="sec" id="sec-months">
    <div class="sh">📆 التقويم الفلاحي الجزائري</div>
    <div class="mwheel" id="mwheel"></div>
    <div id="mdet"></div>
  </div>

  <!-- LAYALI -->
  <div class="sec" id="sec-layali">
    <div class="sh">🌙 الليالي البيض والسود والعجوز والوسم</div>
    <div class="lgrid" id="lgrid"></div>
  </div>

  <!-- GHARS -->
  <div class="sec" id="sec-ghars">
    <div class="sh">🌱 مواعيد الغرس والحصاد</div>
    <div class="cgrid" id="cgrid"></div>
  </div>

  <!-- LEXICON -->
  <div class="sec" id="sec-lex">
    <div class="sh">📖 معجم الطقس بالدارجة الجزائرية</div>
    <input class="srch" type="text" placeholder="ابحث: صقعة، وسم، قيظ..." id="srch" oninput="filterLex(this.value)">
    <div class="lexgrid" id="lexgrid"></div>
  </div>

  <!-- SIGNS -->
  <div class="sec" id="sec-signs">
    <div class="sh">🔍 الإشارات الطبيعية لتوقع الطقس</div>
    <div class="sgrid" id="sgrid"></div>
  </div>

  <!-- STARS -->
  <div class="sec" id="sec-stars">
    <div class="sh">⭐ النجوم والأنواء عند الفلاح الجزائري</div>
    <div class="nlist" id="nlist"></div>
  </div>

  <!-- AI CHAT -->
  <div class="sec" id="sec-chat">
    <div class="sh">🤖 اسأل خبير التقاليد الجزائرية</div>
    <div class="chat-wrap">
      <div class="chat-panel">
        <div class="chat-hdr">
          <div>
            <div class="chat-hdr-title">دردشة الذكاء الاصطناعي</div>
            <div class="chat-hdr-sub">اسأل عن الليالي، الوسم، الغرس، الطقس التقليدي...</div>
          </div>
          <span class="provider-lbl" id="provLbl">---</span>
        </div>
        <div class="chat-msgs" id="chatMsgs">
          <div class="msg ai">
            <div class="msg-label">▸ خبير التقاليد</div>
            مرحباً! أنا خبير في التقاليد الفلاحية الجزائرية. اسألني عن الليالي البيض والسود، الوسم، مواعيد الغرس، كلمات الطقس بالدارجة، أو أي شيء عن التقويم الشعبي الجزائري القديم.
          </div>
        </div>
        <div class="chat-input-area">
          <textarea class="chat-input" id="chatInput" placeholder="اسأل مثلاً: ما الفرق بين الليالي البيض والسود؟ متى نغرس الزيتون؟ ماذا تعني كلمة الشهيلية؟"></textarea>
          <button class="chat-btn" id="sendBtn" onclick="sendMsg()">⚡ أرسل السؤال</button>
        </div>
      </div>
      <div class="quick-panel">
        <div class="qp-title">▸ أسئلة سريعة</div>
        <button class="qbtn" onclick="askQuick(this.dataset.q)" data-q="ما هي الليالي البيض وما أصلها التاريخي؟">🌙 ما هي الليالي البيض؟</button>
        <button class="qbtn" onclick="askQuick(this.dataset.q)" data-q="متى يكون الوسم وما أهميته عند الفلاح الجزائري؟">🌧️ الوسم — متى وكيف؟</button>
        <button class="qbtn" onclick="askQuick(this.dataset.q)" data-q="قصة ليالي العجوز في التقاليد الجزائرية">👵 قصة العجوز بالتفصيل</button>
        <button class="qbtn" onclick="askQuick(this.dataset.q)" data-q="ما معنى كلمة الشهيلية والصقعة والشيبة بالدارجة الجزائرية؟">📖 الشهيلية والصقعة؟</button>
        <button class="qbtn" onclick="askQuick(this.dataset.q)" data-q="ما هي أمثال الجزائريين عن المطر والزراعة؟">🌾 أمثال عن المطر والزراعة</button>
        <button class="qbtn" onclick="askQuick(this.dataset.q)" data-q="متى يغرس الفلاح الجزائري الزيتون وكيف يعرف وقت الحصاد؟">🫒 توقيت الزيتون</button>
        <button class="qbtn" onclick="askQuick(this.dataset.q)" data-q="كيف يقرأ الفلاح الجزائري القديم الطقس من الطبيعة بدون أجهزة؟">🌿 قراءة الطقس من الطبيعة</button>
        <button class="qbtn" onclick="askQuick(this.dataset.q)" data-q="ما هي نجمة سهيل وما علاقتها بالمواسم عند الجزائريين؟">⭐ نجمة سهيل</button>
        <button class="qbtn" onclick="askQuick(this.dataset.q)" data-q="اشرح لي التقويم الفلاحي الجزائري القديم شهراً شهراً">📅 التقويم الفلاحي كاملاً</button>
      </div>
    </div>
  </div>

</div><!-- /main -->

<script>
let KB={}, chatHistory=[], isLoading=false;

// ── Tab switching ─────────────────────────────────────────────────
function show(id,btn){
  document.querySelectorAll('.sec').forEach(s=>s.classList.remove('on'));
  document.querySelectorAll('.tab').forEach(b=>b.classList.remove('on'));
  document.getElementById('sec-'+id).classList.add('on');
  if(btn) btn.classList.add('on');
}

// ── Clock ─────────────────────────────────────────────────────────
function tick(){
  const n=new Date();
  document.getElementById('clk').textContent=n.toTimeString().slice(0,5);
  document.getElementById('cdate').textContent=n.toLocaleDateString('ar-DZ',{weekday:'long',day:'numeric',month:'long'});
  const lun=29.53058867, ref=new Date(2000,0,6);
  const ph=(((n-ref)/86400000%lun)+lun)%lun;
  document.getElementById('moon').textContent=['🌑','🌒','🌓','🌔','🌕','🌖','🌗','🌘','🌑'][Math.round(ph/lun*8)];
}
setInterval(tick,1000); tick();

// ── Status ────────────────────────────────────────────────────────
async function checkStatus(){
  try{
    const d=await(await fetch('/api/status')).json();
    const dot=document.getElementById('aiDot');
    const lbl=document.getElementById('aiLbl');
    document.getElementById('provLbl').textContent=d.provider.toUpperCase()+' — '+d.model;
    if(d.has_key){ dot.className='ai-dot'; lbl.textContent=d.provider.toUpperCase()+' جاهز'; }
    else{ dot.className='ai-dot warn'; lbl.textContent='أضف مفتاح AI'; }
  }catch(e){ document.getElementById('aiDot').className='ai-dot warn'; }
}
checkStatus(); setInterval(checkStatus,20000);

// ── Load KB ───────────────────────────────────────────────────────
async function init(){
  KB=await(await fetch('/api/kb')).json();
  const td=await(await fetch('/api/today')).json();
  renderToday(td);
  renderMonths();
  renderLayali();
  renderCrops();
  renderLex();
  renderSigns();
  renderStars();
}

// ── TODAY ─────────────────────────────────────────────────────────
function renderToday(td){
  const m=td.month;
  document.getElementById('mbIcon').textContent=m.icon;
  document.getElementById('mbName').textContent=m.ar;
  document.getElementById('mbSeason').textContent='— '+m.season+' —';

  // Alert
  const alEl=document.getElementById('layaliAlert');
  if(td.layali.length){
    const ly=td.layali[0];
    alEl.innerHTML=`<div class="alert"><div class="al-t">${ly.icon} ${ly.name} — نحن في هذه الفترة الآن</div><div class="al-d">${ly.desc}</div><div class="al-w">⚠️ ${ly.farming}</div></div>`;
  }

  document.getElementById('todayGrid').innerHTML=`
    <div class="tcard"><div class="tc-lbl">▸ الشهر الفلاحي</div><div class="tc-icon">${m.icon}</div>
      <div class="tc-title">${m.ar}</div><div class="tc-sub">${m.dz} · ${m.amz}</div>
      <div class="tc-text">${m.nick}</div></div>
    <div class="tcard"><div class="tc-lbl">▸ الطقس التقليدي</div><div class="tc-icon">🌡️</div>
      <div class="tc-title">الطقس</div><div class="tc-text">${m.weather}</div>
      <div class="tc-say">${m.saying}</div></div>
    <div class="tcard"><div class="tc-lbl">▸ أعمال الفلاح</div><div class="tc-icon">👨‍🌾</div>
      <div class="tc-title">في الأرض</div><div class="tc-text">${m.farming}</div>
      <div style="margin-top:8px">${m.words.map(w=>`<span class="word-tag">${w}</span>`).join('')}</div></div>`;

  if(td.crops.length){
    document.getElementById('cropsToday').innerHTML=`<div class="sh" style="margin-top:20px;">🌿 الغرس والحصاد هذا الشهر</div>
      <div class="cgrid">${td.crops.map(cropCard).join('')}</div>`;
  }
}

// ── MONTHS ────────────────────────────────────────────────────────
function renderMonths(){
  const cur=new Date().getMonth()+1;
  document.getElementById('mwheel').innerHTML=KB.months.map(m=>`
    <div class="mbtn ${m.n===cur?'cur':''}" onclick="showMDet(${m.n})">
      <span class="mi">${m.icon}</span><div class="mn">${m.ar}</div><div class="md">${m.dz}</div>
    </div>`).join('');
  showMDet(cur);
}
function showMDet(n){
  const m=KB.months.find(x=>x.n===n); if(!m)return;
  document.getElementById('mdet').innerHTML=`
    <div class="mdet">
      <div class="mdet-h"><div class="mdet-big">${m.icon}</div>
        <div><div class="mdet-ar">${m.ar}</div><div class="mdet-dz">${m.dz} · ${m.amz}</div>
          <div class="mdet-nick">${m.nick}</div></div></div>
      <div class="poem">${m.poem.replace(/\n/g,'<br>')}</div>
      <div class="mdet-grid">
        <div class="mbox"><div class="mbox-lbl">▸ الطقس التقليدي</div><div class="mbox-txt">${m.weather}</div></div>
        <div class="mbox"><div class="mbox-lbl">▸ أعمال الفلاح</div><div class="mbox-txt">${m.farming}</div></div>
      </div>
      <div style="margin-top:14px">${m.words.map(w=>`<span class="word-tag">${w}</span>`).join('')}</div>
      <div class="saying" style="margin-top:12px">${m.saying}</div>
    </div>`;
}

// ── LAYALI ────────────────────────────────────────────────────────
function renderLayali(){
  document.getElementById('lgrid').innerHTML=KB.layali.map(ly=>`
    <div class="lcard">
      <div class="lc-n">${ly.icon} ${ly.name}</div>
      <div class="lc-dz">${ly.darija}</div>
      <div class="lc-per">📅 ${ly.period}</div>
      <div class="lc-desc">${ly.desc}</div>
      <div class="lc-warn">⚠️ ${ly.farming}</div>
      <ul class="lc-signs">${(ly.signs||[]).map(s=>`<li>${s}</li>`).join('')}</ul>
      <div style="margin-top:10px">${(ly.sayings||[]).map(s=>`<div class="lc-say">${s}</div>`).join('')}</div>
      <div class="lc-poem">${ly.poem.replace(/\n/g,'<br>')}</div>
      <div class="lc-src">${ly.src}</div>
    </div>`).join('');
}

// ── CROPS ─────────────────────────────────────────────────────────
function cropCard(g){
  return `<div class="ccard"><div class="cc-icon">${g.i}</div>
    <div class="cc-name">${g.c}</div><div class="cc-dz">${g.dz}</div>
    <div class="cc-per">📅 ${g.p}</div><div class="cc-desc">${g.desc}</div>
    ${g.says.map(s=>`<div class="cc-say">${s}</div>`).join('')}</div>`;
}
function renderCrops(){ document.getElementById('cgrid').innerHTML=KB.ghars.map(cropCard).join(''); }

// ── LEXICON ───────────────────────────────────────────────────────
function lexCard(w){ return `<div class="lexcard"><div class="lw">${w.w}</div>
  <div class="lm">${w.m}</div><div class="ls"><span class="stag s-${w.s}">${w.s}</span></div></div>`; }
function renderLex(f=null){ document.getElementById('lexgrid').innerHTML=(f||KB.lexicon).map(lexCard).join(''); }
function filterLex(q){
  if(!q.trim()){renderLex();return;}
  renderLex(KB.lexicon.filter(w=>w.w.includes(q)||w.m.toLowerCase().includes(q.toLowerCase())||w.s.includes(q)));
}

// ── SIGNS ─────────────────────────────────────────────────────────
function renderSigns(){
  document.getElementById('sgrid').innerHTML=KB.signs.map(s=>`
    <div class="scard"><div class="sicon">${s.i}</div>
    <div><div class="stxt">${s.s}</div><div class="smtxt">← ${s.m}</div></div></div>`).join('');
}

// ── STARS ─────────────────────────────────────────────────────────
function renderStars(){
  document.getElementById('nlist').innerHTML=KB.nujum.map(n=>`
    <div class="ncard"><div class="nicon">${n.i}</div>
    <div><div class="nname">${n.n}</div><div class="nper">📅 ${n.p}</div>
    <div class="nmean">${n.m}</div><div class="nsay">${n.say}</div></div></div>`).join('');
}

// ══ AI CHAT ═══════════════════════════════════════════════════════
function addMsg(role, text){
  const msgs=document.getElementById('chatMsgs');
  const div=document.createElement('div');
  div.className='msg '+(role==='user'?'user':'ai');
  div.innerHTML=`<div class="msg-label">${role==='user'?'▸ أنت':'▸ خبير التقاليد'}</div>${text}`;
  msgs.appendChild(div);
  msgs.scrollTop=msgs.scrollHeight;
  return div;
}

function showThinking(){
  const msgs=document.getElementById('chatMsgs');
  const div=document.createElement('div');
  div.className='msg ai'; div.id='thinking';
  div.innerHTML='<div class="thinking"><span></span><span></span><span></span></div>';
  msgs.appendChild(div);
  msgs.scrollTop=msgs.scrollHeight;
}

async function sendMsg(){
  if(isLoading)return;
  const inp=document.getElementById('chatInput');
  const q=inp.value.trim();
  if(!q)return;
  inp.value='';
  isLoading=true;
  document.getElementById('sendBtn').disabled=true;

  addMsg('user',q);
  chatHistory.push({role:'user',content:q});
  showThinking();

  try{
    const resp=await fetch('/api/chat',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({question:q, history:chatHistory.slice(-8)})
    });
    const data=await resp.json();
    document.getElementById('thinking')?.remove();
    const answer=data.answer||data.error||'⚠️ لم يصل رد';
    addMsg('ai',answer);
    chatHistory.push({role:'assistant',content:answer});
  }catch(e){
    document.getElementById('thinking')?.remove();
    const d=addMsg('ai','⚠️ خطأ في الاتصال: '+e.message);
    d.classList.add('err');
  }finally{
    isLoading=false;
    document.getElementById('sendBtn').disabled=false;
    document.getElementById('chatInput').focus();
  }
}

function askQuick(q){
  document.getElementById('chatInput').value=q;
  show('chat', document.querySelector('.tab:last-child'));
  document.querySelectorAll('.tab').forEach(b=>b.classList.remove('on'));
  document.querySelectorAll('.tab')[7].classList.add('on');
  sendMsg();
}

document.addEventListener('keydown',e=>{
  if(e.ctrlKey&&e.key==='Enter'&&document.getElementById('sec-chat').classList.contains('on')) sendMsg();
});

init();
</script>
</body>
</html>"""

# ════════════════════════════════════════════════════════════════════
#  LAUNCH — فتح المتصفح تلقائياً
# ════════════════════════════════════════════════════════════════════
def open_browser():
    time.sleep(1.5)
    url = "http://localhost:5001"
    import sys, subprocess
    if sys.platform == "darwin":
        subprocess.Popen(["open", url])
    elif sys.platform == "win32":
        subprocess.Popen(["start", url], shell=True)
    else:
        # Linux — try multiple options
        for cmd in ["xdg-open", "sensible-browser", "firefox", "chromium-browser", "google-chrome"]:
            try:
                subprocess.Popen([cmd, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                break
            except FileNotFoundError:
                continue

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    print("\n" + "═"*55)
    print("  الطاقس الجزائري — TAQS DJAZAIRI")
    print("  التقويم الفلاحي + الذكاء الاصطناعي")
    print("═"*55)
    print(f"  🌐  http://localhost:{port}")
    print(f"  🤖  AI: {AI_PROVIDER.upper()}")
    print(f"  🔑  Key: {'✅ موجود' if (ANTHROPIC_KEY or DEEPSEEK_KEY or AI_PROVIDER=='ollama') else '❌ أضف .env'}")
    print(f"  ⬡   Fully Offline (except AI chat)")
    print("═"*55)
    print("  افتح المتصفح على: http://localhost:5001")
    print("  Ctrl+C لإيقاف التشغيل\n")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=False, host="0.0.0.0", port=port, use_reloader=False)
