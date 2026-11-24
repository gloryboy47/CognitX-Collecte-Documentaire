"""Tests d'integration pour l'API auth."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def api(override_db):
    return TestClient(app)


def test_register_new_user(api):
    resp = api.post("/api/v1/auth/register", json={
        "email": "nouveau@test.com",
        "password": "securepass",
        "full_name": "Nouveau User",
        "role": "client",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "nouveau@test.com"
    assert data["user"]["role"] == "client"


def test_register_duplicate_email(api):
    payload = {
        "email": "dup@test.com",
        "password": "securepass",
        "full_name": "User 1",
        "role": "client",
    }
    api.post("/api/v1/auth/register", json=payload)
    resp = api.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


def test_login_success(api):
    api.post("/api/v1/auth/register", json={
        "email": "login@test.com",
        "password": "mypassword",
        "full_name": "Login User",
        "role": "consultant",
    })
    resp = api.post("/api/v1/auth/login", json={
        "email": "login@test.com",
        "password": "mypassword",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["role"] == "consultant"


def test_login_wrong_password(api):
    api.post("/api/v1/auth/register", json={
        "email": "wrong@test.com",
        "password": "correctpass",
        "full_name": "User",
    })
    resp = api.post("/api/v1/auth/login", json={
        "email": "wrong@test.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_login_nonexistent_user(api):
    resp = api.post("/api/v1/auth/login", json={
        "email": "ghost@test.com",
        "password": "whatever",
    })
    assert resp.status_code == 401
