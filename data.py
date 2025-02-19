import pymongo
from pymongo import MongoClient
from hashlib import bcrypt
import uuid
from datetime import datetime

# Подключение к MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['game_db']  # Название базы данных
users_collection = db['users']
matches_collection = db['matches']
news_collection = db['news']

class Database:
    """Класс для взаимодействия с базой данных MongoDB"""

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['game_db']
        self.users_collection = self.db['users']
        self.matches_collection = self.db['matches']
        self.news_collection = self.db['news']

class User:
    """Класс для пользователя"""

    def __init__(self, user_id=None, email=None, password=None, username=None, avatar_url=None, playstyle=None):
        self.user_id = user_id or str(uuid.uuid4())  # Генерация уникального ID
        self.email = email
        self.password = password
        self.username = username
        self.avatar_url = avatar_url
        self.playstyle = playstyle
        self.created_at = datetime.utcnow()
        self.last_login = self.created_at
        self.rank = 'Bronze'
        self.xp = 0
        self.wins = 0
        self.losses = 0
        self.matches_played = 0
        self.win_rate = 0
        self.friends = []
        self.clan_id = None
        self.status = 'Offline'

    def hash_password(self):
        """Хеширует пароль пользователя"""
        return bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())

    def save(self):
        """Сохраняет пользователя в базе данных"""
        hashed_password = self.hash_password()
        user_data = {
            'user_id': self.user_id,
            'email': self.email,
            'password': hashed_password,
            'username': self.username,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'avatar_url': self.avatar_url,
            'rank': self.rank,
            'xp': self.xp,
            'wins': self.wins,
            'losses': self.losses,
            'matches_played': self.matches_played,
            'win_rate': self.win_rate,
            'playstyle': self.playstyle,
            'friends': self.friends,
            'clan_id': self.clan_id,
            'status': self.status
        }

        users_collection.insert_one(user_data)

    @staticmethod
    def get_by_id(user_id):
        """Получить пользователя по ID"""
        user_data = users_collection.find_one({'user_id': user_id})
        if user_data:
            return User(**user_data)
        return None

    def update_stats(self, wins=None, losses=None, matches_played=None, xp=None, rank=None):
        """Обновляет статистику пользователя"""
        update_data = {}

        if wins is not None:
            update_data['wins'] = self.wins + wins
        if losses is not None:
            update_data['losses'] = self.losses + losses
        if matches_played is not None:
            update_data['matches_played'] = self.matches_played + matches_played
        if xp is not None:
            update_data['xp'] = self.xp + xp
        if rank is not None:
            update_data['rank'] = rank

        if update_data:
            users_collection.update_one({'user_id': self.user_id}, {'$set': update_data})
            self.__dict__.update(update_data)  # Обновить атрибуты объекта

class Match:
    """Класс для матча"""

    def __init__(self, match_id=None, players=None, rank_range=None):
        self.match_id = match_id or str(uuid.uuid4())  # Генерация уникального ID для матча
        self.players = players or []
        self.status = 'waiting'  # Статус матча
        self.rank_range = rank_range
        self.created_at = datetime.utcnow()
        self.result = None

    def save(self):
        """Сохраняет матч в базе данных"""
        match_data = {
            '_id': self.match_id,
            'players': self.players,
            'status': self.status,
            'rank_range': self.rank_range,
            'created_at': self.created_at,
            'result': self.result
        }
        matches_collection.insert_one(match_data)

    @staticmethod
    def get_by_id(match_id):
        """Получить матч по ID"""
        match_data = matches_collection.find_one({'_id': match_id})
        if match_data:
            return Match(**match_data)
        return None

class News:
    """Класс для новостей"""

    def __init__(self, news_id=None, title=None, content=None, type='announcement', author_id=None, image_url=None, related_match_id=None):
        self.news_id = news_id or str(uuid.uuid4())
        self.title = title
        self.content = content
        self.created_at = datetime.utcnow()
        self.type = type
        self.author_id = author_id
        self.is_active = True
        self.image_url = image_url
        self.related_match_id = related_match_id

    def save(self):
        """Сохраняет новость в базе данных"""
        news_data = {
            '_id': self.news_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at,
            'type': self.type,
            'author_id': self.author_id,
            'is_active': self.is_active,
            'image_url': self.image_url,
            'related_match_id': self.related_match_id
        }
        news_collection.insert_one(news_data)

    @staticmethod
    def get_all():
        """Получить все активные новости"""
        return news_collection.find({'is_active': True}).sort('created_at', pymongo.DESCENDING)

# Пример использования
if __name__ == '__main__':
    # Создание нового пользователя
    user = User(email='user@example.com', password='password123', username='PlayerOne')
    user.save()
    print(f"New user created: {user.username}")

    # Создание нового матча
    match = Match(players=[user.user_id], rank_range={"min": 1000, "max": 1500})
    match.save()
    print(f"New match created: {match.match_id}")

    # Добавление новости
    news = News(title="Новое обновление", content="Обновление с новым контентом!")
    news.save()
    print(f"New news added: {news.title}")
