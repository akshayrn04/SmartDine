from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth_dependency import require_restaurant

from fastapi import HTTPException
from sqlalchemy.sql import func as sqlfunc

from app.notification_service import notify_booking_update

from app.routes.bookings import is_past


router = APIRouter(prefix="/api", tags=["restaurant"])


@router.get("/bookings", response_model=list[schemas.BookingOut])
def all_bookings(
    db: Session = Depends(get_db),
    _=Depends(require_restaurant),
):
    return db.query(models.Booking).order_by(models.Booking.date, models.Booking.slot_start).all()


@router.post("/seat-blocks", response_model=schemas.SeatBlockOut)
def block_seats(
    payload: schemas.SeatBlockCreate,
    db: Session = Depends(get_db),
    user=Depends(require_restaurant),
):
    block = models.SeatBlock(
        date=payload.date,
        slot_start=payload.slot_start,
        seats_blocked=payload.seats_blocked,
        reason=payload.reason,
        created_by=user.id,
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


@router.get("/customers", response_model=list[schemas.CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    _=Depends(require_restaurant),
):
    return db.query(models.User).filter(models.User.role == "customer").all()




@router.delete("/bookings/{booking_id}/restaurant-cancel")
def restaurant_cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_restaurant),
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    if is_past(booking.date, booking.slot_start):
        raise HTTPException(status_code=400, detail="Past bookings cannot be cancelled")
    
    booking.status = "CANCELLED"
    booking.cancelled_at = sqlfunc.now()

    customer = db.get(models.User, booking.user_id)
    notify_booking_update(
        db, customer,
        f"Hi {customer.name}, we're sorry. Your booking on {booking.date.strftime('%A, %B %d')} "
        f"at {booking.slot_start.strftime('%I:%M %p')} was cancelled by the restaurant.",
    )

    db.commit()
    return {"message": "Booking cancelled by restaurant", "booking_id": booking.id}