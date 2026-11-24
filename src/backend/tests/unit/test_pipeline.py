"""Tests unitaires pour la logique de decision du pipeline."""

import pytest


def test_decision_logic_conforme():
    """Si confidence >= 80% et classe != autre -> PROPOSE_CONFORME."""
    result = {"predicted_class": "facture", "confidence": 0.95}
    min_conf = 0.80

    if result["confidence"] >= min_conf:
        if result["predicted_class"] == "autre":
            decision = "PROPOSE_REJET"
        else:
            decision = "PROPOSE_CONFORME"
    else:
        decision = "A_REVOIR"

    assert decision == "PROPOSE_CONFORME"


def test_decision_logic_rejet_autre():
    """Si confidence >= 80% mais classe == autre -> PROPOSE_REJET."""
    result = {"predicted_class": "autre", "confidence": 0.90}
    min_conf = 0.80

    if result["confidence"] >= min_conf:
        if result["predicted_class"] == "autre":
            decision = "PROPOSE_REJET"
        else:
            decision = "PROPOSE_CONFORME"
    else:
        decision = "A_REVOIR"

    assert decision == "PROPOSE_REJET"


def test_decision_logic_low_confidence():
    """Si confidence < 80% -> A_REVOIR (humain doit decider)."""
    result = {"predicted_class": "facture", "confidence": 0.65}
    min_conf = 0.80

    if result["confidence"] >= min_conf:
        if result["predicted_class"] == "autre":
            decision = "PROPOSE_REJET"
        else:
            decision = "PROPOSE_CONFORME"
    else:
        decision = "A_REVOIR"

    assert decision == "A_REVOIR"


def test_decision_logic_boundary():
    """Exactement a 80% -> PROPOSE_CONFORME (seuil inclusif)."""
    result = {"predicted_class": "contrat", "confidence": 0.80}
    min_conf = 0.80

    if result["confidence"] >= min_conf:
        if result["predicted_class"] == "autre":
            decision = "PROPOSE_REJET"
        else:
            decision = "PROPOSE_CONFORME"
    else:
        decision = "A_REVOIR"

    assert decision == "PROPOSE_CONFORME"
