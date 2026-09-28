from datetime import time
from app.database import SessionLocal
from app import models

db = SessionLocal()

existing = db.query(models.RestaurantSettings).first()
if existing:
    print("Settings already exist:", existing.total_seats, "seats")
else:
    settings = models.RestaurantSettings(
        total_seats=10,
        slot_length_minutes=60,
        open_time=time(12, 0),
        close_time=time(22, 0),
    )
    db.add(settings)
    db.commit()
    print("Settings created:", settings.total_seats, "seats")

db.close()