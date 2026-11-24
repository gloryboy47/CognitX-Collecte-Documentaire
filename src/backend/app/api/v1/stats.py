"""API statistiques pour le dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.base import get_db
from app.db.models import Document, DocumentState, Prediction, Case, User
from app.core.deps import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
def get_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_docs = db.query(Document).count()
    total_cases = db.query(Case).count()

    state_counts = {}
    for state in DocumentState:
        count = db.query(Document).filter(Document.state == state).count()
        if count > 0:
            state_counts[state.value] = count

    preds = db.query(Prediction).all()
    class_counts = {}
    confidences = []
    for p in preds:
        class_counts[p.predicted_class] = class_counts.get(p.predicted_class, 0) + 1
        confidences.append(p.confidence)

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    high_confidence = sum(1 for c in confidences if c >= 0.80)
    low_confidence = sum(1 for c in confidences if c < 0.80)

    confirmed = db.query(Document).filter(Document.state == DocumentState.CONFIRME).count()
    rejected = db.query(Document).filter(Document.state == DocumentState.REJETE).count()
    pending = db.query(Document).filter(
        Document.state.in_([
            DocumentState.PROPOSE_CONFORME,
            DocumentState.PROPOSE_REJET,
            DocumentState.A_REVOIR,
        ])
    ).count()

    return {
        "total_documents": total_docs,
        "total_cases": total_cases,
        "documents_par_statut": state_counts,
        "predictions_par_classe": class_counts,
        "confiance_moyenne": round(avg_confidence, 4),
        "haute_confiance": high_confidence,
        "basse_confiance": low_confidence,
        "confirmes": confirmed,
        "rejetes": rejected,
        "en_attente": pending,
    }
