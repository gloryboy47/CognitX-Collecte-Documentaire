"""Pieces attendues d'un dossier, pieces manquantes et calcul du statut du dossier."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import (
    Case, CaseRequirement, CaseState, Document, DocumentState, DocumentType, Prediction,
)

PROCESSING = {DocumentState.DEPOSE, DocumentState.EN_LECTURE, DocumentState.EN_ANALYSE}

# Statut d'une piece attendue : le meilleur document de ce type l'emporte (ordre = priorite)
PRIORITY = [
    (DocumentState.CONFIRME, "FOURNI"),
    (DocumentState.PROPOSE_CONFORME, "A_VALIDER"),
    (DocumentState.A_REVOIR, "A_REVOIR"),
    (DocumentState.REJETE, "REJETE"),
]


def ensure_requirements(db: Session, case: Case) -> list[CaseRequirement]:
    """Cree les pieces attendues du dossier si elles n'existent pas encore."""
    existing = db.query(CaseRequirement).filter(CaseRequirement.case_id == case.id).all()
    if existing:
        return existing
    codes = [c.strip() for c in settings.REQUIRED_DOCUMENT_TYPES.split(",") if c.strip()]
    types = {t.code: t for t in db.query(DocumentType).filter(DocumentType.code.in_(codes)).all()}
    created = [
        CaseRequirement(case_id=case.id, document_type_id=types[code].id)
        for code in codes if code in types
    ]
    db.add_all(created)
    db.commit()
    return created


def _states_by_class(db: Session, documents: list[Document]) -> dict[str, set[DocumentState]]:
    """Etats des documents, regroupes par classe de leur prediction la plus recente."""
    ids = [d.id for d in documents]
    latest: dict[int, str] = {}
    if ids:
        predictions = (
            db.query(Prediction)
            .filter(Prediction.document_id.in_(ids))
            .order_by(Prediction.id)
            .all()
        )
        for p in predictions:
            latest[p.document_id] = p.predicted_class
    grouped: dict[str, set[DocumentState]] = {}
    for d in documents:
        if d.id in latest:
            grouped.setdefault(latest[d.id], set()).add(d.state)
    return grouped


def build_checklist(db: Session, case: Case) -> list[dict[str, str]]:
    """Liste des pieces attendues avec leur statut."""
    requirements = ensure_requirements(db, case)
    documents = db.query(Document).filter(Document.case_id == case.id).all()
    grouped = _states_by_class(db, documents)
    types = {t.id: t for t in db.query(DocumentType).all()}

    checklist = []
    for req in sorted(requirements, key=lambda r: r.id):
        doc_type = types[req.document_type_id]
        states = grouped.get(doc_type.code, set())
        status = next((label for state, label in PRIORITY if state in states), "MANQUANT")
        checklist.append({"code": doc_type.code, "label": doc_type.label, "status": status})
    return checklist


def refresh_case_state(db: Session, case: Case) -> CaseState:
    """Recalcule et enregistre le statut du dossier.

    EN_COURS  : au moins un document en cours de traitement
    VALIDE    : toutes les pieces attendues confirmees par un consultant
    A_VALIDER : toutes les pieces presentes, certaines en attente du consultant
    INCOMPLET : au moins une piece manquante, rejetee ou a revoir
    """
    checklist = build_checklist(db, case)
    documents = db.query(Document).filter(Document.case_id == case.id).all()
    statuses = {item["status"] for item in checklist}

    if any(d.state in PROCESSING for d in documents):
        state = CaseState.EN_COURS
    elif checklist and statuses == {"FOURNI"}:
        state = CaseState.VALIDE
    elif checklist and statuses <= {"FOURNI", "A_VALIDER"}:
        state = CaseState.A_VALIDER
    else:
        state = CaseState.INCOMPLET

    for req, item in zip(
        sorted(ensure_requirements(db, case), key=lambda r: r.id), checklist
    ):
        req.is_satisfied = item["status"] == "FOURNI"
    case.state = state
    db.commit()
    return state
