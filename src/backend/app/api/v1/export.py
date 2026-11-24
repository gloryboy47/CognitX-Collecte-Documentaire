"""Export des decisions d'un dossier en CSV."""

import csv
import io

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Case, Document, User
from app.core.deps import get_current_user

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/cases/{case_id}/csv")
def export_case_csv(case_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dossier introuvable")
    if user.role.value != "consultant" and case.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acces interdit")

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Document", "Taille (Ko)", "Classe predite", "Confiance IA",
        "Decision finale", "Decide par", "Commentaire", "Date decision",
    ])

    for doc in case.documents:
        last_pred = doc.predictions[-1] if doc.predictions else None
        last_decision = doc.decisions[-1] if doc.decisions else None

        writer.writerow([
            doc.original_filename,
            f"{doc.file_size / 1024:.0f}" if doc.file_size else "",
            last_pred.predicted_class if last_pred else "",
            f"{last_pred.confidence:.0%}" if last_pred else "",
            last_decision.decision if last_decision else doc.state.value,
            last_decision.actor.value if last_decision else "",
            last_decision.comment if last_decision else "",
            last_decision.created_at.strftime("%Y-%m-%d %H:%M") if last_decision else "",
        ])

    output.seek(0)
    filename = f"export_{case.name.replace(' ', '_')}_{case_id}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
