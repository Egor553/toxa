"""
Обработчики текстовых сообщений
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from datetime import datetime
from bot.database.db import get_db
from bot.database.models import User, Task, Category
from bot.ai.openai_client import AIClient
from bot.utils.formatters import MessageFormatter


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений (создание задач)"""
    user = update.effective_user
    message_text = update.message.text
    
    db = next(get_db())
    
    try:
        # Получаем или создаём пользователя
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        if not db_user:
            db_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        
        # Парсим задачу с помощью ИИ
        parsed = AIClient.parse_task(message_text)
        
        # Определяем категорию
        categories = [cat.name for cat in db.query(Category).all()]
        category_name = AIClient.categorize_task(parsed["title"], categories)
        
        category = db.query(Category).filter(Category.name == category_name).first()
        if not category:
            category = Category(name=category_name)
            db.add(category)
            db.commit()
            db.refresh(category)
        
        # Создаём задачу
        task = Task(
            user_id=db_user.id,
            category_id=category.id,
            title=parsed["title"],
            current_progress=parsed.get("current_progress") or 0.0,
            target_progress=parsed.get("target_progress"),
            is_active=True,
            is_completed=False
        )
        
        # Парсим дедлайн, если есть
        if parsed.get("deadline"):
            try:
                task.deadline = datetime.strptime(parsed["deadline"], "%Y-%m-%d")
            except:
                pass
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Формируем ответ
        response = f"✅ Задача добавлена!\n\n"
        response += f"📌 {task.title}\n"
        response += f"🏷 Категория: {category.name}\n"
        
        if task.target_progress:
            response += f"📊 Прогресс: {task.current_progress:.0f}/{task.target_progress:.0f}\n"
        
        if task.deadline:
            response += f"📅 Дедлайн: {task.deadline.strftime('%d.%m.%Y')}\n"
        
        # Добавляем кнопки
        keyboard = [
            [
                InlineKeyboardButton("✅ Выполнено", callback_data=f"complete_{task.id}"),
                InlineKeyboardButton("❌ Не выполнено", callback_data=f"miss_{task.id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при создании задачи: {e}")
    finally:
        db.close()

