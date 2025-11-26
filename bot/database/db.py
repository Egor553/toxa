"""
Инициализация и управление базой данных
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from config.settings import settings
from bot.database.models import Base, Category, Achievement

# Создаём директорию для БД, если её нет
db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
if db_path.parent != Path("."):
    db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Инициализация базы данных"""
    Base.metadata.create_all(bind=engine)
    
    # Создаём категории по умолчанию
    db = SessionLocal()
    try:
        for cat_name in settings.DEFAULT_CATEGORIES:
            if not db.query(Category).filter(Category.name == cat_name).first():
                category = Category(name=cat_name)
                db.add(category)
        
        # Создаём базовые ачивки
        achievements_data = [
            {
                "name": "Железный",
                "description": "Серия 7 дней без пропусков",
                "emoji": "🔥",
                "condition_type": "streak",
                "condition_value": "7",
                "xp_reward": 50
            },
            {
                "name": "Манимейкер",
                "description": "10 закрытых задач по работе",
                "emoji": "💰",
                "condition_type": "category_tasks",
                "condition_value": '{"category": "Работа", "count": 10}',
                "xp_reward": 30
            },
            {
                "name": "Боец",
                "description": "5 тренировок подряд",
                "emoji": "💪",
                "condition_type": "category_streak",
                "condition_value": '{"category": "Тренировки", "streak": 5}',
                "xp_reward": 40
            },
            {
                "name": "Гроссмейстер внимания",
                "description": "Достиг цели по блогу",
                "emoji": "👑",
                "condition_type": "category_goal",
                "condition_value": '{"category": "Блог"}',
                "xp_reward": 60
            }
        ]
        
        for ach_data in achievements_data:
            if not db.query(Achievement).filter(Achievement.name == ach_data["name"]).first():
                achievement = Achievement(**ach_data)
                db.add(achievement)
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Ошибка при инициализации БД: {e}")
    finally:
        db.close()


def get_db() -> Session:
    """Получить сессию БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

