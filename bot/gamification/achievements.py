"""
Система ачивок
"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from bot.database.models import User, Achievement, UserAchievement, Task, TaskLog


class AchievementSystem:
    """Система проверки и выдачи ачивок"""
    
    @staticmethod
    def check_achievements(db: Session, user_id: int) -> List[Achievement]:
        """
        Проверяет и выдаёт новые ачивки пользователю
        
        Args:
            db: Сессия БД
            user_id: ID пользователя
            
        Returns:
            Список новых ачивок
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # Получаем все ачивки
        all_achievements = db.query(Achievement).all()
        new_achievements = []
        
        for achievement in all_achievements:
            # Проверяем, есть ли уже эта ачивка у пользователя
            existing = db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement.id
            ).first()
            
            if existing:
                continue
            
            # Проверяем условие
            if AchievementSystem._check_condition(db, user, achievement):
                # Выдаём ачивку
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
                db.add(user_achievement)
                
                # Начисляем XP
                user.xp += achievement.xp_reward
                
                new_achievements.append(achievement)
        
        if new_achievements:
            db.commit()
        
        return new_achievements
    
    @staticmethod
    def _check_condition(db: Session, user: User, achievement: Achievement) -> bool:
        """
        Проверяет условие ачивки
        
        Args:
            db: Сессия БД
            user: Пользователь
            achievement: Ачивка
            
        Returns:
            True, если условие выполнено
        """
        condition_type = achievement.condition_type
        
        if condition_type == "streak":
            # Серия дней
            required_streak = int(achievement.condition_value)
            return user.current_streak >= required_streak
        
        elif condition_type == "category_tasks":
            # Количество задач в категории
            try:
                condition_data = json.loads(achievement.condition_value)
                category_name = condition_data.get("category")
                required_count = condition_data.get("count", 0)
                
                completed_tasks = db.query(Task).join(TaskLog).filter(
                    Task.user_id == user.id,
                    Task.category.has(name=category_name),
                    TaskLog.status == "completed"
                ).count()
                
                return completed_tasks >= required_count
            except:
                return False
        
        elif condition_type == "category_streak":
            # Серия задач в категории
            try:
                condition_data = json.loads(achievement.condition_value)
                category_name = condition_data.get("category")
                required_streak = condition_data.get("streak", 0)
                
                # Получаем последние логи задач в категории
                logs = db.query(TaskLog).join(Task).filter(
                    Task.user_id == user.id,
                    Task.category.has(name=category_name)
                ).order_by(TaskLog.created_at.desc()).limit(required_streak).all()
                
                if len(logs) < required_streak:
                    return False
                
                # Проверяем, что все последние задачи выполнены
                return all(log.status == "completed" for log in logs)
            except:
                return False
        
        elif condition_type == "category_goal":
            # Достижение цели в категории
            try:
                condition_data = json.loads(achievement.condition_value)
                category_name = condition_data.get("category")
                
                # Проверяем, есть ли завершённые задачи с прогрессом >= 100%
                completed_goals = db.query(Task).filter(
                    Task.user_id == user.id,
                    Task.category.has(name=category_name),
                    Task.is_completed == True,
                    Task.target_progress.isnot(None),
                    Task.current_progress >= Task.target_progress
                ).count()
                
                return completed_goals > 0
            except:
                return False
        
        return False

