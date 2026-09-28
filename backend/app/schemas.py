from pydantic import BaseModel, EmailStr
from datetime import date, time as time_type

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    password: str
    opted_in: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class BookingCreate(BaseModel):
    date: date
    slot_start: time_type
    party_size: int

class BookingOut(BaseModel):
    id: int
    date: date
    slot_start: time_type
    party_size: int
    status: str

    class Config:
        from_attributes = True

class AvailabilityOut(BaseModel):
    date: date
    slot_start: time_type
    total_seats: int
    booked_seats: int
    blocked_seats: int
    available_seats: int

#------------------------- Resturant -----------

class SeatBlockCreate(BaseModel):
    date: date
    slot_start: time_type
    seats_blocked: int
    reason: str | None = None

class SeatBlockOut(BaseModel):
    id: int
    date: date
    slot_start: time_type
    seats_blocked: int
    reason: str | None

    class Config:
        from_attributes = True

class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    opted_in: bool

    class Config:
        from_attributes = True

class DashboardOut(BaseModel):
    date: date
    total_bookings_today: int
    total_seats_booked_today: int
    cancellations_today: int
    total_seats: int
    slots: list[AvailabilityOut]

class PredictionOut(BaseModel):
    date: date
    slot_start: time_type
    predicted_occupancy: float
    predicted_seats: int



class CampaignCreate(BaseModel):
    target_date: date
    slot_start: time_type

class CampaignOut(BaseModel):
    id: int
    target_date: date
    slot_start: time_type
    predicted_occupancy: str
    offer_type: str
    offer_value: str | None
    status: str

    class Config:
        from_attributes = True

class NotificationOut(BaseModel):
    id: int
    user_id: int
    message_text: str
    status: str

    class Config:
        from_attributes = True