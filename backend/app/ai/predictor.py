import os
import joblib
import pandas as pd
from datetime import date

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models", "demand_model.joblib")
FEATURES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models", "features.joblib")

_model = None
_features = None

def _load():
    global _model, _features
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _features = joblib.load(FEATURES_PATH)
    return _model, _features

def predict_occupancy(target_date: date, hour: int) -> float:
    model, features = _load()
    row = {
        "day_of_week": target_date.weekday(),
        "month": target_date.month,
        "hour": hour,
        "is_weekend": 1 if target_date.weekday() in (4, 5) else 0,
    }
    X = pd.DataFrame([row])[features]
    prediction = model.predict(X)[0]
    return max(0.0, min(1.0, float(prediction)))   # keep it between 0 and 1