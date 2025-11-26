"""
Утилиты для форматирования сообщений
"""
from datetime import datetime
from typing import List, Optional
from bot.database.models import Task, User
from bot.gamification.xp_system import XPSystem


class MessageFormatter:
    """Форматирование сообщений для бота"""
    
    @staticmethod
    def format_task_list(tasks: List[Task]) -> str:
        """
        Форматирует список задач
        
        Args:
            tasks: Список задач
            
        Returns:
            Отформатированная строка
        """
        if not tasks:
            return "📋 У тебя пока нет активных задач. Добавь новую командой /add"
        
        # Группируем по категориям
        tasks_by_category = {}
        for task in tasks:
            category_name = task.category.name if task.category else "Без категории"
            if category_name not in tasks_by_category:
                tasks_by_category[category_name] = []
            tasks_by_category[category_name].append(task)
        
        # Формируем сообщение
        message = "🔥 Твои задачи на сегодня:\n\n"
        
        for category_name, category_tasks in tasks_by_category.items():
            emoji = category_tasks[0].category.emoji if category_tasks[0].category and category_tasks[0].category.emoji else "📌"
            message += f"{emoji} {category_name}:\n"
            
            for i, task in enumerate(category_tasks, 1):
                message += f"  {i}. {task.title}"
                
                # Добавляем прогресс, если есть
                if task.target_progress is not None:
                    progress_pct = (task.current_progress / task.target_progress * 100) if task.target_progress > 0 else 0
                    message += f" ({task.current_progress:.0f}/{task.target_progress:.0f} - {progress_pct:.0f}%)"
                
                # Добавляем дедлайн, если есть
                if task.deadline:
                    deadline_str = task.deadline.strftime("%d.%m.%Y")
                    message += f" [до {deadline_str}]"
                
                message += "\n"
            
            message += "\n"
        
        return message.strip()
    
    @staticmethod
    def format_progress(user: User) -> str:
        """
        Форматирует информацию о прогрессе пользователя
        
        Args:
            user: Пользователь
            
        Returns:
            Отформатированная строка
        """
        xp_in_level, xp_needed, percentage = XPSystem.get_progress_to_next_level(user.xp, user.level)
        progress_bar = XPSystem.format_progress_bar(percentage)
        
        message = f"""
🎮 Твой прогресс:

📊 Уровень: {user.level}
💎 XP: {user.xp} ({xp_in_level}/{xp_needed} до следующего уровня)
📈 Прогресс: {progress_bar} {percentage:.1f}%

🔥 Серия дней: {user.current_streak} (рекорд: {user.longest_streak})
⭐ Всего очков: {user.total_points}
"""
        return message.strip()
    
    @staticmethod
    def format_achievements(achievements: List) -> str:
        """
        Форматирует список ачивок
        
        Args:
            achievements: Список ачивок
            
        Returns:
            Отформатированная строка
        """
        if not achievements:
            return "🏆 У тебя пока нет ачивок. Выполняй задачи, чтобы получить их!"
        
        message = "🏆 Твои ачивки:\n\n"
        for ach in achievements:
            emoji = ach.achievement.emoji if ach.achievement.emoji else "🏅"
            message += f"{emoji} {ach.achievement.name}\n"
            if ach.achievement.description:
                message += f"   {ach.achievement.description}\n"
            message += f"   Получена: {ach.unlocked_at.strftime('%d.%m.%Y')}\n\n"
        
        return message.strip()
    
    @staticmethod
    def format_stats(stats: dict) -> str:
        """
        Форматирует статистику
        
        Args:
            stats: Словарь со статистикой
            
        Returns:
            Отформатированная строка
        """
        message = f"""
📊 Статистика:

📅 За сегодня:
   ✅ Выполнено: {stats.get('today_completed', 0)}
   ❌ Пропущено: {stats.get('today_missed', 0)}
   📈 Процент: {stats.get('today_percentage', 0):.1f}%

📆 За неделю:
   ✅ Выполнено: {stats.get('week_completed', 0)}
   ❌ Пропущено: {stats.get('week_missed', 0)}
   📈 Процент: {stats.get('week_percentage', 0):.1f}%

📆 За месяц:
   ✅ Выполнено: {stats.get('month_completed', 0)}
   ❌ Пропущено: {stats.get('month_missed', 0)}
   📈 Процент: {stats.get('month_percentage', 0):.1f}%

🏆 Топ категория: {stats.get('top_category', 'Нет данных')}
🔥 Серия дней: {stats.get('current_streak', 0)}
"""
        return message.strip()

