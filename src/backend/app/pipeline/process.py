"""Pipeline de traitement : OCR → Classification → Decision IA.

Execute en tache de fond apres l'upload d'un document.
"""

from app.db.base import SessionLocal
from app.db.models import (
    Document, DocumentState, OcrResult, Prediction, Decision, DecisionActor,
    ExtractedField, ValidationCheck,
)
from app.modules.ocr.engine import extract_text
from app.modules.classification.classifier import classify
from app.modules.extraction.extractor import extract_fields
from app.modules.validation.validator import validate_document
from app.modules.notifications.notifier import notify_document_ready
from app.core.config import settings


def run_pipeline(document_id: int) -> None:
    db = SessionLocal()
    try:
        doc = db.get(Document, document_id)
        if not doc:
            return

        # --- Etape 1 : OCR ---
        doc.state = DocumentState.EN_LECTURE
        db.commit()

        text, confidence, engine = extract_text(doc.stored_path)
        ocr = OcrResult(
            document_id=doc.id,
            text=text,
            confidence=confidence,
            engine=engine,
        )
        db.add(ocr)
        db.commit()

        if not text.strip():
            doc.state = DocumentState.A_REVOIR
            decision = Decision(
                document_id=doc.id,
                actor=DecisionActor.IA,
                decision="A_REVOIR",
                comment="Texte OCR vide ou illisible",
            )
            db.add(decision)
            db.commit()
            return

        # --- Etape 2 : Classification ---
        doc.state = DocumentState.EN_ANALYSE
        db.commit()

        result = classify(text)
        pred = Prediction(
            document_id=doc.id,
            predicted_class=result["predicted_class"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
            top_features=result["top_features"],
            model_version=result["model_version"],
        )
        db.add(pred)
        db.commit()

        # --- Etape 3 : Extraction de champs ---
        fields = extract_fields(text, result["predicted_class"])
        for f in fields:
            db.add(ExtractedField(
                document_id=doc.id,
                field_name=f.field_name,
                field_value=f.field_value,
                source=f.source,
            ))
        db.commit()

        # --- Etape 4 : Validation metier ---
        fields_dict = {f.field_name: f.field_value for f in fields}
        checks = validate_document(text, result["predicted_class"], fields_dict)
        for c in checks:
            db.add(ValidationCheck(
                document_id=doc.id,
                rule_name=c.rule_name,
                passed=c.passed,
                message=c.message,
            ))
        db.commit()

        # --- Etape 5 : Decision IA ---
        min_conf = settings.CLASSIFICATION_MIN_CONFIDENCE

        if result["confidence"] >= min_conf:
            if result["predicted_class"] == "autre":
                doc.state = DocumentState.PROPOSE_REJET
                ia_decision = "PROPOSE_REJET"
                comment = f"Classe '{result['predicted_class']}' (confiance {result['confidence']:.0%})"
            else:
                doc.state = DocumentState.PROPOSE_CONFORME
                ia_decision = "PROPOSE_CONFORME"
                comment = f"Classe '{result['predicted_class']}' (confiance {result['confidence']:.0%})"
        else:
            doc.state = DocumentState.A_REVOIR
            ia_decision = "A_REVOIR"
            comment = f"Confiance insuffisante ({result['confidence']:.0%} < {min_conf:.0%})"

        decision = Decision(
            document_id=doc.id,
            actor=DecisionActor.IA,
            decision=ia_decision,
            comment=comment,
        )
        db.add(decision)
        db.commit()

        # --- Etape 6 : Notification consultants ---
        notify_document_ready(db, doc)

    except Exception as e:
        db.rollback()
        try:
            doc = db.get(Document, document_id)
            if doc:
                doc.state = DocumentState.A_REVOIR
                decision = Decision(
                    document_id=doc.id,
                    actor=DecisionActor.IA,
                    decision="A_REVOIR",
                    comment=f"Erreur pipeline : {str(e)[:200]}",
                )
                db.add(decision)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
