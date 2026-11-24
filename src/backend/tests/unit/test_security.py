"""Tests unitaires pour le module security."""

from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_hash_and_verify():
    hashed = hash_password("mon_mot_de_passe")
    assert hashed != "mon_mot_de_passe"
    assert verify_password("mon_mot_de_passe", hashed)
    assert not verify_password("mauvais", hashed)


def test_create_and_decode_token():
    token = create_access_token(user_id=42, role="client")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "client"
    assert "exp" in payload


def test_different_roles():
    token_client = create_access_token(1, "client")
    token_consultant = create_access_token(2, "consultant")
    assert decode_token(token_client)["role"] == "client"
    assert decode_token(token_consultant)["role"] == "consultant"
