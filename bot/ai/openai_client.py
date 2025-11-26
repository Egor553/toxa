"""
Клиент для работы с OpenAI API
"""
import json
import re
import random
from typing import Optional, Dict, List
from config.settings import settings

# Пытаемся импортировать OpenAI (опционально)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

# Инициализируем клиент только если есть ключ и библиотека установлена
client = None
if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
    except:
        pass

# Заглушки для мотивационных сообщений
MOTIVATION_COMPLETED = [
    "Живой, дерзкий, вот так надо работать! 🔥",
    "Красавчик, уровень растёт! 💪",
    "Огонь! Продолжай в том же духе! ⚡",
    "Ты в ударе! Так держать! 🚀",
    "Мощно! Идёшь к цели! 🎯",
    "Красота! Ещё одна победа! 🏆",
    "Безбашенно! Так и надо! 💥",
    "Жёстко! Ты на правильном пути! 🔥"
]

MOTIVATION_MISSED = [
    "Слабина? Исправим. Поехали дальше! 💪",
    "Бывает. Главное - не сдавайся! 🚀",
    "Ничего страшного. Завтра будет лучше! ⭐",
    "Окей, пропустил. Но не останавливайся! 🔥",
    "Бывает. Важно не сбиться с пути! 💎",
    "Ничего, завтра наверстаешь! 🎯"
]


class AIClient:
    """Клиент для работы с ИИ"""
    
    @staticmethod
    def categorize_task(task_text: str, available_categories: List[str]) -> str:
        """
        Определяет категорию задачи с помощью ИИ или простых правил
        
        Args:
            task_text: Текст задачи
            available_categories: Список доступных категорий
            
        Returns:
            Название категории
        """
        # Если нет клиента OpenAI, используем простые правила
        if not client:
            return AIClient._categorize_by_keywords(task_text, available_categories)
        
        categories_str = ", ".join(available_categories)
        
        prompt = f"""Определи категорию для следующей задачи. 
Доступные категории: {categories_str}

Задача: "{task_text}"

Верни ТОЛЬКО название категории, без дополнительных объяснений."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты помощник для категоризации задач. Отвечай только названием категории."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            category = response.choices[0].message.content.strip()
            
            # Проверяем, что категория есть в списке
            if category in available_categories:
                return category
            
            # Если нет точного совпадения, ищем похожую
            for cat in available_categories:
                if cat.lower() in category.lower() or category.lower() in cat.lower():
                    return cat
            
            # Если ничего не найдено, используем правила
            return AIClient._categorize_by_keywords(task_text, available_categories)
            
        except Exception as e:
            print(f"Ошибка при категоризации (используем правила): {e}")
            return AIClient._categorize_by_keywords(task_text, available_categories)
    
    @staticmethod
    def _categorize_by_keywords(task_text: str, available_categories: List[str]) -> str:
        """
        Простая категоризация по ключевым словам (fallback)
        """
        task_lower = task_text.lower()
        
        # Ключевые слова для категорий
        keywords = {
            "Тренировки": ["тренировка", "тренировк", "кардио", "спорт", "бег", "зал", "фитнес", "упражнен", "качаться"],
            "Блог": ["блог", "сторис", "пост", "контент", "публикация", "подписчик", "подписчик"],
            "Работа": ["работа", "задача", "проект", "встреча", "звонок", "клиент", "лид", "продаж"],
            "Продажи": ["продаж", "лид", "клиент", "сделка", "контракт", "договор"],
            "Команда": ["команда", "сотрудник", "коллега", "встреча", "совещание"],
            "Чтение": ["читать", "книга", "статья", "обучение", "изучение"],
            "Лайвы": ["лайв", "стрим", "эфир", "трансляция"],
            "Личное развитие": ["развитие", "навык", "курс", "обучение", "саморазвитие"]
        }
        
        # Ищем совпадения
        for category, words in keywords.items():
            if category in available_categories:
                for word in words:
                    if word in task_lower:
                        return category
        
        # Если ничего не найдено, возвращаем "Работа" по умолчанию
        return "Работа" if "Работа" in available_categories else (available_categories[0] if available_categories else "Работа")
    
    @staticmethod
    def parse_task(task_text: str) -> Dict:
        """
        Парсит текст задачи и извлекает информацию
        
        Args:
            task_text: Текст задачи
            
        Returns:
            Словарь с полями: title, category, current_progress, target_progress, deadline
        """
        # Если нет клиента OpenAI, используем простой парсинг
        if not client:
            return AIClient._parse_task_simple(task_text)
        
        prompt = f"""Проанализируй следующую задачу и извлеки информацию в формате JSON:
{{
    "title": "краткое название задачи",
    "current_progress": число или null,
    "target_progress": число или null,
    "deadline": "дата в формате YYYY-MM-DD или null"
}}

Задача: "{task_text}"

Верни ТОЛЬКО JSON, без дополнительного текста."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты помощник для парсинга задач. Отвечай только валидным JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Убираем markdown форматирование, если есть
            result_text = re.sub(r'```json\n?', '', result_text)
            result_text = re.sub(r'```\n?', '', result_text)
            
            parsed = json.loads(result_text)
            return parsed
            
        except Exception as e:
            print(f"Ошибка при парсинге задачи (используем простой парсинг): {e}")
            return AIClient._parse_task_simple(task_text)
    
    @staticmethod
    def _parse_task_simple(task_text: str) -> Dict:
        """
        Простой парсинг задачи без ИИ (fallback)
        """
        import re
        from datetime import datetime, timedelta
        
        result = {
            "title": task_text,
            "current_progress": None,
            "target_progress": None,
            "deadline": None
        }
        
        # Пытаемся найти прогресс в формате "я на X из Y" или "X/Y"
        progress_patterns = [
            r'я на (\d+)',
            r'на (\d+)',
            r'(\d+)\s*/\s*(\d+)',
            r'(\d+)\s*из\s*(\d+)',
            r'(\d+)\s*до\s*(\d+)'
        ]
        
        for pattern in progress_patterns:
            match = re.search(pattern, task_text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    result["current_progress"] = float(match.group(1))
                    result["target_progress"] = float(match.group(2))
                elif len(match.groups()) == 1:
                    result["current_progress"] = float(match.group(1))
                break
        
        # Пытаемся найти цель в формате "цель: X" или "X подписчиков"
        goal_patterns = [
            r'цель[:\s]+(\d+)',
            r'(\d+)\s+подписчик',
            r'(\d+)\s+кг',
            r'(\d+)\s+минут'
        ]
        
        if not result["target_progress"]:
            for pattern in goal_patterns:
                match = re.search(pattern, task_text, re.IGNORECASE)
                if match:
                    result["target_progress"] = float(match.group(1))
                    if not result["current_progress"]:
                        result["current_progress"] = 0.0
                    break
        
        # Упрощаем название, убирая технические детали
        title = task_text
        # Убираем фразы типа "хочу цель:", "добавь" и т.д.
        title = re.sub(r'^(хочу\s+цель|добавь|добавить|нужна\s+цель)[:\s]*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'я\s+на\s+\d+.*?$', '', title, flags=re.IGNORECASE)
        title = title.strip()
        
        if title:
            result["title"] = title
        
        return result
    
    @staticmethod
    def generate_motivation_message(is_completed: bool, task_title: str, user_level: int) -> str:
        """
        Генерирует мотивационное сообщение
        
        Args:
            is_completed: Выполнена ли задача
            task_title: Название задачи
            user_level: Уровень пользователя
            
        Returns:
            Мотивационное сообщение
        """
        # Если нет клиента OpenAI, используем заглушки
        if not client:
            if is_completed:
                return random.choice(MOTIVATION_COMPLETED)
            else:
                return random.choice(MOTIVATION_MISSED)
        
        if is_completed:
            prompt = f"""Сгенерируй короткое мотивационное сообщение (1-2 предложения) в стиле поколения Z, 
дерзкое и живое, для пользователя уровня {user_level}, который только что выполнил задачу "{task_title}".

Примеры стиля:
- "Живой, дерзкий, вот так надо работать."
- "Красавчик, уровень растёт."
- "Огонь! Продолжай в том же духе."

Верни ТОЛЬКО текст сообщения, без кавычек."""
        else:
            prompt = f"""Сгенерируй короткое мотивационное сообщение (1-2 предложения) в стиле поколения Z, 
дерзкое и поддерживающее, для пользователя уровня {user_level}, который не выполнил задачу "{task_title}".

Примеры стиля:
- "Слабина? Исправим. Поехали дальше."
- "Бывает. Главное - не сдавайся."

Верни ТОЛЬКО текст сообщения, без кавычек."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты мотивационный коуч в стиле поколения Z. Отвечай коротко и дерзко."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Ошибка при генерации мотивации (используем заглушки): {e}")
            if is_completed:
                return random.choice(MOTIVATION_COMPLETED)
            else:
                return random.choice(MOTIVATION_MISSED)

