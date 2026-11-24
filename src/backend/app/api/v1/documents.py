import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Document, DocumentState, Case, User, Decision, DecisionActor
from app.core.deps import get_current_user, require_consultant
from app.core.config import STORAGE_PATH
from app.api.v1.schemas import DocumentOut, DocumentDetail, DecisionCreate, DecisionOut, ExtractedFieldOut, ValidationCheckOut
from app.pipeline.process import run_pipeline
from app.modules.notifications.notifier import notify_case_complete

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 Mo


@router.post("/upload/{case_id}", response_model=DocumentOut, status_code=201)
async def upload_document(
    case_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dossier introuvable")
    if user.role.value != "consultant" and case.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acces interdit")

    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Extension non autorisee : {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Fichier trop volumineux (max 20 Mo)")

    file_hash = hashlib.sha256(content).hexdigest()
    stored_name = f"{uuid.uuid4().hex}{ext}"
    case_dir = STORAGE_PATH / str(case_id)
    case_dir.mkdir(parents=True, exist_ok=True)
    stored_path = case_dir / stored_name
    stored_path.write_bytes(content)

    doc = Document(
        case_id=case_id,
        original_filename=file.filename or "document",
        stored_path=str(stored_path),
        file_hash=file_hash,
        file_size=len(content),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(run_pipeline, doc.id)

    return doc


@router.get("/case/{case_id}", response_model=list[DocumentOut])
def list_documents(case_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dossier introuvable")
    if user.role.value != "consultant" and case.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acces interdit")
    return db.query(Document).filter(Document.case_id == case_id).all()


@router.get("/{doc_id}", response_model=DocumentDetail)
def get_document(doc_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document introuvable")
    case = db.get(Case, doc.case_id)
    if user.role.value != "consultant" and case.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acces interdit")

    result = DocumentDetail.model_validate(doc)
    if doc.ocr_result:
        result.ocr_text = doc.ocr_result.text
        result.ocr_confidence = doc.ocr_result.confidence
    result.extracted_fields = [ExtractedFieldOut.model_validate(f) for f in doc.extracted_fields]
    result.validation_checks = [ValidationCheckOut.model_validate(c) for c in doc.validation_checks]
    return result


@router.post("/{doc_id}/decide", response_model=DecisionOut)
def decide(
    doc_id: int,
    body: DecisionCreate,
    user: User = Depends(require_consultant),
    db: Session = Depends(get_db),
):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document introuvable")
    if doc.state.value not in ("PROPOSE_CONFORME", "PROPOSE_REJET", "A_REVOIR"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Le document n'est pas en attente de decision")

    decision = Decision(
        document_id=doc_id,
        actor=DecisionActor.CONSULTANT,
        decision=body.decision,
        comment=body.comment,
    )
    db.add(decision)

    if body.decision in ("confirme", "CONFIRME"):
        doc.state = DocumentState.CONFIRME
    elif body.decision in ("rejete", "REJETE"):
        doc.state = DocumentState.REJETE
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Decision invalide (confirme ou rejete)")

    db.commit()
    db.refresh(decision)

    case = db.get(Case, doc.case_id)
    if case:
        notify_case_complete(db, case)

    return decision
