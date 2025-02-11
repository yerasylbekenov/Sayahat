from gigachat import GigaChat
from configs import config
from datetime import datetime
import re
import logging
from typing import List, Dict, Optional, Set, Tuple
from utils.models import Tour, City, Hotel
from data import database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GigaChatClient:
    def __init__(self):
        self.auth_key = config.AUTH_KEY
        self.verify_ssl = False
        self.db = database.Database()
        
        # Log initialization
        logger.info(f"GigaChatClient initialized with auth key present: {bool(self.auth_key)}")
        
        # Системный промпт для задания контекста
        self.system_prompt = """
        Вы - ассистент онлайн-платформы Sayahat для покупки туров. Ваша задача - помогать пользователям 
        найти идеальный тур, основываясь на их предпочтениях и интересах. Анализируйте их запросы
        и предлагайте наиболее подходящие варианты из нашей базы данных. Вы не можете бронировать тур для человека.
        Вам нельзя отвечать на вопросы связанные остальными темами это очень строго запрещен. Вам еще нельзя говорить про туры в других странах это строго запрещен.
        """
        
        # Расширенные категории и их связи
        self.categories = {
            'mountains': {
                'patterns': r'\b(горы|вершины|пик|альпинизм|треккинг|поход)\b',
                'keywords': ['горный', 'альпинистский', 'треккинг'],
                'locations': ['Алматы', 'Медеу', 'Шымбулак', 'Талгар', 'Большое Алматинское озеро'],
                'activities': ['треккинг', 'скалолазание', 'походы', 'фотографирование'],
                'related_categories': ['nature', 'adventure']
            },
            'lakes': {
                'patterns': r'\b(озеро|озёра|побережье|пляж)\b',
                'keywords': ['озерный', 'прибрежный'],
                'locations': ['Борабай', 'Алаколь', 'Балхаш', 'Кольсай', 'Каинды'],
                'activities': ['плавание', 'рыбалка', 'отдых', 'кемпинг'],
                'related_categories': ['nature', 'relax']
            },
            'culture': {
                'patterns': r'\b(музей|история|культура|традиции|юрта|мавзолей)\b',
                'keywords': ['исторический', 'культурный', 'традиционный'],
                'locations': ['Туркестан', 'Отрар', 'Тараз', 'Астана'],
                'activities': ['экскурсии', 'мастер-классы', 'дегустации'],
                'related_categories': ['history', 'city']
            },
            'adventure': {
                'patterns': r'\b(рафтинг|каньон|сафари|джип-тур|квадроциклы)\b',
                'keywords': ['экстремальный', 'приключенческий', 'активный'],
                'locations': ['Чарынский каньон', 'Тургеньское ущелье', 'Капчагай'],
                'activities': ['рафтинг', 'джип-туры', 'скалолазание'],
                'related_categories': ['nature', 'sport']
            },
            'nature': {
                'patterns': r'\b(природа|парк|заповедник|флора|фауна|степь)\b',
                'keywords': ['природный', 'экологический', 'заповедный'],
                'locations': ['Аксу-Жабаглы', 'Алтын-Эмель', 'Бурабай'],
                'activities': ['наблюдение за птицами', 'фотоохота', 'экскурсии'],
                'related_categories': ['mountains', 'lakes']
            }
        }

    def test_connection(self) -> bool:
        """Тестирует подключение к GigaChat"""
        try:
            with GigaChat(credentials=self.auth_key, 
                         model="GigaChat-Pro", 
                         verify_ssl_certs=self.verify_ssl) as giga:
                test_response = giga.chat("Test connection")
                success = bool(test_response and test_response.choices)
                logger.info(f"GigaChat connection test {'successful' if success else 'failed'}")
                return success
        except Exception as e:
            logger.error(f"GigaChat connection test failed with error: {str(e)}")
            return False

    def analyze_preferences(self, message: str) -> Dict[str, float]:
        """Анализирует предпочтения пользователя из сообщения"""
        logger.info(f"🔍 Анализируем предпочтения по сообщению: {message}")

        preferences = {}

        for category, data in self.categories.items():
            pattern_matches = len(re.findall(data['patterns'], message, re.I))
            keyword_matches = sum(1 for keyword in data['keywords'] 
                                if keyword.lower() in message.lower())
            location_matches = sum(1 for location in data['locations'] 
                                if location.lower() in message.lower())
            activity_matches = sum(1 for activity in data['activities'] 
                                if activity.lower() in message.lower())

            total_score = (pattern_matches * 2 + 
                        keyword_matches * 1.5 + 
                        location_matches * 2 + 
                        activity_matches * 1.5)

            if total_score > 0:
                preferences[category] = total_score
                for related in data['related_categories']:
                    preferences[related] = preferences.get(related, 0) + total_score * 0.5

            logger.info(f"📊 {category}: {total_score} баллов")

        logger.info(f"✅ Итоговые предпочтения: {preferences}")
        return preferences


    def get_relevant_locations(self, preferences: Dict[str, float]) -> Set[str]:
        """Получает релевантные локации на основе предпочтений"""
        locations = set()
        for category, score in preferences.items():
            if category in self.categories:
                locations.update(self.categories[category]['locations'])
        logger.info(f"Found relevant locations: {locations}")
        return locations

    def get_relevant_activities(self, preferences: Dict[str, float]) -> Set[str]:
        """Получает релевантные активности на основе предпочтений"""
        activities = set()
        for category, score in preferences.items():
            if category in self.categories:
                activities.update(self.categories[category]['activities'])
        logger.info(f"Found relevant activities: {activities}")
        return activities

    def search_locations(self, locations: Set[str]) -> List[Tuple[City, float]]:
        """Ищет информацию о городах и достопримечательностях"""
        logger.info(f"Searching locations: {locations}")
        results = []
        
        try:
            with self.db._get_cursor() as cursor:
                for location in locations:
                    cursor.execute('''
                        SELECT *, 
                               CASE 
                                   WHEN name LIKE ? THEN 2
                                   WHEN info LIKE ? THEN 1
                               END as relevance
                        FROM cities 
                        WHERE name LIKE ? OR info LIKE ?
                        ORDER BY relevance DESC
                    ''', (f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%'))
                    
                    rows = cursor.fetchall()
                    for row in rows:
                        city_data = list(row[:-1])
                        relevance = row[-1]
                        results.append((City(*city_data), float(relevance)))
            
            logger.info(f"Found {len(results)} locations")
            return results
            
        except Exception as e:
            logger.error(f"Error in search_locations: {str(e)}")
            return []

    def get_relevant_tours(self, preferences: Dict[str, float], locations: Set[str]) -> List[Tuple[Tour, float]]:
        """Получает релевантные туры на основе предпочтений и локаций"""
        logger.info(f"🔎 Поиск туров с предпочтениями: {preferences}")
        logger.info(f"📍 Локации: {locations}")

        results = []
        try:
            with self.db._get_cursor() as cursor:
                conditions = []
                params = []
                
                if locations:
                    location_conditions = []
                    for location in locations:
                        location_conditions.extend([
                            "cities LIKE ?",
                            "info LIKE ?"
                        ])
                        params.extend([f'%{location}%', f'%{location}%'])
                    if location_conditions:
                        conditions.append(f"({' OR '.join(location_conditions)})")
                
                category_conditions = []
                for category, score in preferences.items():
                    if category in self.categories:
                        for keyword in self.categories[category]['keywords']:
                            category_conditions.extend([
                                "name LIKE ?",
                                "info LIKE ?"
                            ])
                            params.extend([f'%{keyword}%', f'%{keyword}%'])
                
                if category_conditions:
                    conditions.append(f"({' OR '.join(category_conditions)})")
                
                query = '''
                    SELECT *, 
                        (CASE 
                            WHEN stars IS NOT NULL THEN stars * 0.3
                            ELSE 0 
                        END +
                        CASE 
                            WHEN reviews IS NOT NULL THEN 0.2
                            ELSE 0
                        END) as relevance
                    FROM tours
                '''
                
                if conditions:
                    query += f" WHERE {' AND '.join(conditions)}"
                
                query += " ORDER BY relevance DESC LIMIT 2"
                
                logger.info(f"📝 SQL-запрос:\n{query}")
                logger.info(f"📌 Параметры: {params}")
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                for row in rows:
                    tour_data = list(row[:-1])
                    relevance = row[-1]
                    results.append((Tour(*tour_data), float(relevance)))

                logger.info(f"✅ Найдено туров: {len(results)}")
                return results
                
        except Exception as e:
            logger.error(f"⚠ Ошибка в get_relevant_tours: {str(e)}")
            return []


    def format_location_info(self, city: City, relevance: float) -> str:
        """Форматирует информацию о локации в Markdown"""
        try:
            info = f"## 🏛 {city.name}\n"
            if relevance > 1.5:
                info += "_(Идеально подходит!)_\n\n"
            
            if city.info:
                info += f"**Описание**: {city.info}\n\n"
            
            if city.places_to_visit:
                places = city.places_to_visit.split(",")
                info += f"📍 **Интересные места:**\n- " + "\n- ".join(places) + "\n\n"
            
            if city.hotels:
                hotels = city.hotels.split(",")
                info += f"🏨 **Где остановиться:**\n- " + "\n- ".join(hotels) + "\n\n"
            
            return info
        except Exception as e:
            logger.error(f"Error formatting location info: {str(e)}")
            return ""

    def format_tour_suggestion(self, tour: Tour) -> str:
        """Форматирует предложение тура в Markdown"""
        try:
            tour_link = f"/tour/{tour.tour_id}"
            
            suggestion = f"### 🎯 [{tour.name}]({tour_link})\n"

            if tour.photos:
                suggestion += f'\n<img src="{tour.photos}" width="300" height="200" style="object-fit: cover;">\n'
            
            suggestion += f"\n💰 **Стоимость**: {tour.price:,.0f} тенге\n"

            if tour.stars:
                stars = "⭐" * int(tour.stars)
                suggestion += f"**Рейтинг**: {stars} ({tour.stars:.1f})\n"
            
            if tour.cities:
                suggestion += f"\n🏛 **Города**: {tour.cities}\n"
            
            if tour.info:
                suggestion += f"\nℹ️ **Описание**: {tour.info}\n"
            
            if tour.reviews:
                suggestion += f"\n👥 **Отзывы**: {tour.reviews}\n"
            
            suggestion += f"\n🔗 **[Перейти к туру]({tour_link})**\n"
            
            return suggestion
        except Exception as e:
            logger.error(f"Error formatting tour suggestion: {str(e)}")
            return ""

    def chat_with_context(self, user_id: int, message: str) -> str:
        """Отправляет сообщение в GigaChat с учетом контекста"""
        try:
            logger.info(f"💬 Получено сообщение от пользователя {user_id}: {message}")

            history = [{"role": "system", "content": self.system_prompt}]
            chat_history = self.db.load_chat_history(user_id)

            if chat_history:
                logger.info(f"📜 Загруженная история чата ({len(chat_history)} сообщений):")
                for msg in chat_history[-5:]:
                    logger.info(f"{msg['role']}: {msg['content']}")

                history.extend(chat_history[-5:])

            history.append({"role": "user", "content": message})

            combined_message = "\n".join([
                f"{msg['role']}: {msg['content']}" for msg in history
            ])

            logger.info(f"📤 Отправляемый контекст в GigaChat:\n{combined_message}")

            with GigaChat(credentials=self.auth_key, 
                        model="GigaChat-Pro", 
                        verify_ssl_certs=self.verify_ssl) as giga:
                response = giga.chat(combined_message)

                if not response or not response.choices:
                    logger.error("❌ Пустой ответ от GigaChat")
                    return "Извините, произошла ошибка при обработке запроса."

                response_text = response.choices[0].message.content
                logger.info(f"✅ Ответ от GigaChat:\n{response_text}")

                return response_text

        except Exception as e:
            logger.error(f"⚠ Ошибка в chat_with_context: {str(e)}")
            return "Извините, произошла техническая ошибка. Мы уже работаем над её устранением."


    def process_message(self, user_id: int, message: str) -> str:
        """Обрабатывает сообщение пользователя и формирует ответ в Markdown"""
        preferences = self.analyze_preferences(message)
        locations = self.get_relevant_locations(preferences)
        activities = self.get_relevant_activities(preferences)
        
        base_response = self.chat_with_context(user_id, message)
        
        response_parts = [f"## 🤖 Ваш персональный ассистент\n\n{base_response}\n"]
        
        if locations:
            location_info = self.search_locations(locations)
            if location_info:
                response_parts.append("## 📍 Подходящие места для путешествия:\n")
                for city, relevance in sorted(location_info, key=lambda x: x[1], reverse=True)[:3]:
                    response_parts.append(self.format_location_info(city, relevance))
        
        if "тур" in message.lower() or "путешествие" in message.lower():
            relevant_tours = self.get_relevant_tours(preferences, locations)
            if relevant_tours:
                response_parts.append("## 🎯 Рекомендованные туры:\n")
                for tour, relevance in sorted(relevant_tours, key=lambda x: x[1], reverse=True):
                    response_parts.append(self.format_tour_suggestion(tour))

        
        if activities:
            response_parts.append("## 🎡 Рекомендуемые активности:\n")
            response_parts.append("- " + "\n- ".join(activities))
        
        final_response = "\n".join(response_parts)
        
        self.db.save_chat_message(user_id, "user", message)
        self.db.save_chat_message(user_id, "assistant", final_response)
        
        return final_response


    def format_tour_suggestion(self, tour: Tour) -> str:
        """Форматирует предложение тура в Markdown с фото и ссылкой"""
        tour_link = f"/tour/{tour.tour_id}"
        
        suggestion = f"### 🎯 [{tour.name}]({tour_link})\n"

        if tour.photos:
            suggestion += f'\n<img src="{tour.photos}" width="300" height="200" style="object-fit: cover;">\n'
        
        suggestion += f"\n💰 **Стоимость**: {tour.price:,.0f} тенге\n"

        if tour.stars:
            stars = "\n⭐" * int(tour.stars)
            suggestion += f"**Рейтинг**: {stars} ({tour.stars:.1f})\n"
        
        if tour.cities:
            suggestion += f"\n🏛 **Города**: {tour.cities}\n"
        
        if tour.info:
            suggestion += f"\nℹ️ **Описание**: {tour.info}\n"
        
        if tour.reviews:
            suggestion += f"\n👥 **Отзывы**: {tour.reviews}\n"
        

        
        suggestion += f"\n🔗 **[Перейти к туру]({tour_link})**\n"
        
        return suggestion


    def chat_with_context(self, user_id: int, message: str) -> str:
        """Отправляет сообщение в GigaChat с учетом контекста"""
        try:
            history = [{"role": "system", "content": self.system_prompt}]
            chat_history = self.db.load_chat_history(user_id)
            
            if chat_history:
                history.extend(chat_history[-5:])
            
            history.append({"role": "user", "content": message})
            
            combined_message = "\n".join([
                f"{msg['role']}: {msg['content']}" for msg in history
            ])

            with GigaChat(credentials=self.auth_key, 
                         model="GigaChat", 
                         verify_ssl_certs=self.verify_ssl) as giga:
                response = giga.chat(combined_message)
                return response.choices[0].message.content if response.choices else \
                       "Извините, произошла ошибка при обработке запроса."
                
        except Exception as e:
            logger.error(f"Ошибка при запросе к GigaChat: {e}")
            return "Извините, сейчас я испытываю технические трудности. Попробуйте повторить запрос позже."