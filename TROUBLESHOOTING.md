# 🛠️ حل مشاكل بوت صرّاف

## ❌ المشكلة 1: "البوت مش بيرد على /start"

### السبب 99% من الوقت: البوت مش شغّال على جهازك!

**الطريقة الأسهل:**

✅ على **Windows**: دابل كليك على `run.bat`
✅ على **Mac/Linux**: شغّل `./run.sh` من Terminal

---

## ❌ المشكلة 2: "python is not recognized"

**الحل:** ثبّت Python من https://www.python.org/downloads/

⚠️ **مهم جداً:** في شاشة التثبيت، فعّل الخيار ده:
```
☑️ Add Python to PATH
```

---

## ❌ المشكلة 3: pip مش موجود

```bash
python -m ensurepip --upgrade
```

أو شغّل:
```bash
python -m pip install -r requirements.txt
```

---

## ❌ المشكلة 4: "No module named telegram"

```bash
pip install python-telegram-bot==20.7 aiohttp==3.9.1
```

---

## ❌ المشكلة 5: البوت اشتغل بس مش بيرد

**تأكد من 3 حاجات:**

### 1. البوت شغّال فعلاً؟
في Terminal لازم تشوف:
```
✅ البوت شغال...
✅ تم تحديث أسعار العملات - 161 عملة
```

### 2. بتكلم البوت الصح؟
- ادخل @BotFather
- `/mybots` → اختار بوتك
- اضغط على الاسم يفتحلك المحادثة
- ابعت `/start`

### 3. فيرس فاير وول بيمنع الاتصال؟
لو أنت على شبكة شركة أو جامعة، جرّب من موبايلك.

---

## ❌ المشكلة 6: "Conflict: terminated by other getUpdates request"

معناه في **نسخة تانية** من البوت شغّالة.
- أغلق كل Terminal / Python شغّال
- شغّل البوت مرة واحدة بس

---

## ✅ اختبار سريع إن كل حاجة تمام

افتح Terminal في مجلد المشروع واكتب:
```bash
python -c "from telegram import Bot; import asyncio; asyncio.run(Bot('8928361588:AAHkkxvEcYjJw9ZyLha9gqLsiAXpvMGTHNM').get_me())"
```

لو اشتغل يبقى كل حاجة تمام. لو طلع error، ابعتلي الـ error.

---

## 🆘 لو مش قادر تحلها

ابعتلي:
1. **صورة Terminal** بعد ما شغّلت `run.bat`
2. **رسالة الخطأ** لو ظهرت
3. **نوع نظامك** (Windows / Mac / Linux)

وأنا هحلها لك إن شاء الله 💪
