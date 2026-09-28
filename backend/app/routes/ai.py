from datetime import date as date_cls, time as time_cls, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth_dependency import require_restaurant
from app.ai.predictor import predict_occupancy

router = APIRouter(prefix="/api/ai", tags=["ai"])

SLOT_HOURS = list(range(12, 22))   # 12:00 to 21:00, matches generate_data.py


@router.get("/predictions", response_model=list[schemas.PredictionOut])
def get_predictions(
    days_ahead: int = 7,
    db: Session = Depends(get_db),
    _=Depends(require_restaurant),
):
    settings = db.query(models.RestaurantSettings).first()
    total_seats = settings.total_seats if settings else 10

    results = []
    today = date_cls.today()
    for i in range(1, days_ahead + 1):
        target_date = today + timedelta(days=i)
        for hour in SLOT_HOURS:
            occ = predict_occupancy(target_date, hour)
            results.append({
                "date": target_date,
                "slot_start": time_cls(hour, 0),
                "predicted_occupancy": round(occ, 3),
                "predicted_seats": round(occ * total_seats),
            })
    return results