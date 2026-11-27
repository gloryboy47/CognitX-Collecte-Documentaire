from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


# --- Auth ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Literal["client", "consultant"] = "client"
    invite_code: str = ""


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Cases ---

class CaseCreate(BaseModel):
    name: str
    description: str = ""


class CaseOut(BaseModel):
    id: int
    name: str
    description: str
    state: str
    owner_id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class RequirementOut(BaseModel):
    code: str
    label: str
    status: Literal["FOURNI", "A_VALIDER", "A_REVOIR", "REJETE", "MANQUANT"]


class CaseDetail(CaseOut):
    documents: list["DocumentOut"] = []
    # Nomme "checklist" : "requirements" est deja la relation ORM du modele Case
    checklist: list[RequirementOut] = []


# --- Documents ---

class DocumentOut(BaseModel):
    id: int
    case_id: int
    original_filename: str
    file_size: int | None
    state: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ExtractedFieldOut(BaseModel):
    id: int
    field_name: str
    field_value: str | None
    source: str
    model_config = {"from_attributes": True}


class ValidationCheckOut(BaseModel):
    id: int
    rule_name: str
    passed: bool
    message: str | None
    model_config = {"from_attributes": True}


class DocumentDetail(DocumentOut):
    ocr_text: str | None = None
    ocr_confidence: float | None = None
    predictions: list["PredictionOut"] = []
    decisions: list["DecisionOut"] = []
    extracted_fields: list["ExtractedFieldOut"] = []
    validation_checks: list["ValidationCheckOut"] = []


class PredictionOut(BaseModel):
    id: int
    predicted_class: str
    confidence: float
    probabilities: str | None
    top_features: str | None
    model_version: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class DecisionCreate(BaseModel):
    decision: str
    comment: str = ""


class DecisionOut(BaseModel):
    id: int
    actor: str
    decision: str
    comment: str
    created_at: datetime
    model_config = {"from_attributes": True}


# --- Notifications ---

class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    model_config = {"from_attributes": True}
