from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Case, User
from app.core.deps import get_current_user
from app.api.v1.schemas import CaseCreate, CaseOut, CaseDetail, RequirementOut
from app.modules.cases.service import ensure_requirements, build_checklist

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseOut, status_code=201)
def create_case(body: CaseCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    case = Case(name=body.name, description=body.description, owner_id=user.id)
    db.add(case)
    db.commit()
    db.refresh(case)
    ensure_requirements(db, case)
    return case


@router.get("", response_model=list[CaseOut])
def list_cases(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role.value == "consultant":
        return db.query(Case).all()
    return db.query(Case).filter(Case.owner_id == user.id).all()


@router.get("/{case_id}", response_model=CaseDetail)
def get_case(case_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dossier introuvable")
    if user.role.value != "consultant" and case.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acces interdit")
    checklist = build_checklist(db, case)
    result = CaseDetail.model_validate(case)
    result.checklist = [RequirementOut(**item) for item in checklist]
    return result
