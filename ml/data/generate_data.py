import random
from datetime import date, timedelta, time
import sys
import os

# Let this script import from the backend app
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.database import SessionLocal
from app import models

db = SessionLocal()

settings = db.query(models.RestaurantSettings).first()
if not settings:
    print("Run setup_settings.py in backend/ first.")
    exit()

TOTAL_SEATS = settings.total_seats
SLOT_TIMES = [time(h, 0) for h in range(12, 22)]   # 12:00 to 21:00, one slot per hour
START_DATE = date.today() - timedelta(days=180)     # 6 months of history
END_DATE = date.today() - timedelta(days=1)          # up to yesterday

# Make sure we have some fake customers to attach bookings to
existing_customers = db.query(models.User).filter(models.User.role == "customer").all()
if len(existing_customers) < 20:
    from app import security
    for i in range(20 - len(existing_customers)):
        c = models.User(
            name=f"Test Customer {i}",
            email=f"fake_customer_{i}@example.com",
            password_hash=security.hash_password("password123"),
            role="customer",
            opted_in=random.choice([True, True, False]),  # mostly opted in
        )
        db.add(c)
    db.commit()
    existing_customers = db.query(models.User).filter(models.User.role == "customer").all()

def demand_chance(d: date, slot: time) -> float:
    """Returns a 0-1 'busyness' score based on realistic patterns."""
    weekday = d.weekday()   # 0=Monday ... 5=Saturday, 6=Sunday
    is_weekend = weekday in (4, 5)          # Fri, Sat busier
    is_dinner = slot.hour >= 18             # dinner hours busier than afternoon
    base = 0.35
    if is_weekend:
        base += 0.25
    if is_dinner:
        base += 0.25
    if weekday == 1:                        # Tuesdays are quiet
        base -= 0.15
    return max(0.05, min(base, 0.95))

created = 0
current = START_DATE
while current <= END_DATE:
    for slot in SLOT_TIMES:
        chance = demand_chance(current, slot)
        seats_filled = 0
        # Keep adding small party bookings until the slot is roughly as full as 'chance' suggests
        target_fill = int(TOTAL_SEATS * chance)
        while seats_filled < target_fill:
            party_size = random.choice([1, 2, 2, 3, 4])
            if seats_filled + party_size > TOTAL_SEATS:
                break
            status = "CONFIRMED"
            if random.random() < 0.08:      # ~8% cancellation rate
                status = "CANCELLED"
            customer = random.choice(existing_customers)
            booking = models.Booking(
                user_id=customer.id,
                date=current,
                slot_start=slot,
                party_size=party_size,
                status=status,
            )
            db.add(booking)
            if status == "CONFIRMED":
                seats_filled += party_size
            created += 1
    current += timedelta(days=1)

db.commit()
print(f"Created {created} historical bookings from {START_DATE} to {END_DATE}.")
db.close()