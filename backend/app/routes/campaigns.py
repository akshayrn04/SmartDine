from datetime import date as date_cls, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth_dependency import require_restaurant
from app.routes.bookings import get_available_seats
from app.ai.predictor import predict_occupancy
from app.ai.decision_engine import decide_action, choose_incentive, MEDIUM_THRESHOLD
from app.ai.targeting import find_suitable_customers
from app.ai.messaging import generate_message_template
from app.notification_service import send_notification

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.post("", response_model=schemas.CampaignOut)
def create_campaign(
    payload: schemas.CampaignCreate,
    db: Session = Depends(get_db),
    user=Depends(require_restaurant),
):
    # 1. Only today's slots that haven't started yet
    today = date_cls.today()
    now = datetime.now().time()

    if payload.target_date != today:
        raise HTTPException(status_code=400, detail="Campaigns can only be created for today's slots")
    if payload.slot_start <= now:
        raise HTTPException(status_code=400, detail="That slot has already started")

    # 2. Combine the model's prediction with the real current occupancy
    predicted = predict_occupancy(payload.target_date, payload.slot_start.hour)
    seats = get_available_seats(db, payload.target_date, payload.slot_start)
    current = (seats["booked_seats"] + seats["blocked_seats"]) / seats["total_seats"]

    occ = max(predicted, current)   # if it's already filling up, don't discount it
    action = decide_action(occ)

    if action == "NO_ACTION":
        raise HTTPException(status_code=400, detail=f"No campaign needed. Occupancy is {occ:.2f}")

    # 3. Pick an incentive and save the campaign (waiting for approval)
    offer_type, offer_value = choose_incentive(occ)

    campaign = models.Campaign(
        target_date=payload.target_date,
        slot_start=payload.slot_start,
        predicted_occupancy=f"{occ:.3f}",
        offer_type=offer_type,
        offer_value=offer_value,
        status="PENDING_APPROVAL",
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    # 4. Find suitable customers, write ONE message, and fill in each name
    customers = find_suitable_customers(db, payload.target_date, payload.slot_start)
    restaurant_name = "SmartDine"

    template = generate_message_template(
        restaurant_name, payload.target_date, payload.slot_start, offer_type, offer_value
    )
    campaign.message_template = template

    for customer in customers:
        notification = models.Notification(
            campaign_id=campaign.id,
            user_id=customer.id,
            message_text=template.replace("{name}", customer.name),
            status="PENDING",
        )
        db.add(notification)

    db.commit()
    return campaign


@router.get("", response_model=list[schemas.CampaignOut])
def list_campaigns(db: Session = Depends(get_db), _=Depends(require_restaurant)):
    return db.query(models.Campaign).order_by(models.Campaign.created_at.desc()).all()


@router.get("/{campaign_id}/notifications", response_model=list[schemas.NotificationOut])
def campaign_notifications(campaign_id: int, db: Session = Depends(get_db), _=Depends(require_restaurant)):
    return db.query(models.Notification).filter(models.Notification.campaign_id == campaign_id).all()


@router.post("/{campaign_id}/approve", response_model=schemas.CampaignOut)
def approve_campaign(campaign_id: int, db: Session = Depends(get_db), user=Depends(require_restaurant)):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != "PENDING_APPROVAL":
        raise HTTPException(status_code=400, detail=f"Campaign is already {campaign.status}")

    # Fresh check: has the slot filled up since this campaign was created?
    seats = get_available_seats(db, campaign.target_date, campaign.slot_start)
    current = (seats["booked_seats"] + seats["blocked_seats"]) / seats["total_seats"]
    if current > MEDIUM_THRESHOLD:
        campaign.status = "EXPIRED"
        db.commit()
        raise HTTPException(status_code=400, detail="Slot has filled up since this campaign was created, so it was expired")

    campaign.status = "APPROVED"
    campaign.approved_by = user.id

    pending = (
        db.query(models.Notification)
        .filter(models.Notification.campaign_id == campaign.id, models.Notification.status == "PENDING")
        .all()
    )
    for n in pending:
        send_notification(db, n)

    campaign.status = "SENT"
    db.commit()
    db.refresh(campaign)
    return campaign

@router.post("/{campaign_id}/reject", response_model=schemas.CampaignOut)
def reject_campaign(campaign_id: int, db: Session = Depends(get_db), _=Depends(require_restaurant)):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.status = "REJECTED"
    db.commit()
    db.refresh(campaign)
    return campaign