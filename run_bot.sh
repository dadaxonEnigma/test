#!/bin/bash

echo ""
echo "════════════════════════════════════════════"
echo "   🤖 Telegram Bot - Test Learning App"
echo "════════════════════════════════════════════"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python не установлен!"
    echo ""
    echo "Установите Python:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo ""
    exit 1
fi

echo "✅ Python найден"
echo ""

# Check if requirements are installed
if ! python3 -c "import telegram" 2>/dev/null; then
    echo "📦 Установка зависимостей..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка при установке зависимостей!"
        exit 1
    fi
    echo ""
fi

echo "✅ Все готово!"
echo ""

# Check if token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠️  TELEGRAM_BOT_TOKEN не установлен!"
    echo ""
    echo "Как получить токен:"
    echo "1. Откройте Telegram и найдите @BotFather"
    echo "2. Отправьте /newbot"
    echo "3. Ответьте на вопросы"
    echo "4. Скопируйте полученный TOKEN"
    echo ""
    read -p "Введите ваш TELEGRAM_BOT_TOKEN: " TOKEN
    export TELEGRAM_BOT_TOKEN="$TOKEN"
    echo ""
fi

echo "🤖 Запускаем бота..."
echo ""
echo "Сейчас бот должен появиться в Telegram"
echo "Отправьте /start вашему боту"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo "════════════════════════════════════════════"
echo ""

python3 telegram_bot.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Бот завершился с ошибкой!"
    echo ""
fi
