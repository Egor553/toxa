#!/bin/bash
# Автоматическая установка бота на сервере

echo "🚀 Установка Telegram-бота Toxa..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.10+"
    exit 1
fi

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Обновление pip
echo "⬆️ Обновление pip..."
pip install --upgrade pip

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Создание папки для БД
echo "📁 Создание папки для базы данных..."
mkdir -p data

# Проверка .env файла
if [ ! -f .env ]; then
    echo "⚠️ Файл .env не найден. Создаю шаблон..."
    cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=
DATABASE_URL=sqlite:///data/bot.db
XP_PER_TASK=10
XP_MULTIPLIER=1.0
LEVEL_UP_BASE_XP=100
DEFAULT_REMINDER_TIME=18:00
TIMEZONE=Europe/Moscow
EOF
    echo "✅ Файл .env создан. ОБЯЗАТЕЛЬНО отредактируй его и добавь TELEGRAM_BOT_TOKEN!"
    echo "   Команда: nano .env"
else
    echo "✅ Файл .env уже существует"
fi

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Отредактируй .env файл: nano .env"
echo "2. Добавь свой TELEGRAM_BOT_TOKEN"
echo "3. Запусти бота: ./start.sh"
echo ""

