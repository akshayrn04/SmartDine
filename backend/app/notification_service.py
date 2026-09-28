from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app import models


def deliver(user: models.User, text: str) -> bool:
    """Console sender for now. Later, the Twilio call goes here (only this function changes)."""
    print(f"[NOTIFY -> {user.name} | {user.phone or 'no phone'}] {text}")
    return True


def send_notification(db: Session, notification: models.Notification):
    """Send one saved notification and record the result."""
    user = db.get(models.User, notification.user_id)
    ok = deliver(user, notification.message_text)
    notification.status = "SENT" if ok else "FAILED"
    if ok:
        notification.sent_at = datetime.now(timezone.utc)


def notify_booking_update(db: Session, user: models.User, text: str):
    """Instant notice about a booking. Only for customers who opted in. No approval needed."""
    if not user.opted_in:
        return None
    notification = models.Notification(
        campaign_id=None, user_id=user.id, message_text=text,
        status="PENDING", type="BOOKING_UPDATE",
    )
    db.add(notification)
    db.flush()
    send_notification(db, notification)
    return notification