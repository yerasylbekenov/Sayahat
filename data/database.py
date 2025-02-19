import sqlite3
from contextlib import contextmanager
from configs.config import DB_NAME
from utils.models import User, Tour, Transaction, TourParticipant
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

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
        conn.row_factory = sqlite3.Row  # Enable row factory for named columns
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
                    stars REAL,
                    start_date DATETIME NOT NULL,
                    end_date DATETIME NOT NULL,
                    max_participants INTEGER NOT NULL,
                    current_participants INTEGER DEFAULT 0,
                    difficulty_level TEXT,
                    included_services TEXT,
                    meeting_point TEXT,
                    requirements TEXT,
                    language TEXT DEFAULT 'Russian',
                    status TEXT DEFAULT 'Upcoming'
                );
                
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    price REAL NOT NULL,
                    date TEXT NOT NULL,
                    tours_id INTEGER,
                    participants_count INTEGER NOT NULL DEFAULT 1,
                    payment_status TEXT DEFAULT 'Pending',
                    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (tours_id) REFERENCES tours (tours_id)
                );
                
                CREATE TABLE IF NOT EXISTS cities (
                    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    hotels TEXT,
                    info TEXT,
                    places_to_visit TEXT,
                    photo TEXT,
                    country TEXT,
                    climate TEXT,
                    best_time_to_visit TEXT,
                    local_currency TEXT
                );
                
                CREATE TABLE IF NOT EXISTS hotels (
                    hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    photo TEXT,
                    price_per_person REAL NOT NULL,
                    stars REAL,
                    city_id INTEGER,
                    room_types TEXT,
                    amenities TEXT,
                    check_in_time TEXT,
                    check_out_time TEXT,
                    total_rooms INTEGER,
                    available_rooms INTEGER,
                    FOREIGN KEY (city_id) REFERENCES cities (city_id)
                );

                CREATE TABLE IF NOT EXISTS tour_participants (
                    participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tour_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Waiting',
                    special_requirements TEXT,
                    emergency_contact TEXT,
                    payment_status TEXT DEFAULT 'Pending',
                    FOREIGN KEY (tour_id) REFERENCES tours (tour_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
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

    def get_tour_participants(self, tour_id: int) -> List[TourParticipant]:
        """Получение списка участников тура"""
        with self._get_cursor() as cursor:
            cursor.execute('SELECT * FROM tour_participants WHERE tour_id = ?', (tour_id,))
            return [TourParticipant(**dict(row)) for row in cursor.fetchall()]

    def add_tour_participant(self, **kwargs) -> bool:
        """Добавление участника в тур"""
        with self._get_cursor() as cursor:
            # Проверяем количество текущих участников
            cursor.execute('SELECT current_participants, max_participants FROM tours WHERE tour_id = ?', 
                         (kwargs['tour_id'],))
            current, maximum = cursor.fetchone()
            
            if current >= maximum:
                return False
            
            # Добавляем участника
            fields, values = zip(*kwargs.items())
            query = f'INSERT INTO tour_participants ({", ".join(fields)}) VALUES ({", ".join("?" * len(values))})'
            cursor.execute(query, values)
            
            # Обновляем количество участников в туре
            cursor.execute('UPDATE tours SET current_participants = current_participants + 1 WHERE tour_id = ?',
                         (kwargs['tour_id'],))
            return True

    def get_active_tours(self, user_id: int) -> List[Tour]:
        """Получение активных туров пользователя"""
        with self._get_cursor() as cursor:
            cursor.execute('''
                SELECT t.* FROM tours t
                JOIN tour_participants tp ON t.tour_id = tp.tour_id
                WHERE tp.user_id = ? AND t.status = 'Active'
            ''', (user_id,))
            return [Tour(**dict(row)) for row in cursor.fetchall()]

    def get_upcoming_tours(self, user_id: int) -> List[Tour]:
        """Получение предстоящих туров пользователя"""
        with self._get_cursor() as cursor:
            cursor.execute('''
                SELECT t.* FROM tours t
                JOIN tour_participants tp ON t.tour_id = tp.tour_id
                WHERE tp.user_id = ? AND t.status = 'Upcoming'
            ''', (user_id,))
            return [Tour(**dict(row)) for row in cursor.fetchall()]
    
    def get_completed_tours(self, user_id: int):
        with self._get_cursor() as cursor:
            cursor.execute('''
                SELECT t.* FROM tours t
                JOIN tour_participants tp ON t.tour_id = tp.tour_id
                WHERE tp.user_id = ? AND t.status = 'Completed'
            ''', (user_id,))
            return [Tour(**dict(row)) for row in cursor.fetchall()]

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