"""
Настройки приложения
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/bot.db")
    
    # Геймификация
    XP_PER_TASK: int = int(os.getenv("XP_PER_TASK", "10"))
    XP_MULTIPLIER: float = float(os.getenv("XP_MULTIPLIER", "1.0"))
    LEVEL_UP_BASE_XP: int = int(os.getenv("LEVEL_UP_BASE_XP", "100"))
    
    # Напоминания
    DEFAULT_REMINDER_TIME: str = os.getenv("DEFAULT_REMINDER_TIME", "18:00")
    TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Moscow")
    
    # Категории по умолчанию
    DEFAULT_CATEGORIES: list = [
        "Работа",
        "Тренировки",
        "Блог",
        "Продажи",
        "Команда",
        "Чтение",
        "Лайвы",
        "Личное развитие"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

