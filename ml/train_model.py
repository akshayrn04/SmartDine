import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

import pandas as pd
from datetime import date
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

from app.database import SessionLocal
from app import models

db = SessionLocal()
settings = db.query(models.RestaurantSettings).first()
TOTAL_SEATS = settings.total_seats

# 1. Load all confirmed bookings into a table Pandas can work with
bookings = db.query(models.Booking).filter(models.Booking.status == "CONFIRMED").all()
rows = [{"date": b.date, "slot_start": b.slot_start, "party_size": b.party_size} for b in bookings]
df = pd.DataFrame(rows)
db.close()

# 2. Aggregate to one row per (date, slot): total seats filled that slot
grouped = df.groupby(["date", "slot_start"])["party_size"].sum().reset_index()
grouped.rename(columns={"party_size": "seats_filled"}, inplace=True)
grouped["occupancy"] = grouped["seats_filled"] / TOTAL_SEATS   # 0 to 1

# 3. Feature engineering — turn date/time into numbers the model can use
grouped["date"] = pd.to_datetime(grouped["date"])
grouped["day_of_week"] = grouped["date"].dt.dayofweek   # 0=Mon ... 6=Sun
grouped["month"] = grouped["date"].dt.month
grouped["hour"] = grouped["slot_start"].apply(lambda t: t.hour)
grouped["is_weekend"] = grouped["day_of_week"].isin([4, 5]).astype(int)

features = ["day_of_week", "month", "hour", "is_weekend"]
X = grouped[features]
y = grouped["occupancy"]

# 4. Split chronologically (train on older data, test on the most recent slice)
grouped = grouped.sort_values("date")
split_index = int(len(grouped) * 0.8)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

# 5. Try a few models and compare
candidates = {
    "LinearRegression": LinearRegression(),
    "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
    "GradientBoosting": GradientBoostingRegressor(random_state=42),
}

best_name, best_model, best_mae = None, None, float("inf")
for name, model in candidates.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds) ** 0.5
    r2 = r2_score(y_test, preds)
    print(f"{name}: MAE={mae:.3f}  RMSE={rmse:.3f}  R2={r2:.3f}")
    if mae < best_mae:
        best_name, best_model, best_mae = name, model, mae

print(f"\nBest model: {best_name} (MAE={best_mae:.3f})")

# 6. Save the winning model
os.makedirs("ml/models", exist_ok=True)
joblib.dump(best_model, "ml/models/demand_model.joblib")
joblib.dump(features, "ml/models/features.joblib")
print("Saved to ml/models/demand_model.joblib")