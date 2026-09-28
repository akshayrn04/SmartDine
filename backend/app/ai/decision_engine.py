HIGH_THRESHOLD = 0.70   # above this: no action needed
MEDIUM_THRESHOLD = 0.40  # above this but below HIGH: notify, no incentive

def decide_action(predicted_occupancy: float) -> str:
    if predicted_occupancy > HIGH_THRESHOLD:
        return "NO_ACTION"
    elif predicted_occupancy > MEDIUM_THRESHOLD:
        return "NOTIFICATION"
    else:
        return "INCENTIVE_CANDIDATE"


def choose_incentive(predicted_occupancy: float) -> tuple[str, str | None]:
    """Returns (offer_type, offer_value)."""
    if predicted_occupancy < 0.20:
        return "DISCOUNT_PERCENT", "15"
    elif predicted_occupancy < MEDIUM_THRESHOLD:
        return "FREEBIE", "Complimentary dessert"
    else:
        return "NONE", None