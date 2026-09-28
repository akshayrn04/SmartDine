'''from fastapi import FastAPI
from app.database import engine, Base
from app import models

print("Tables Base knows about:", Base.metadata.tables.keys())
Base.metadata.create_all(bind=engine)
print("create_all finished running")

app = FastAPI(title="SmartDine API")

@app.get("/")
def root():
    return {"message": "SmartDine backend is running"}
'''
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.routes import auth
from app.routes import auth, bookings, restaurant, analytics, ai, campaigns



Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartDine API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "SmartDine backend is running"}

app.include_router(auth.router)
app.include_router(bookings.router)
app.include_router(restaurant.router)
app.include_router(analytics.router)
app.include_router(ai.router)
app.include_router(campaigns.router)