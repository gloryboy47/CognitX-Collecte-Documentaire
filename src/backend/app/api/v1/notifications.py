"""API notifications : lecture et marquage comme lues."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Notification, User
from app.core.deps import get_current_user
from app.api.v1.schemas import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )


@router.get("/unread/count")
def unread_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.is_read == False)
        .count()
    )
    return {"count": count}


@router.post("/{notif_id}/read")
def mark_read(notif_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.get(Notification, notif_id)
    if notif and notif.user_id == user.id:
        notif.is_read = True
        db.commit()
    return {"ok": True}


@router.post("/read-all")
def mark_all_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(
        Notification.user_id == user.id, Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"ok": True}
