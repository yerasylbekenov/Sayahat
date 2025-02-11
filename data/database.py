import sqlite3
from contextlib import contextmanager
from configs.config import DB_NAME
from utils.models import User, Tour, Transaction
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_name = DB_NAME
            cls._instance._create_tables()
        return cls._instance

    @contextmanager
    def _get_cursor(self):
        """Контекстный менеджер для получения курсора базы данных"""
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        cursor = conn.cursor()
        try:
            yield cursor
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.commit()
            conn.close()

    def _create_tables(self):
        """Создание таблиц в базе данных"""
        with self._get_cursor() as cursor:
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    payments TEXT,
                    tours TEXT,
                    basket TEXT,
                    user_photo TEXT DEFAULT 'https://i.ibb.co.com/MBszKW1/user-552721.png',
                    balance TEXT DEFAULT '0',
                    code TEXT
                );
                
                CREATE TABLE IF NOT EXISTS tours (
                    tour_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    photos TEXT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    cities TEXT,
                    info TEXT,
                    reviews TEXT,
                    stars REAL
                );
                
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    price REAL NOT NULL,
                    date TEXT NOT NULL,
                    tours_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (tours_id) REFERENCES tours (tours_id)
                );
                
                CREATE TABLE IF NOT EXISTS cities (
                    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    hotels TEXT,
                    info TEXT,
                    places_to_visit TEXT,
                    photo TEXT
                );
                
                CREATE TABLE IF NOT EXISTS hotels (
                    hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    photo TEXT,
                    price_per_person REAL NOT NULL,
                    stars REAL,
                    city_id INTEGER,
                    FOREIGN KEY (city_id) REFERENCES cities (city_id)
                );

                CREATE TABLE IF NOT EXISTS chat_history (
                    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                );
            ''')

    def save_chat_message(self, user_id: int, role: str, content: str):
        """Сохраняет сообщение в истории чата"""
        with self._get_cursor() as cursor:
            cursor.execute(
                'INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)',
                (user_id, role, content)
            )

    def load_chat_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Загружает историю чата для пользователя"""
        with self._get_cursor() as cursor:
            cursor.execute('SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY timestamp', (user_id,))
            rows = cursor.fetchall()
            return [{"role": row[0], "content": row[1]} for row in rows]

    # Остальные методы остаются без изменений
    # ...

    def get_user(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        with self._get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return User(*row) if row else None

    def add_user(self, **kwargs) -> bool:
        """Добавление пользователя в базу данных"""
        if self.get_user(kwargs["email"]):
            return False
        fields, values = zip(*kwargs.items())
        query = f'INSERT INTO users ({", ".join(fields)}) VALUES ({", ".join("?" * len(values))})'
        with self._get_cursor() as cursor:
            cursor.execute(query, values)
        return True

    def search_tours(self, search_term: str):
        """Поиск туров по названию или информации"""
        with self._get_cursor() as cursor:
            cursor.execute('SELECT * FROM tours WHERE name LIKE ? OR info LIKE ?', 
                        (f'%{search_term}%', f'%{search_term}%'))
            rows = cursor.fetchall()
            return [Tour(*row) for row in rows] if rows else []

    def add_tour(self, **kwargs):
        """Добавление тура в базу данных"""
        fields, values = zip(*kwargs.items())
        query = f'INSERT INTO tours ({", ".join(fields)}) VALUES ({", ".join("?" * len(values))})'
        with self._get_cursor() as cursor:
            cursor.execute(query, values)

    def get_all_tours(self):
        """Получение всех туров из базы данных"""
        with self._get_cursor() as cursor:
            cursor.execute('SELECT * FROM tours')
            rows = cursor.fetchall()
            return [Tour(*row) for row in rows] if rows else []

    def add_transaction(self, **kwargs):
        """Добавление транзакции в базу данных"""
        fields, values = zip(*kwargs.items())
        query = f'INSERT INTO transactions ({", ".join(fields)}) VALUES ({", ".join("?" * len(values))})'
        with self._get_cursor() as cursor:
            cursor.execute(query, values)

    def add_city(self, **kwargs):
        """Добавление города в базу данных"""
        fields, values = zip(*kwargs.items())
        query = f'INSERT INTO cities ({", ".join(fields)}) VALUES ({", ".join("?" * len(values))})'
        with self._get_cursor() as cursor:
            cursor.execute(query, values)

    def add_hotel(self, **kwargs):
        """Добавление отеля в базу данных"""
        fields, values = zip(*kwargs.items())
        query = f'INSERT INTO hotels ({", ".join(fields)}) VALUES ({", ".join("?" * len(values))})'
        with self._get_cursor() as cursor:
            cursor.execute(query, values)

    def update_record(self, table: str, id_column: str, record_id: int, **kwargs):
        """Обновление записи в таблице"""
        if not kwargs:
            return
        set_clause = ', '.join(f"{key} = ?" for key in kwargs)
        query = f'UPDATE {table} SET {set_clause} WHERE {id_column} = ?'
        params = list(kwargs.values()) + [record_id]
        with self._get_cursor() as cursor:
            cursor.execute(query, params)

    def get_record(self, table: str, id_column: str, record_id: int):
        """Получение записи из таблицы по ID"""
        with self._get_cursor() as cursor:
            cursor.execute(f'SELECT * FROM {table} WHERE {id_column} = ?', (record_id,))
            row = cursor.fetchone()
            if row and table == 'users':
                return User(*row)  # Преобразуем кортеж в объект User
            return row