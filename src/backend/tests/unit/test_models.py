"""Tests unitaires pour les modeles SQLAlchemy."""

from app.db.models import (
    DocumentState,
    CaseState,
    DecisionActor,
    Role,
)


def test_document_states():
    assert DocumentState.DEPOSE.value == "DEPOSE"
    assert DocumentState.CONFIRME.value == "CONFIRME"
    assert DocumentState.REJETE.value == "REJETE"
    all_states = [s.value for s in DocumentState]
    assert len(all_states) == 8


def test_case_states():
    assert CaseState.INCOMPLET.value == "INCOMPLET"
    assert CaseState.VALIDE.value == "VALIDE"
    all_states = [s.value for s in CaseState]
    assert len(all_states) == 4


def test_roles():
    assert Role.CLIENT.value == "client"
    assert Role.CONSULTANT.value == "consultant"


def test_decision_actors():
    assert DecisionActor.IA.value == "ia"
    assert DecisionActor.CONSULTANT.value == "consultant"
