"""
Главный файл бота
"""
import asyncio
import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.database.db import init_db
from bot.handlers import commands, messages, callbacks
from bot.scheduler.reminder_scheduler import ReminderScheduler
from config.settings import settings

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Главная функция запуска бота"""
    # Инициализация БД
    logger.info("Инициализация базы данных...")
    init_db()
    
    # Создание приложения
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", commands.start_command))
    application.add_handler(CommandHandler("add", commands.add_task_command))
    application.add_handler(CommandHandler("tasks", commands.tasks_command))
    application.add_handler(CommandHandler("progress", commands.progress_command))
    application.add_handler(CommandHandler("stats", commands.stats_command))
    application.add_handler(CommandHandler("help", commands.help_command))
    
    # Обработчик текстовых сообщений (создание задач)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_message))
    
    # Обработчик callback-запросов (кнопки)
    application.add_handler(CallbackQueryHandler(callbacks.handle_callback))
    
    # Запуск планировщика напоминаний
    async def post_init(app: Application):
        bot = app.bot
        scheduler = ReminderScheduler(bot)
        scheduler.start()
        app.bot_data['scheduler'] = scheduler
    
    application.post_init = post_init
    
    # Запуск бота
    logger.info("Запуск бота...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

