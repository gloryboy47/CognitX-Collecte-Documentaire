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

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

STORAGE_PATH = Path(settings.STORAGE_DIR)
STORAGE_PATH.mkdir(parents=True, exist_ok=True)
