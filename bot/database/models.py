"""
Модели базы данных
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Геймификация
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    total_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)  # Текущая серия дней
    longest_streak = Column(Integer, default=0)  # Самая длинная серия
    
    # Связи
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    task_logs = relationship("TaskLog", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    """Модель категории"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    emoji = Column(String(10), nullable=True)  # Эмодзи для категории
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    tasks = relationship("Task", back_populates="category")


class Task(Base):
    """Модель задачи"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Прогресс
    current_progress = Column(Float, default=0.0)  # Текущий прогресс
    target_progress = Column(Float, nullable=True)  # Целевой прогресс
    
    # Статус
    is_completed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # Активна ли задача
    
    # Временные метки
    deadline = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")


class TaskLog(Base):
    """Лог выполнения задач"""
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    
    status = Column(String(20), nullable=False)  # "completed" или "missed"
    xp_earned = Column(Integer, default=0)
    points_earned = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="task_logs")
    task = relationship("Task", back_populates="logs")


class Achievement(Base):
    """Модель ачивки"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    emoji = Column(String(10), nullable=True)
    condition_type = Column(String(50), nullable=False)  # "streak", "tasks_count", "category", etc.
    condition_value = Column(String(200), nullable=False)  # JSON или строка
    xp_reward = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user_achievements = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    """Связь пользователя и ачивки"""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")


class Reminder(Base):
    """Модель напоминания"""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # Если None - общее напоминание
    
    message = Column(Text, nullable=False)
    time = Column(String(10), nullable=False)  # Формат "HH:MM"
    days_of_week = Column(String(20), nullable=True)  # "1,2,3,4,5" для пн-пт
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sent = Column(DateTime, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="reminders")

