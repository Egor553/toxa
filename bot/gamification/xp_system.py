"""
Система опыта и уровней
"""
from typing import Tuple
from config.settings import settings


class XPSystem:
    """Система начисления XP и уровней"""
    
    @staticmethod
    def calculate_xp_for_task(base_xp: int = None, multiplier: float = None) -> int:
        """
        Рассчитывает XP за задачу
        
        Args:
            base_xp: Базовое количество XP
            multiplier: Множитель
            
        Returns:
            Количество XP
        """
        if base_xp is None:
            base_xp = settings.XP_PER_TASK
        if multiplier is None:
            multiplier = settings.XP_MULTIPLIER
        
        return int(base_xp * multiplier)
    
    @staticmethod
    def calculate_level(xp: int) -> int:
        """
        Рассчитывает уровень на основе XP
        
        Формула: level = floor(sqrt(xp / BASE_XP)) + 1
        
        Args:
            xp: Текущий опыт
            
        Returns:
            Уровень
        """
        import math
        if xp <= 0:
            return 1
        
        level = int(math.sqrt(xp / settings.LEVEL_UP_BASE_XP)) + 1
        return max(1, level)
    
    @staticmethod
    def get_xp_for_level(level: int) -> int:
        """
        Получить минимальный XP для уровня
        
        Args:
            level: Уровень
            
        Returns:
            Минимальный XP
        """
        import math
        if level <= 1:
            return 0
        
        return int((level - 1) ** 2 * settings.LEVEL_UP_BASE_XP)
    
    @staticmethod
    def get_xp_for_next_level(level: int) -> int:
        """
        Получить XP, необходимое для следующего уровня
        
        Args:
            level: Текущий уровень
            
        Returns:
            XP для следующего уровня
        """
        return XPSystem.get_xp_for_level(level + 1)
    
    @staticmethod
    def get_progress_to_next_level(current_xp: int, current_level: int) -> Tuple[int, int, float]:
        """
        Получить прогресс до следующего уровня
        
        Args:
            current_xp: Текущий XP
            current_level: Текущий уровень
            
        Returns:
            Кортеж (текущий XP в уровне, XP до следующего уровня, процент)
        """
        xp_for_current = XPSystem.get_xp_for_level(current_level)
        xp_for_next = XPSystem.get_xp_for_level(current_level + 1)
        
        xp_in_level = current_xp - xp_for_current
        xp_needed = xp_for_next - xp_for_current
        
        if xp_needed == 0:
            percentage = 100.0
        else:
            percentage = (xp_in_level / xp_needed) * 100
        
        return xp_in_level, xp_needed, percentage
    
    @staticmethod
    def format_progress_bar(percentage: float, length: int = 10) -> str:
        """
        Форматирует прогресс-бар
        
        Args:
            percentage: Процент (0-100)
            length: Длина прогресс-бара
            
        Returns:
            Строка прогресс-бара
        """
        filled = int(length * percentage / 100)
        empty = length - filled
        
        return "▓" * filled + "▒" * empty

