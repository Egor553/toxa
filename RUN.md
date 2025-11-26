# 🚀 Запуск бота на сервере

## Быстрая установка и запуск

### 1. Клонируй репозиторий
```bash
git clone https://github.com/Egor553/toxa.git
cd toxa
```

### 2. Установи всё автоматически
```bash
chmod +x install.sh start.sh
./install.sh
```

### 3. Настрой токен
```bash
nano .env
```
Добавь свой `TELEGRAM_BOT_TOKEN`

### 4. Запусти бота
```bash
./start.sh
```

---

## Запуск в фоне (screen)

```bash
screen -S toxa
./start.sh
```

Отключись: `Ctrl+A`, затем `D`  
Вернуться: `screen -r toxa`

---

## Обновление кода

```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
```

---

## Всё!

Бот запущен и работает! 🎉

