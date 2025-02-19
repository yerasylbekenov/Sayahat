from dataclasses import dataclass
from typing import Optional
from datetime import datetime

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
    start_date: datetime
    end_date: datetime
    max_participants: int
    current_participants: int
    difficulty_level: Optional[str]  # Easy, Medium, Hard
    included_services: Optional[str]  # JSON string of included services
    meeting_point: Optional[str]
    requirements: Optional[str]  # Physical requirements, necessary equipment
    language: Optional[str]
    status: Optional[str]  # Active, Completed, Cancelled, Upcoming

@dataclass
class Transaction:
    transaction_id: int
    user_id: int
    price: float
    date: str
    tours_id: Optional[int]
    participants_count: int
    payment_status: str  # Pending, Completed, Refunded
    booking_date: datetime

@dataclass
class City:
    city_id: int
    name: str
    hotels: Optional[str]
    info: Optional[str]
    places_to_visit: Optional[str]
    photo: Optional[str]
    country: Optional[str]
    climate: Optional[str]
    best_time_to_visit: Optional[str]
    local_currency: Optional[str]

@dataclass
class Hotel:
    hotel_id: int
    name: str
    photo: Optional[str]
    price_per_person: float
    stars: Optional[float]
    city_id: int
    room_types: Optional[str]  # JSON string of available room types
    amenities: Optional[str]  # JSON string of hotel amenities
    check_in_time: Optional[str]
    check_out_time: Optional[str]
    total_rooms: int
    available_rooms: int

@dataclass
class TourParticipant:
    participant_id: int
    tour_id: int
    user_id: int
    booking_date: datetime
    status: str  # Confirmed, Cancelled, Waiting
    special_requirements: Optional[str]
    emergency_contact: Optional[str]
    payment_status: str