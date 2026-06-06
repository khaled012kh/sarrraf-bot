#!/bin/bash
echo "========================================"
echo "   بوت صرّاف - محول العملات الذكي"
echo "========================================"
echo

# التأكد من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 مش مثبّت"
    echo "   حمّله من: https://www.python.org/downloads/"
    exit 1
fi

echo "[1/3] فحص المكتبات..."
if ! python3 -c "import telegram" 2>/dev/null; then
    echo "[2/3] تثبيت المكتبات... استنى شوية"
    pip3 install -r requirements.txt
else
    echo "[2/3] المكتبات موجودة بالفعل ✓"
fi

echo "[3/3] تشغيل البوت..."
echo
echo "========================================"
echo "  ✅ البوت شغّال - روح ابعتله /start"
echo "  لإيقاف البوت اضغط Ctrl+C"
echo "========================================"
echo

python3 bot.py
