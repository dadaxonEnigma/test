@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ════════════════════════════════════════════
echo    🤖 Telegram Bot - Test Learning App
echo ════════════════════════════════════════════
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Python не установлен!
    echo.
    echo Пожалуйста установите Python с python.org
    echo При установке выбирите "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Check if requirements are installed
pip show python-telegram-bot >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo 📦 Установка зависимостей...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        color 0C
        echo ❌ Ошибка при установке зависимостей!
        pause
        exit /b 1
    )
    echo.
)

color 0A
echo ✅ Все готово!
echo.

REM Check if token is set
if "%TELEGRAM_BOT_TOKEN%"=="" (
    color 0E
    echo ⚠️  TELEGRAM_BOT_TOKEN не установлен!
    echo.
    echo Как получить токен:
    echo 1. Откройте Telegram и найдите @BotFather
    echo 2. Отправьте /newbot
    echo 3. Ответьте на вопросы
    echo 4. Скопируйте полученный TOKEN
    echo.
    set /p TOKEN="Введите ваш TELEGRAM_BOT_TOKEN: "
    set TELEGRAM_BOT_TOKEN=%TOKEN%
    echo.
)

color 0A
echo 🤖 Запускаем бота...
echo.
echo Сейчас бот должен появиться в Telegram
echo Отправьте /start вашему боту
echo.
echo Для остановки нажмите Ctrl+C
echo ════════════════════════════════════════════
echo.

python telegram_bot.py

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ❌ Бот завершился с ошибкой!
    echo.
    pause
)
