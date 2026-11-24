from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base, engine
from app.db.models import DocumentType
from app.db.base import SessionLocal
from app.api.v1 import auth, cases, documents, notifications, export, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_document_types()
    yield


app = FastAPI(
    title="CognitX — Collecte Documentaire Intelligente",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}


def _seed_document_types():
    db = SessionLocal()
    try:
        if db.query(DocumentType).count() == 0:
            types = [
                DocumentType(code="facture", label="Facture", description="Facture de prestation ou de vente"),
                DocumentType(code="fiche_de_paie", label="Fiche de paie", description="Bulletin de salaire"),
                DocumentType(code="contrat", label="Contrat", description="Contrat de prestation, travail ou partenariat"),
                DocumentType(code="compte_rendu_rd", label="Compte rendu R&D", description="Compte rendu de reunion de recherche et developpement"),
                DocumentType(code="autre", label="Autre", description="Document non pertinent pour le dossier CIR/CII"),
            ]
            db.add_all(types)
            db.commit()
    finally:
        db.close()
