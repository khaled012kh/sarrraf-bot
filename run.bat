@echo off
chcp 65001 >nul
title بوت صرّاف - محول العملات
echo ========================================
echo     بوت صرّاف - محول العملات الذكي
echo ========================================
echo.

REM التأكد من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [خطأ] Python مش مثبّت على جهازك!
    echo حمّله من: https://www.python.org/downloads/
    echo وتأكد تفعل Add Python to PATH وقت التثبيت
    pause
    exit /b
)

echo [1/3] فحص المكتبات...
pip show python-telegram-bot >nul 2>&1
if errorlevel 1 (
    echo [2/3] تثبيت المكتبات... استنى شوية
    pip install -r requirements.txt
) else (
    echo [2/3] المكتبات موجودة بالفعل ✓
)

echo [3/3] تشغيل البوت...
echo.
echo ========================================
echo  ✅ البوت شغّال - روح ابعتله /start
echo  لإيقاف البوت اضغط Ctrl+C
echo ========================================
echo.

python bot.py

pause
