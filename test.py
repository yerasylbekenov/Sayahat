from data import database
from datetime import datetime, timedelta
import random

# Инициализация базы данных
db = database.Database()

# Данные для городов
cities_data = [
    {"name": "Алматы", "hotels": "Отель Казахстан", "info": "Крупнейший город Казахстана", "places_to_visit": "Медео, Шымбулак", "photo": "", "country": "Казахстан", "climate": "Континентальный", "best_time_to_visit": "Весна и осень", "local_currency": "Тенге"},
    {"name": "Казахстан", "hotels": "", "info": "Страна Центральной Азии", "places_to_visit": "Астана, Байконур", "photo": "", "country": "Казахстан", "climate": "Резкоконтинентальный", "best_time_to_visit": "Лето", "local_currency": "Тенге"}
]

# Добавление городов в базу данных
city_ids = {}
for city in cities_data:
    db.add_city(**city)
    city_record = db.get_record("cities", "name", city["name"])
    if city_record:
        city_ids[city["name"]] = city_record["city_id"]  # Доступ через ["ключ"]

# Данные для туров
tours_data = [
    {
        "name": "Горы Алатау",
        "price": 150.0,
        "cities": city_ids["Алматы"],
        "info": "Путешествие по живописным горам Казахстана",
        "reviews": "",
        "stars": 4.7,
        "start_date": (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
        "end_date": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S'),
        "max_participants": 15,
        "difficulty_level": "Средний",
        "included_services": "Трансфер, питание, экскурсии",
        "meeting_point": "Аэропорт Алматы",
        "requirements": "Спортивная одежда",
        "language": "Russian",
        "status": "Upcoming"
    },
    {
        "name": "Озеро Каинды",
        "price": 100.0,
        "cities": city_ids["Казахстан"],
        "info": "Прогулка к мистическому затопленному лесу",
        "reviews": "",
        "stars": 4.5,
        "start_date": (datetime.now() + timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S'),
        "end_date": (datetime.now() + timedelta(days=23)).strftime('%Y-%m-%d %H:%M:%S'),
        "max_participants": 10,
        "difficulty_level": "Лёгкий",
        "included_services": "Гид, питание, транспорт",
        "meeting_point": "Центр Алматы",
        "requirements": "Тёплая одежда",
        "language": "Russian",
        "status": "Upcoming"
    }
]

# Добавление туров в базу данных
for tour in tours_data:
    db.add_tour(**tour)
    tour_id = db.get_all_tours()[-1].tour_id  # Получаем ID только что добавленного тура
    num_participants = random.randint(5, tour["max_participants"])  # Генерируем случайное число участников
    
    for _ in range(num_participants):
        participant = {
            "tour_id": tour_id,
            "user_id": random.randint(1, 100),  # Генерация случайного пользователя
            "special_requirements": "",
            "emergency_contact": "+77001234567",
            "payment_status": "Paid"
        }
        db.add_tour_participant(**participant)
    
    print(f"Тур '{tour['name']}' успешно добавлен с {num_participants} участниками!")
