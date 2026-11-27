from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./.storage/collecte.db"
    STORAGE_DIR: str = "./.storage/files"

    JWT_SECRET: str = "change-me-with-a-long-random-string"
    JWT_ACCESS_TTL_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"

    TESSERACT_CMD: str = "tesseract"
    OCR_LANGS: str = "fra+eng"

    ML_MODEL_PATH: str = "src/ml/artifacts/current"
    CLASSIFICATION_MIN_CONFIDENCE: float = 0.80

    REMINDER_INTERVAL_HOURS: int = 24

    # Inscription consultant : desactivee tant que ce code est vide
    CONSULTANT_INVITE_CODE: str = ""
    # Pieces attendues par dossier. Liste HYPOTHETIQUE, a valider avec l'encadrant / Leyton.
    REQUIRED_DOCUMENT_TYPES: str = "facture,fiche_de_paie,contrat,compte_rendu_rd"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

STORAGE_PATH = Path(settings.STORAGE_DIR)
STORAGE_PATH.mkdir(parents=True, exist_ok=True)
