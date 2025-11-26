"""
Планировщик напоминаний
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from sqlalchemy.orm import Session
from bot.database.db import get_db
from bot.database.models import Reminder, User, Task
from bot.ai.openai_client import AIClient
from telegram import Bot
from config.settings import settings
import pytz


class ReminderScheduler:
    """Планировщик напоминаний"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone(settings.TIMEZONE))
    
    def start(self):
        """Запускает планировщик"""
        # Загружаем напоминания из БД
        self._load_reminders()
        
        # Запускаем ежедневную проверку задач
        self.scheduler.add_job(
            self._send_daily_tasks,
            CronTrigger(hour=9, minute=0),  # Каждый день в 9:00
            id="daily_tasks"
        )
        
        self.scheduler.start()
    
    def stop(self):
        """Останавливает планировщик"""
        self.scheduler.shutdown()
    
    def _load_reminders(self):
        """Загружает напоминания из БД и добавляет их в планировщик"""
        db = next(get_db())
        try:
            reminders = db.query(Reminder).filter(Reminder.is_active == True).all()
            
            for reminder in reminders:
                self._schedule_reminder(reminder)
        finally:
            db.close()
    
    def _schedule_reminder(self, reminder: Reminder):
        """Добавляет напоминание в планировщик"""
        time_parts = reminder.time.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        if reminder.days_of_week:
            # Напоминание в определённые дни недели
            days = [int(d) for d in reminder.days_of_week.split(",")]
            trigger = CronTrigger(day_of_week=days, hour=hour, minute=minute)
        else:
            # Ежедневное напоминание
            trigger = CronTrigger(hour=hour, minute=minute)
        
        self.scheduler.add_job(
            self._send_reminder,
            trigger,
            args=[reminder.id],
            id=f"reminder_{reminder.id}",
            replace_existing=True
        )
    
    async def _send_reminder(self, reminder_id: int):
        """Отправляет напоминание"""
        db = next(get_db())
        try:
            reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
            if not reminder or not reminder.is_active:
                return
            
            user = reminder.user
            message = reminder.message
            
            # Если есть задача, добавляем информацию о ней
            if reminder.task_id:
                task = reminder.task
                message += f"\n\n📌 {task.title}"
                if task.deadline:
                    message += f"\n📅 Дедлайн: {task.deadline.strftime('%d.%m.%Y')}"
            
            # Генерируем мотивационное сообщение
            motivation = AIClient.generate_motivation_message(True, "напоминание", user.level)
            message += f"\n\n{motivation}"
            
            await self.bot.send_message(
                chat_id=user.telegram_id,
                text=message
            )
            
            # Обновляем время последней отправки
            reminder.last_sent = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            print(f"Ошибка при отправке напоминания: {e}")
        finally:
            db.close()
    
    async def _send_daily_tasks(self):
        """Отправляет ежедневный список задач"""
        db = next(get_db())
        try:
            users = db.query(User).all()
            
            for user in users:
                # Получаем активные задачи
                active_tasks = db.query(Task).filter(
                    Task.user_id == user.id,
                    Task.is_active == True,
                    Task.is_completed == False
                ).all()
                
                if not active_tasks:
                    continue
                
                from bot.utils.formatters import MessageFormatter
                message = MessageFormatter.format_task_list(active_tasks)
                
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message
                )
                
        except Exception as e:
            print(f"Ошибка при отправке ежедневных задач: {e}")
        finally:
            db.close()

