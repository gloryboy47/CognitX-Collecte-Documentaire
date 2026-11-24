"""Configuration pytest — base de test SQLite in-memory."""

import os
import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["STORAGE_DIR"] = "/tmp/test-storage"
os.environ["JWT_SECRET"] = "test-secret-key-for-tests"

from app.db.base import Base, get_db
from app.db.models import User, Role, DocumentType
from app.core.security import hash_password, create_access_token
from app.main import app


engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestSession()
    _seed_types(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def _seed_types(db):
    if db.query(DocumentType).count() == 0:
        for code, label in [
            ("facture", "Facture"),
            ("fiche_de_paie", "Fiche de paie"),
            ("contrat", "Contrat"),
            ("compte_rendu_rd", "Compte rendu R&D"),
            ("autre", "Autre"),
        ]:
            db.add(DocumentType(code=code, label=label))
        db.commit()


@pytest.fixture
def db():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def override_db(db):
    def _get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db
    yield db
    app.dependency_overrides.clear()


@pytest.fixture
def client_user(db):
    user = User(
        email="client@test.com",
        hashed_password=hash_password("test1234"),
        full_name="Test Client",
        role=Role.CLIENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def consultant_user(db):
    user = User(
        email="consultant@test.com",
        hashed_password=hash_password("test1234"),
        full_name="Test Consultant",
        role=Role.CONSULTANT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def client_token(client_user):
    return create_access_token(client_user.id, client_user.role.value)


@pytest.fixture
def consultant_token(consultant_user):
    return create_access_token(consultant_user.id, consultant_user.role.value)
