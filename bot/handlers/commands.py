"""
Обработчики команд бота
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from bot.database.db import get_db
from bot.database.models import User, Task, Category, TaskLog
from bot.ai.openai_client import AIClient
from bot.gamification.xp_system import XPSystem
from bot.gamification.achievements import AchievementSystem
from bot.utils.formatters import MessageFormatter
from config.settings import settings


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    db = next(get_db())
    
    try:
        # Проверяем, есть ли пользователь в БД
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        
        if not db_user:
            # Создаём нового пользователя
            db_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            welcome_message = f"""
👋 Привет, {user.first_name}!

Я твой личный мини-коуч для геймификации рабочих процессов.

🎮 Что я умею:
• Принимать задачи и цели
• Категоризировать их автоматически
• Отслеживать прогресс
• Начислять XP и уровни
• Выдавать ачивки
• Мотивировать тебя

📝 Просто напиши мне задачу, например:
"Хочу цель: 500 подписчиков, я на 480"
или
"Добавь тренировку: 45 минут кардио"

Используй /help для списка команд.
"""
        else:
            welcome_message = f"""
👋 С возвращением, {db_user.first_name or user.first_name}!

Твой уровень: {db_user.level} | XP: {db_user.xp}
Серия дней: {db_user.current_streak} 🔥

Что будем делать сегодня?
"""
        
        await update.message.reply_text(welcome_message)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        db.close()


async def add_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /add"""
    await update.message.reply_text(
        "📝 Напиши задачу или цель, например:\n\n"
        "• Хочу цель: 500 подписчиков, я на 480\n"
        "• Добавь тренировку: 45 минут кардио\n"
        "• Записать сторис для блога"
    )


async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /tasks"""
    user = update.effective_user
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        if not db_user:
            await update.message.reply_text("❌ Пользователь не найден. Используй /start")
            return
        
        # Получаем активные задачи
        active_tasks = db.query(Task).filter(
            Task.user_id == db_user.id,
            Task.is_active == True,
            Task.is_completed == False
        ).all()
        
        message = MessageFormatter.format_task_list(active_tasks)
        
        # Добавляем кнопки для каждой задачи
        keyboard = []
        for task in active_tasks:
            keyboard.append([
                InlineKeyboardButton(
                    f"✅ {task.title[:30]}...",
                    callback_data=f"complete_{task.id}"
                ),
                InlineKeyboardButton(
                    f"❌ {task.title[:30]}...",
                    callback_data=f"miss_{task.id}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        db.close()


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /progress"""
    user = update.effective_user
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        if not db_user:
            await update.message.reply_text("❌ Пользователь не найден. Используй /start")
            return
        
        message = MessageFormatter.format_progress(db_user)
        
        # Получаем ачивки
        achievements = db_user.achievements
        if achievements:
            message += "\n\n" + MessageFormatter.format_achievements(achievements)
        
        await update.message.reply_text(message)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        db.close()


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    user = update.effective_user
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        if not db_user:
            await update.message.reply_text("❌ Пользователь не найден. Используй /start")
            return
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)
        
        # Статистика за сегодня
        today_completed = db.query(TaskLog).filter(
            TaskLog.user_id == db_user.id,
            TaskLog.status == "completed",
            TaskLog.created_at >= today_start
        ).count()
        
        today_missed = db.query(TaskLog).filter(
            TaskLog.user_id == db_user.id,
            TaskLog.status == "missed",
            TaskLog.created_at >= today_start
        ).count()
        
        today_total = today_completed + today_missed
        today_percentage = (today_completed / today_total * 100) if today_total > 0 else 0
        
        # Статистика за неделю
        week_completed = db.query(TaskLog).filter(
            TaskLog.user_id == db_user.id,
            TaskLog.status == "completed",
            TaskLog.created_at >= week_start
        ).count()
        
        week_missed = db.query(TaskLog).filter(
            TaskLog.user_id == db_user.id,
            TaskLog.status == "missed",
            TaskLog.created_at >= week_start
        ).count()
        
        week_total = week_completed + week_missed
        week_percentage = (week_completed / week_total * 100) if week_total > 0 else 0
        
        # Статистика за месяц
        month_completed = db.query(TaskLog).filter(
            TaskLog.user_id == db_user.id,
            TaskLog.status == "completed",
            TaskLog.created_at >= month_start
        ).count()
        
        month_missed = db.query(TaskLog).filter(
            TaskLog.user_id == db_user.id,
            TaskLog.status == "missed",
            TaskLog.created_at >= month_start
        ).count()
        
        month_total = month_completed + month_missed
        month_percentage = (month_completed / month_total * 100) if month_total > 0 else 0
        
        # Топ категория
        from sqlalchemy import func
        top_category_result = db.query(
            Category.name,
            func.count(TaskLog.id).label('count')
        ).join(Task).join(TaskLog).filter(
            TaskLog.user_id == db_user.id,
            TaskLog.status == "completed",
            TaskLog.created_at >= month_start
        ).group_by(Category.name).order_by(func.count(TaskLog.id).desc()).first()
        
        top_category = top_category_result[0] if top_category_result else "Нет данных"
        
        stats = {
            "today_completed": today_completed,
            "today_missed": today_missed,
            "today_percentage": today_percentage,
            "week_completed": week_completed,
            "week_missed": week_missed,
            "week_percentage": week_percentage,
            "month_completed": month_completed,
            "month_missed": month_missed,
            "month_percentage": month_percentage,
            "top_category": top_category,
            "current_streak": db_user.current_streak
        }
        
        message = MessageFormatter.format_stats(stats)
        await update.message.reply_text(message)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        db.close()


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📚 Доступные команды:

/add - Добавить новую задачу
/tasks - Показать активные задачи
/progress - Показать прогресс (XP, уровень, ачивки)
/stats - Статистика выполнения
/categories - Управление категориями
/help - Показать эту справку

💡 Просто напиши задачу в чат, и я её добавлю!
"""
    await update.message.reply_text(help_text)

