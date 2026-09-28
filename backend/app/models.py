from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import Date, Time, ForeignKey


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)          # "customer" or "restaurant"
    opted_in = Column(Boolean, default=False)       # agreed to receive offers?
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RestaurantSettings(Base):
    __tablename__ = "restaurant_settings"

    id = Column(Integer, primary_key=True, index=True)
    total_seats = Column(Integer, nullable=False)
    slot_length_minutes = Column(Integer, nullable=False, default=60)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)


class SeatBlock(Base):
    __tablename__ = "seat_blocks"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    slot_start = Column(Time, nullable=False)
    seats_blocked = Column(Integer, nullable=False)
    reason = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    slot_start = Column(Time, nullable=False)
    party_size = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="CONFIRMED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    target_date = Column(Date, nullable=False)
    slot_start = Column(Time, nullable=False)
    predicted_occupancy = Column(String, nullable=False)   # stored as text for simplicity, e.g. "0.220"
    offer_type = Column(String, nullable=False)             # NONE, DISCOUNT_PERCENT, FIXED_DISCOUNT, FREEBIE, LOYALTY_POINTS
    offer_value = Column(String, nullable=True)
    message_template = Column(String, nullable=True)
    status = Column(String, nullable=False, default="PENDING_APPROVAL")  # PENDING_APPROVAL, APPROVED, REJECTED, SENT
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    type = Column(String, nullable=False, default="CAMPAIGN")   # CAMPAIGN or BOOKING_UPDATE
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_text = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING")   # PENDING, SENT, FAILED
    sent_at = Column(DateTime(timezone=True), nullable=True)

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    responded_at = Column(DateTime(timezone=True), server_default=func.now())
    booked = Column(Boolean, default=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)