from datetime import date as date_cls, datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models, schemas
from app.auth_dependency import require_restaurant
from app.routes.bookings import get_available_seats

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=schemas.DashboardOut)
def dashboard(db: Session = Depends(get_db), _=Depends(require_restaurant)):
    today = date_cls.today()
    settings = db.query(models.RestaurantSettings).first()

    todays_bookings = db.query(models.Booking).filter(models.Booking.date == today).all()
    confirmed = [b for b in todays_bookings if b.status == "CONFIRMED"]
    cancelled = [b for b in todays_bookings if b.status == "CANCELLED"]
    seats_booked_today = sum(b.party_size for b in confirmed)

    # Build one row per distinct booked/blocked slot today, showing live availability
    slot_times = sorted(set(b.slot_start for b in confirmed))
    slots = []
    for t in slot_times:
        result = get_available_seats(db, today, t)
        slots.append({"date": today, "slot_start": t, **result})

    return {
        "date": today,
        "total_bookings_today": len(confirmed),
        "total_seats_booked_today": seats_booked_today,
        "cancellations_today": len(cancelled),
        "total_seats": settings.total_seats if settings else 0,
        "slots": slots,
    }


@router.get("/occupancy")
def occupancy_trend(
    days: int = 7,
    db: Session = Depends(get_db),
    _=Depends(require_restaurant),
):
    """Booked seats per day for the last N days, plus a simple occupancy %."""
    settings = db.query(models.RestaurantSettings).first()
    total_seats = settings.total_seats if settings else 1

    today = date_cls.today()
    results = []
    for i in range(days):
        d = today - timedelta(days=i)
        booked = (
            db.query(func.coalesce(func.sum(models.Booking.party_size), 0))
            .filter(models.Booking.date == d, models.Booking.status == "CONFIRMED")
            .scalar()
        )
        results.append({
            "date": d,
            "seats_booked": booked,
            "total_seats": total_seats,
        })
    return list(reversed(results))


@router.get("/cancellation-rate")
def cancellation_rate(db: Session = Depends(get_db), _=Depends(require_restaurant)):
    total = db.query(func.count(models.Booking.id)).scalar()
    cancelled = (
        db.query(func.count(models.Booking.id))
        .filter(models.Booking.status == "CANCELLED")
        .scalar()
    )
    rate = (cancelled / total * 100) if total else 0
    return {"total_bookings": total, "cancelled": cancelled, "cancellation_rate_percent": round(rate, 2)}




@router.get("/campaigns")
def campaign_results(db: Session = Depends(get_db), _=Depends(require_restaurant)):
    results = []
    campaigns = db.query(models.Campaign).order_by(models.Campaign.created_at.desc()).all()
    for c in campaigns:
        targeted = (
            db.query(func.count(models.Notification.id))
            .filter(models.Notification.campaign_id == c.id)
            .scalar()
        )
        booked = (
            db.query(func.count(models.Response.id))
            .join(models.Notification, models.Notification.id == models.Response.notification_id)
            .filter(models.Notification.campaign_id == c.id, models.Response.booked == True)
            .scalar()
        )
        results.append({
            "campaign_id": c.id,
            "status": c.status,
            "target_date": c.target_date,
            "slot_start": c.slot_start,
            "offer_type": c.offer_type,
            "customers_targeted": targeted,
            "bookings_generated": booked,
            "conversion_rate_percent": round(booked / targeted * 100, 1) if targeted else 0,
        })
    return results