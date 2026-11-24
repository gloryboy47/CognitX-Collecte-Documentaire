import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Enum, ForeignKey, Boolean,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


# --- Enums ---

class Role(str, enum.Enum):
    CLIENT = "client"
    CONSULTANT = "consultant"


class DocumentState(str, enum.Enum):
    DEPOSE = "DEPOSE"
    EN_LECTURE = "EN_LECTURE"
    EN_ANALYSE = "EN_ANALYSE"
    PROPOSE_CONFORME = "PROPOSE_CONFORME"
    PROPOSE_REJET = "PROPOSE_REJET"
    A_REVOIR = "A_REVOIR"
    CONFIRME = "CONFIRME"
    REJETE = "REJETE"


class CaseState(str, enum.Enum):
    INCOMPLET = "INCOMPLET"
    EN_COURS = "EN_COURS"
    A_VALIDER = "A_VALIDER"
    VALIDE = "VALIDE"


class DecisionActor(str, enum.Enum):
    IA = "ia"
    CONSULTANT = "consultant"


# --- Models ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.CLIENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)

    cases = relationship("Case", back_populates="owner")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    state = Column(Enum(CaseState), nullable=False, default=CaseState.INCOMPLET)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    owner = relationship("User", back_populates="cases")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    requirements = relationship("CaseRequirement", back_populates="case", cascade="all, delete-orphan")


class DocumentType(Base):
    __tablename__ = "document_types"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(255), nullable=False)
    description = Column(Text, default="")


class CaseRequirement(Base):
    __tablename__ = "case_requirements"

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), nullable=False)
    is_satisfied = Column(Boolean, default=False)

    case = relationship("Case", back_populates="requirements")
    document_type = relationship("DocumentType")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_path = Column(String(500), nullable=False)
    file_hash = Column(String(64))
    file_size = Column(Integer)
    state = Column(Enum(DocumentState), nullable=False, default=DocumentState.DEPOSE)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    case = relationship("Case", back_populates="documents")
    ocr_result = relationship("OcrResult", back_populates="document", uselist=False, cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="document", cascade="all, delete-orphan")
    extracted_fields = relationship("ExtractedField", back_populates="document", cascade="all, delete-orphan")
    validation_checks = relationship("ValidationCheck", back_populates="document", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="document", cascade="all, delete-orphan")


class OcrResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), unique=True, nullable=False)
    text = Column(Text, nullable=False)
    confidence = Column(Float)
    engine = Column(String(50), default="pymupdf")
    created_at = Column(DateTime, default=_utcnow)

    document = relationship("Document", back_populates="ocr_result")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    predicted_class = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    probabilities = Column(Text)
    top_features = Column(Text)
    model_version = Column(String(100))
    created_at = Column(DateTime, default=_utcnow)

    document = relationship("Document", back_populates="predictions")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text)
    source = Column(String(50), default="regex")

    document = relationship("Document", back_populates="extracted_fields")


class ValidationCheck(Base):
    __tablename__ = "validation_checks"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    rule_name = Column(String(100), nullable=False)
    passed = Column(Boolean, nullable=False)
    message = Column(Text)

    document = relationship("Document", back_populates="validation_checks")


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    actor = Column(Enum(DecisionActor), nullable=False)
    decision = Column(String(50), nullable=False)
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=_utcnow)

    document = relationship("Document", back_populates="decisions")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User")
