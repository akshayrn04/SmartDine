from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models

def find_suitable_customers(db: Session, target_date, slot_start, limit: int = 20) -> list[models.User]:
    weekday = target_date.weekday()
    hour = slot_start.hour

    # Customers who have booked this weekday/hour combo before, and are opted in
    candidates = (
        db.query(models.User)
        .join(models.Booking, models.Booking.user_id == models.User.id)
        .filter(
            models.User.role == "customer",
            models.User.opted_in == True,
            func.extract("dow", models.Booking.date) == weekday,
            func.extract("hour", models.Booking.slot_start) == hour,
        )
        .group_by(models.User.id)
        .order_by(func.count(models.Booking.id).desc())
        .limit(limit)
        .all()
    )
    return candidates