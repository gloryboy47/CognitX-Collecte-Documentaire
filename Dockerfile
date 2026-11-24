FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-fra \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY src/ml/pyproject.toml src/ml/pyproject.toml
COPY src/ml/src/ src/ml/src/
RUN pip install --no-cache-dir ./src/ml

COPY src/backend/pyproject.toml src/backend/pyproject.toml
RUN pip install --no-cache-dir ./src/backend

COPY src/ml/artifacts/ src/ml/artifacts/
COPY src/backend/ src/backend/
COPY data/ data/

ENV ML_MODEL_PATH=src/ml/artifacts/current
ENV STORAGE_DIR=.storage/files
ENV DATABASE_URL=sqlite:///.storage/collecte.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--app-dir", "src/backend", "--host", "0.0.0.0", "--port", "8000"]
