"""
Обработчики callback-запросов (кнопки)
"""
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from bot.database.db import get_db
from bot.database.models import User, Task, TaskLog
from bot.ai.openai_client import AIClient
from bot.gamification.xp_system import XPSystem
from bot.gamification.achievements import AchievementSystem


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback-запросов"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        if not db_user:
            await query.edit_message_text("❌ Пользователь не найден. Используй /start")
            return
        
        if data.startswith("complete_"):
            task_id = int(data.split("_")[1])
            await _handle_task_complete(db, db_user, task_id, query)
        
        elif data.startswith("miss_"):
            task_id = int(data.split("_")[1])
            await _handle_task_miss(db, db_user, task_id, query)
        
    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка: {e}")
    finally:
        db.close()


async def _handle_task_complete(db: Session, user: User, task_id: int, query):
    """Обработка выполнения задачи"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        await query.edit_message_text("❌ Задача не найдена")
        return
    
    if task.is_completed:
        await query.edit_message_text("✅ Эта задача уже выполнена!")
        return
    
    # Отмечаем задачу как выполненную
    task.is_completed = True
    task.completed_at = datetime.utcnow()
    
    # Обновляем прогресс, если есть цель
    if task.target_progress:
        task.current_progress = task.target_progress
    
    # Начисляем XP
    xp_earned = XPSystem.calculate_xp_for_task()
    user.xp += xp_earned
    user.total_points += xp_earned
    
    # Обновляем уровень
    new_level = XPSystem.calculate_level(user.xp)
    level_up = new_level > user.level
    user.level = new_level
    
    # Обновляем серию дней
    _update_streak(db, user, True)
    
    # Создаём лог
    task_log = TaskLog(
        user_id=user.id,
        task_id=task.id,
        status="completed",
        xp_earned=xp_earned,
        points_earned=xp_earned
    )
    db.add(task_log)
    
    # Проверяем ачивки
    new_achievements = AchievementSystem.check_achievements(db, user.id)
    
    db.commit()
    
    # Генерируем мотивационное сообщение
    motivation = AIClient.generate_motivation_message(True, task.title, user.level)
    
    # Формируем ответ
    response = f"✅ Задача выполнена!\n\n"
    response += f"💎 +{xp_earned} XP\n"
    
    if level_up:
        response += f"🎉 УРОВЕНЬ ПОВЫШЕН! Теперь ты уровня {user.level}!\n\n"
    
    response += f"{motivation}\n\n"
    
    if new_achievements:
        response += "🏆 Новая ачивка:\n"
        for ach in new_achievements:
            emoji = ach.emoji if ach.emoji else "🏅"
            response += f"{emoji} {ach.name} - {ach.description}\n"
        response += "\n"
    
    xp_in_level, xp_needed, percentage = XPSystem.get_progress_to_next_level(user.xp, user.level)
    progress_bar = XPSystem.format_progress_bar(percentage)
    response += f"📊 Прогресс: {progress_bar} {percentage:.1f}%"
    
    await query.edit_message_text(response)


async def _handle_task_miss(db: Session, user: User, task_id: int, query):
    """Обработка пропуска задачи"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        await query.edit_message_text("❌ Задача не найдена")
        return
    
    # Обновляем серию дней
    _update_streak(db, user, False)
    
    # Создаём лог
    task_log = TaskLog(
        user_id=user.id,
        task_id=task.id,
        status="missed",
        xp_earned=0,
        points_earned=0
    )
    db.add(task_log)
    
    db.commit()
    
    # Генерируем мотивационное сообщение
    motivation = AIClient.generate_motivation_message(False, task.title, user.level)
    
    response = f"❌ Задача отмечена как невыполненная\n\n"
    response += f"{motivation}\n\n"
    response += f"🔥 Серия дней: {user.current_streak}"
    
    await query.edit_message_text(response)


def _update_streak(db: Session, user: User, completed: bool):
    """Обновляет серию дней пользователя"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Получаем последний лог
    last_log = db.query(TaskLog).filter(
        TaskLog.user_id == user.id
    ).order_by(TaskLog.created_at.desc()).first()
    
    if completed:
        if last_log and last_log.created_at >= today_start:
            # Уже была активность сегодня
            if last_log.status == "completed":
                # Серия продолжается
                pass
            else:
                # Серия сброшена, начинаем заново
                user.current_streak = 1
        else:
            # Первая активность сегодня
            if last_log:
                last_log_date = last_log.created_at.replace(hour=0, minute=0, second=0, microsecond=0)
                yesterday = today_start - timedelta(days=1)
                
                if last_log_date == yesterday:
                    # Вчера была активность, продолжаем серию
                    user.current_streak += 1
                elif last_log_date < yesterday:
                    # Пропуск дней, сбрасываем серию
                    user.current_streak = 1
                else:
                    # Серия продолжается
                    pass
            else:
                # Первая активность вообще
                user.current_streak = 1
    else:
        # Задача не выполнена - сбрасываем серию
        user.current_streak = 0
    
    # Обновляем рекорд
    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak

