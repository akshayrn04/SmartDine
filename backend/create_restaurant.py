from app.database import SessionLocal
from app import models, security

db = SessionLocal()

existing = db.query(models.User).filter(models.User.role == "restaurant").first()
if existing:
    print("A restaurant account already exists:", existing.email)
else:
    restaurant = models.User(
        name="SmartDine Restaurant",
        email="restaurant@smartdine.com",
        phone=None,
        password_hash=security.hash_password("ChangeThisPassword123"),
        role="restaurant",
        opted_in=False,
    )
    db.add(restaurant)
    db.commit()
    print("Restaurant account created:", restaurant.email)

db.close()