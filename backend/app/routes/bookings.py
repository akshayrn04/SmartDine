from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models, schemas
from app.auth_dependency import get_current_user
from datetime import date as date_cls, timedelta
from datetime import datetime, date as date_cls, timedelta
from app.notification_service import notify_booking_update
from datetime import datetime, date as date_cls, time as time_cls, timedelta

BOOKING_WINDOW_DAYS = 7  

def is_past(d, slot_start) -> bool:
    return datetime.combine(d, slot_start) < datetime.now()



router = APIRouter(prefix="/api", tags=["bookings"])


def get_available_seats(db: Session, date_, slot_start) -> dict:
    settings = db.query(models.RestaurantSettings).first()
    if not settings:
        raise HTTPException(status_code=500, detail="Restaurant settings not configured")

    booked = (
        db.query(func.coalesce(func.sum(models.Booking.party_size), 0))
        .filter(
            models.Booking.date == date_,
            models.Booking.slot_start == slot_start,
            models.Booking.status == "CONFIRMED",
        )
        .scalar()
    )
    blocked = (
        db.query(func.coalesce(func.sum(models.SeatBlock.seats_blocked), 0))
        .filter(models.SeatBlock.date == date_, models.SeatBlock.slot_start == slot_start)
        .scalar()
    )
    available = settings.total_seats - booked - blocked
    return {
        "total_seats": settings.total_seats,
        "booked_seats": booked,
        "blocked_seats": blocked,
        "available_seats": available,
    }


@router.get("/availability", response_model=schemas.AvailabilityOut)
def check_availability(date: str, slot_start: str, db: Session = Depends(get_db)):
    from datetime import date as date_cls, time as time_cls
    d = date_cls.fromisoformat(date)
    t = time_cls.fromisoformat(slot_start)
    result = get_available_seats(db, d, t)
    return {"date": d, "slot_start": t, **result}


@router.post("/bookings", response_model=schemas.BookingOut)
def create_booking(
    payload: schemas.BookingCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    today = date_cls.today()
    max_date = today + timedelta(days=BOOKING_WINDOW_DAYS)

    if payload.date < today:
        raise HTTPException(status_code=400, detail="Cannot book a date in the past")
    if payload.date > max_date:
        raise HTTPException(status_code=400, detail=f"Bookings can only be made up to {BOOKING_WINDOW_DAYS} days ahead")

    # Lock the settings row so two simultaneous bookings can't both pass the check
    db.query(models.RestaurantSettings).with_for_update().first()

    result = get_available_seats(db, payload.date, payload.slot_start)
    if payload.party_size > result["available_seats"]:
        raise HTTPException(status_code=400, detail="Not enough seats available for this slot")

    booking = models.Booking(
        user_id=user.id,
        date=payload.date,
        slot_start=payload.slot_start,
        party_size=payload.party_size,
        status="CONFIRMED",
    )

    db.add(booking)
    db.flush()   # gives the booking an id without finishing the save yet

    # Feedback: was this customer sent a campaign for this exact slot?
    notification = (
        db.query(models.Notification)
        .join(models.Campaign, models.Campaign.id == models.Notification.campaign_id)
        .outerjoin(models.Response, models.Response.notification_id == models.Notification.id)
        .filter(
            models.Notification.user_id == user.id,
            models.Notification.status == "SENT",
            models.Campaign.target_date == payload.date,
            models.Campaign.slot_start == payload.slot_start,
            models.Response.id.is_(None),
        )
        .first()
    )
    if notification:
        db.add(models.Response(notification_id=notification.id, booked=True, booking_id=booking.id))

    notify_booking_update(
        db, user,
        f"Hi {user.name}, your table for {payload.party_size} on {payload.date.strftime('%A, %B %d')} "
        f"at {payload.slot_start.strftime('%I:%M %p')} is confirmed.",
    )

    db.commit()
    db.refresh(booking)
    return booking


@router.get("/bookings/me", response_model=list[schemas.BookingOut])
def my_bookings(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return (
        db.query(models.Booking)
        .filter(models.Booking.user_id == user.id)
        .order_by(models.Booking.date, models.Booking.slot_start)
        .all()
    )


@router.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    from sqlalchemy.sql import func as sqlfunc

    booking = (
        db.query(models.Booking)
        .filter(models.Booking.id == booking_id, models.Booking.user_id == user.id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    
    if is_past(booking.date, booking.slot_start):
        raise HTTPException(status_code=400, detail="Past bookings cannot be cancelled")

    booking.status = "CANCELLED"
    booking.cancelled_at = sqlfunc.now()
    db.commit()
    return {"message": "Booking cancelled"}


@router.get("/availability/day", response_model=list[schemas.AvailabilityOut])
def day_availability(
    date: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    d = date_cls.fromisoformat(date)
    settings = db.query(models.RestaurantSettings).first()
    if not settings:
        raise HTTPException(status_code=500, detail="Restaurant settings not configured")

    slots = []
    current = datetime.combine(d, settings.open_time)
    end = datetime.combine(d, settings.close_time)
    step = timedelta(minutes=settings.slot_length_minutes)
    while current < end:
        t = current.time()
        slots.append({"date": d, "slot_start": t, **get_available_seats(db, d, t)})
        current += step
    return slots