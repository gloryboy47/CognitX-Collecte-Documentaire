"""Pieces attendues, statut du dossier, securite d'inscription, doublons et statistiques."""

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import documents as documents_api
from app.core.config import settings
from app.db.models import Case, Document, DocumentState, Notification, Prediction
from app.main import app
from app.modules.cases.service import refresh_case_state


@pytest.fixture
def api(override_db):
    return TestClient(app)


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _new_case(api, token, name="Dossier test"):
    resp = api.post("/api/v1/cases", json={"name": name}, headers=_auth(token))
    assert resp.status_code == 201
    return resp.json()["id"]


def _add_document(db, case_id, predicted_class, state):
    doc = Document(case_id=case_id, original_filename=f"{predicted_class}.pdf",
                   stored_path="x", state=state)
    db.add(doc)
    db.commit()
    db.add(Prediction(document_id=doc.id, predicted_class=predicted_class, confidence=0.9))
    db.commit()
    return doc


def test_new_case_lists_all_missing_pieces(api, client_token):
    case_id = _new_case(api, client_token)
    data = api.get(f"/api/v1/cases/{case_id}", headers=_auth(client_token)).json()
    assert data["state"] == "INCOMPLET"
    assert [c["status"] for c in data["checklist"]] == ["MANQUANT"] * 4


@pytest.mark.parametrize("doc_state,expected", [
    (DocumentState.EN_ANALYSE, "EN_COURS"),
    (DocumentState.PROPOSE_CONFORME, "A_VALIDER"),
    (DocumentState.CONFIRME, "VALIDE"),
    (DocumentState.REJETE, "INCOMPLET"),
])
def test_case_state_follows_documents(api, db, client_token, doc_state, expected):
    case_id = _new_case(api, client_token)
    for cls in ["facture", "fiche_de_paie", "contrat", "compte_rendu_rd"]:
        _add_document(db, case_id, cls, doc_state)
    assert refresh_case_state(db, db.get(Case, case_id)).value == expected


def test_one_missing_piece_keeps_case_incomplete(api, db, client_token):
    case_id = _new_case(api, client_token)
    _add_document(db, case_id, "facture", DocumentState.CONFIRME)
    assert refresh_case_state(db, db.get(Case, case_id)).value == "INCOMPLET"


def test_rejection_notifies_client_with_reason(api, db, client_user, client_token,
                                               consultant_token):
    case_id = _new_case(api, client_token)
    doc = _add_document(db, case_id, "facture", DocumentState.A_REVOIR)
    resp = api.post(f"/api/v1/documents/{doc.id}/decide",
                    json={"decision": "rejete", "comment": "Illisible"},
                    headers=_auth(consultant_token))
    assert resp.status_code == 200
    notif = db.query(Notification).filter(Notification.user_id == client_user.id).one()
    assert notif.type == "document_rejected" and "Illisible" in notif.message


def test_invalid_decision_changes_nothing(api, db, client_token, consultant_token):
    case_id = _new_case(api, client_token)
    doc = _add_document(db, case_id, "facture", DocumentState.A_REVOIR)
    resp = api.post(f"/api/v1/documents/{doc.id}/decide", json={"decision": "peut-etre"},
                    headers=_auth(consultant_token))
    assert resp.status_code == 400
    assert db.get(Document, doc.id).state == DocumentState.A_REVOIR


def test_duplicate_upload_is_refused(api, client_token, monkeypatch, tmp_path):
    monkeypatch.setattr(documents_api, "run_pipeline", lambda doc_id: None)
    monkeypatch.setattr(documents_api, "STORAGE_PATH", tmp_path)
    case_id = _new_case(api, client_token)
    files = {"file": ("a.pdf", b"%PDF-1.4 test", "application/pdf")}
    url = f"/api/v1/documents/upload/{case_id}"
    assert api.post(url, files=files, headers=_auth(client_token)).status_code == 201
    assert api.post(url, files=files, headers=_auth(client_token)).status_code == 409


def test_consultant_signup_requires_invite_code(api, monkeypatch):
    payload = {"email": "c@test.com", "password": "secret123", "full_name": "C",
               "role": "consultant"}
    monkeypatch.setattr(settings, "CONSULTANT_INVITE_CODE", "")
    assert api.post("/api/v1/auth/register", json=payload).status_code == 403
    monkeypatch.setattr(settings, "CONSULTANT_INVITE_CODE", "bon-code")
    assert api.post("/api/v1/auth/register",
                    json={**payload, "invite_code": "faux"}).status_code == 403
    assert api.post("/api/v1/auth/register",
                    json={**payload, "invite_code": "bon-code"}).status_code == 201


def test_client_stats_only_cover_own_cases(api, db, client_token, consultant_token):
    other_case = _new_case(api, consultant_token, "Autre dossier")
    _add_document(db, other_case, "facture", DocumentState.CONFIRME)
    own = api.get("/api/v1/stats", headers=_auth(client_token)).json()
    assert own["total_documents"] == 0 and own["total_cases"] == 0
    everything = api.get("/api/v1/stats", headers=_auth(consultant_token)).json()
    assert everything["total_documents"] == 1
