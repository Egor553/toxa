# 🚀 Деплой на Timeweb

Инструкция по развёртыванию Telegram-бота на облачном сервере Timeweb.

## 📋 Подготовка

### 1. Подключение к серверу

1. Зайди в панель управления Timeweb
2. Создай новый хостинг или используй существующий
3. Убедись, что у тебя есть доступ по SSH

### 2. Клонирование репозитория

Подключись к серверу по SSH и выполни:

```bash
# Перейди в нужную директорию (обычно /home/uXXXXXX/domains/yourdomain.com/public_html)
cd ~/domains/yourdomain.com/public_html

# Клонируй репозиторий
git clone https://github.com/Egor553/toxa.git .

# Или если папка уже существует:
cd toxa
git pull origin main
```

## 🔧 Установка зависимостей

### 1. Создай виртуальное окружение

```bash
# Создай виртуальное окружение
python3 -m venv venv

# Активируй его
source venv/bin/activate
```

### 2. Установи зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## ⚙️ Настройка переменных окружения

### 1. Создай файл .env

```bash
nano .env
```

### 2. Добавь переменные:

```env
TELEGRAM_BOT_TOKEN=твой_токен_от_BotFather
OPENAI_API_KEY=твой_ключ_openai_или_оставь_пустым
DATABASE_URL=sqlite:///data/bot.db
XP_PER_TASK=10
XP_MULTIPLIER=1.0
LEVEL_UP_BASE_XP=100
DEFAULT_REMINDER_TIME=18:00
TIMEZONE=Europe/Moscow
```

### 3. Сохрани файл (Ctrl+O, Enter, Ctrl+X)

## 🗄️ Настройка базы данных

```bash
# Создай папку для БД
mkdir -p data

# Инициализируй БД (запустится автоматически при первом запуске)
python bot/main.py
```

## 🚀 Запуск бота

### Вариант 1: Запуск через screen (рекомендуется)

```bash
# Установи screen, если его нет
sudo apt-get install screen  # или yum install screen

# Создай новую сессию screen
screen -S toxa_bot

# Активируй виртуальное окружение
source venv/bin/activate

# Запусти бота
python bot/main.py

# Отключись от screen: Ctrl+A, затем D
# Вернуться: screen -r toxa_bot
```

### Вариант 2: Запуск через systemd (для постоянной работы)

Создай файл `/etc/systemd/system/toxa-bot.service`:

```bash
sudo nano /etc/systemd/system/toxa-bot.service
```

Содержимое:

```ini
[Unit]
Description=Telegram Bot Toxa
After=network.target

[Service]
Type=simple
User=uXXXXXX  # Замени на своего пользователя
WorkingDirectory=/home/uXXXXXX/domains/yourdomain.com/public_html
Environment="PATH=/home/uXXXXXX/domains/yourdomain.com/public_html/venv/bin"
ExecStart=/home/uXXXXXX/domains/yourdomain.com/public_html/venv/bin/python bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируй сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable toxa-bot
sudo systemctl start toxa-bot

# Проверь статус
sudo systemctl status toxa-bot

# Просмотр логов
sudo journalctl -u toxa-bot -f
```

### Вариант 3: Запуск через nohup

```bash
# Активируй виртуальное окружение
source venv/bin/activate

# Запусти в фоне
nohup python bot/main.py > bot.log 2>&1 &

# Проверь, что процесс запущен
ps aux | grep python

# Просмотр логов
tail -f bot.log
```

## 🔄 Обновление бота

Когда нужно обновить код:

```bash
# Перейди в директорию проекта
cd ~/domains/yourdomain.com/public_html

# Останови бота (если через systemd)
sudo systemctl stop toxa-bot

# Обнови код
git pull origin main

# Обнови зависимости (если нужно)
source venv/bin/activate
pip install -r requirements.txt

# Запусти снова
sudo systemctl start toxa-bot
```

## 📝 Проверка работы

1. Найди своего бота в Telegram
2. Отправь команду `/start`
3. Проверь логи:
   ```bash
   # Если через systemd
   sudo journalctl -u toxa-bot -n 50
   
   # Если через nohup
   tail -f bot.log
   ```

## 🛠️ Решение проблем

### Бот не запускается

```bash
# Проверь, что Python 3.10+
python3 --version

# Проверь переменные окружения
cat .env

# Проверь права на файлы
chmod +x bot/main.py
```

### Ошибки с базой данных

```bash
# Проверь права на папку data
chmod 755 data
chmod 644 data/bot.db  # если файл уже создан
```

### Бот падает

```bash
# Проверь логи
tail -100 bot.log

# Проверь, что все зависимости установлены
pip list
```

## 🔐 Безопасность

1. **Не коммить .env файл** - он уже в .gitignore
2. **Ограничь права доступа к .env**:
   ```bash
   chmod 600 .env
   ```
3. **Используй SSH ключи** вместо паролей

## 📊 Мониторинг

Для мониторинга работы бота можно использовать:

```bash
# Проверка процесса
ps aux | grep python

# Проверка использования ресурсов
top -p $(pgrep -f "bot/main.py")

# Размер базы данных
du -h data/bot.db
```

## ⏰ Настройка cron (если нужно)

Если планировщик не работает, можно настроить cron для ежедневных задач:

```bash
crontab -e
```

Добавь строку (замени пути на свои):

```cron
0 9 * * * cd /home/uXXXXXX/domains/yourdomain.com/public_html && /home/uXXXXXX/domains/yourdomain.com/public_html/venv/bin/python -c "from bot.scheduler.reminder_scheduler import ReminderScheduler; import asyncio; asyncio.run(ReminderScheduler._send_daily_tasks())"
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверь логи
2. Убедись, что все переменные окружения установлены
3. Проверь версию Python (должна быть 3.10+)

