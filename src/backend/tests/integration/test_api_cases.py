"""Tests d'integration pour l'API cases."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def api(override_db):
    return TestClient(app)


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_case(api, client_token):
    resp = api.post(
        "/api/v1/cases",
        json={"name": "Dossier CIR 2024", "description": "Test"},
        headers=_auth(client_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Dossier CIR 2024"
    assert data["state"] == "INCOMPLET"


def test_list_cases_client_sees_own(api, client_token, consultant_token):
    api.post("/api/v1/cases", json={"name": "Mon dossier"}, headers=_auth(client_token))
    api.post("/api/v1/cases", json={"name": "Autre dossier"}, headers=_auth(consultant_token))

    resp = api.get("/api/v1/cases", headers=_auth(client_token))
    cases = resp.json()
    assert len(cases) == 1
    assert cases[0]["name"] == "Mon dossier"


def test_list_cases_consultant_sees_all(api, client_token, consultant_token):
    api.post("/api/v1/cases", json={"name": "Dossier A"}, headers=_auth(client_token))
    api.post("/api/v1/cases", json={"name": "Dossier B"}, headers=_auth(consultant_token))

    resp = api.get("/api/v1/cases", headers=_auth(consultant_token))
    cases = resp.json()
    assert len(cases) == 2


def test_get_case_detail(api, client_token):
    resp = api.post("/api/v1/cases", json={"name": "Detail"}, headers=_auth(client_token))
    case_id = resp.json()["id"]

    resp = api.get(f"/api/v1/cases/{case_id}", headers=_auth(client_token))
    assert resp.status_code == 200
    assert resp.json()["name"] == "Detail"
    assert "documents" in resp.json()


def test_get_case_forbidden_other_client(api, client_token, override_db):
    from app.db.models import User, Role
    from app.core.security import hash_password, create_access_token

    other = User(
        email="other@test.com",
        hashed_password=hash_password("test"),
        full_name="Other",
        role=Role.CLIENT,
    )
    override_db.add(other)
    override_db.commit()
    override_db.refresh(other)
    other_token = create_access_token(other.id, "client")

    resp = api.post("/api/v1/cases", json={"name": "Prive"}, headers=_auth(client_token))
    case_id = resp.json()["id"]

    resp = api.get(f"/api/v1/cases/{case_id}", headers=_auth(other_token))
    assert resp.status_code == 403


def test_no_auth_returns_403(api):
    resp = api.get("/api/v1/cases")
    assert resp.status_code == 403
