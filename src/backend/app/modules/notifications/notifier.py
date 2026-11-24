"""Module de notifications pour les consultants.

Cree des notifications en base quand un document necessite une action humaine.
Les consultants voient leurs notifications via l'API.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Notification, User, Role, Document, Case


def notify_document_ready(db: Session, document: Document) -> None:
    """Notifie tous les consultants qu'un document est pret pour revue."""
    consultants = db.query(User).filter(User.role == Role.CONSULTANT, User.is_active == True).all()

    state_labels = {
        "PROPOSE_CONFORME": "propose conforme par l'IA",
        "PROPOSE_REJET": "propose au rejet par l'IA",
        "A_REVOIR": "a revoir manuellement",
    }
    label = state_labels.get(document.state.value, document.state.value)

    case = db.get(Case, document.case_id)
    case_name = case.name if case else f"Dossier #{document.case_id}"

    for consultant in consultants:
        notif = Notification(
            user_id=consultant.id,
            type="document_ready",
            title=f"Document {label}",
            message=f"{document.original_filename} dans {case_name} est {label}.",
        )
        db.add(notif)

    db.commit()


def notify_case_complete(db: Session, case: Case) -> None:
    """Notifie le proprietaire du dossier que tous les documents sont traites."""
    all_decided = all(
        doc.state.value in ("CONFIRME", "REJETE")
        for doc in case.documents
    )
    if not all_decided or not case.documents:
        return

    notif = Notification(
        user_id=case.owner_id,
        type="case_complete",
        title="Dossier traite",
        message=f"Tous les documents de '{case.name}' ont ete examines par un consultant.",
    )
    db.add(notif)
    db.commit()
