from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, security

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=schemas.TokenResponse)
def register(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password_hash=security.hash_password(payload.password),
        role="customer",
        opted_in=payload.opted_in,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = security.create_access_token({"user_id": user.id, "role": user.role})
    return {"access_token": token, "role": user.role}

@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not security.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = security.create_access_token({"user_id": user.id, "role": user.role})
    return {"access_token": token, "role": user.role}



from app.auth_dependency import get_current_user, require_restaurant

@router.get("/me")
def read_me(user=Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "role": user.role}

@router.get("/restaurant-only-test")
def restaurant_only(user=Depends(require_restaurant)):
    return {"message": f"Welcome, restaurant admin {user.name}"}