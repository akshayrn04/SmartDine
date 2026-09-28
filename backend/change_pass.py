from app.database import SessionLocal
from app import models, security

db = SessionLocal()

restaurant = db.query(models.User).filter(models.User.role == "restaurant").first()
if not restaurant:
    print("No restaurant account found.")
else:
    new_password = "123456"
    restaurant.password_hash = security.hash_password(new_password)
    db.commit()
    print("Password updated for:", restaurant.email)

db.close()