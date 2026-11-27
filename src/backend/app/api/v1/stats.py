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
    # Un client ne voit que ses propres dossiers ; un consultant voit tout.
    docs = db.query(Document)
    cases = db.query(Case)
    preds_query = db.query(Prediction)
    if user.role.value != "consultant":
        docs = docs.join(Case, Document.case_id == Case.id).filter(Case.owner_id == user.id)
        cases = cases.filter(Case.owner_id == user.id)
        preds_query = (
            preds_query.join(Document, Prediction.document_id == Document.id)
            .join(Case, Document.case_id == Case.id)
            .filter(Case.owner_id == user.id)
        )

    total_docs = docs.count()
    total_cases = cases.count()

    state_counts = {}
    for state in DocumentState:
        count = docs.filter(Document.state == state).count()
        if count > 0:
            state_counts[state.value] = count

    preds = preds_query.all()
    class_counts = {}
    confidences = []
    for p in preds:
        class_counts[p.predicted_class] = class_counts.get(p.predicted_class, 0) + 1
        confidences.append(p.confidence)

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    high_confidence = sum(1 for c in confidences if c >= 0.80)
    low_confidence = sum(1 for c in confidences if c < 0.80)

    confirmed = docs.filter(Document.state == DocumentState.CONFIRME).count()
    rejected = docs.filter(Document.state == DocumentState.REJETE).count()
    pending = docs.filter(
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
