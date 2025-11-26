# ⚡ Быстрый деплой на Timeweb

Краткая инструкция для быстрого развёртывания.

## 🚀 Шаги деплоя

### 1. Подключение к серверу

```bash
ssh uXXXXXX@your-server.timeweb.ru
```

### 2. Клонирование репозитория

```bash
cd ~/domains/yourdomain.com/public_html
git clone https://github.com/Egor553/toxa.git .
```

### 3. Установка

```bash
# Создай виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установи зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Настройка .env

```bash
nano .env
```

Добавь:
```env
TELEGRAM_BOT_TOKEN=твой_токен
```

### 5. Создай папку для БД

```bash
mkdir -p data
```

### 6. Запуск через screen (самый простой способ)

```bash
screen -S toxa
source venv/bin/activate
python bot/main.py
```

Отключись: `Ctrl+A`, затем `D`

Вернуться: `screen -r toxa`

---

## 🔄 Обновление

```bash
cd ~/domains/yourdomain.com/public_html
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
```

Перезапусти бота в screen: `screen -r toxa`, затем `Ctrl+C` и снова `python bot/main.py`

---

## 📋 Полная инструкция

См. `DEPLOY.md` для подробной инструкции с systemd и другими опциями.

