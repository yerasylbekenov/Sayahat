from dataclasses import dataclass
from typing import Optional

# Определение классов моделей для работы с данными
@dataclass
class User:
    user_id: int
    user_name: str
    email: str
    password: str
    payments: Optional[str]
    tours: Optional[str]
    basket: Optional[str]
    user_photo: Optional[str]
    balance: Optional[str]
    code: Optional[str]

@dataclass
class Tour:
    tour_id: int
    photos: Optional[str]
    name: str
    price: float
    cities: Optional[str]
    info: Optional[str]
    reviews: Optional[str]
    stars: Optional[float]

@dataclass
class Transaction:
    transaction_id: int
    user_id: int
    price: float
    date: str
    tours_id: Optional[int]

@dataclass
class City:
    city_id: int
    name: str
    hotels: Optional[str]
    info: Optional[str]
    places_to_visit: Optional[str]
    photo: Optional[str]

@dataclass
class Hotel:
    hotel_id: int
    name: str
    photo: Optional[str]
    price_per_person: float
    stars: Optional[float]
    city_id: int
