# ⚡ تشغيل سريع - 3 خطوات بس

## 1️⃣ ثبّت المكتبات
```bash
pip install -r requirements.txt
```

## 2️⃣ حط التوكن
افتح `bot.py` وغيّر السطر ده (السطر 17):
```python
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE")
```
لـ:
```python
BOT_TOKEN = "التوكن_بتاعك_من_BotFather"
```

> 💡 أو شغّل بالأمر ده في Terminal:
> ```bash
> export BOT_TOKEN="التوكن_بتاعك"   # Linux/Mac
> set BOT_TOKEN=التوكن_بتاعك        # Windows
> python bot.py
> ```

## 3️⃣ شغّل
```bash
python bot.py
```

لو شغال صح هتشوف:
```
✅ البوت شغال...
✅ تم تحديث أسعار العملات - 161 عملة
```

---

## 🚀 عايز يشتغل 24/7 مجاناً؟

ارفع المشروع على **Render.com** (مجاني):
1. ارفع الملفات على GitHub
2. اعمل **New Background Worker**
3. في Environment ضيف `BOT_TOKEN` فقط
4. اعمل Deploy

→ التفاصيل الكاملة في `README.md`
