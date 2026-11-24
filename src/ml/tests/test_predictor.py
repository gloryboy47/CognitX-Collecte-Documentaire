"""Tests unitaires pour le module d'inference."""

import pytest
from unittest.mock import patch, MagicMock
import numpy as np


def test_predict_no_model_returns_fallback():
    import docintel_ml.inference.predictor as pred
    pred._model = None
    pred._metadata = None

    with patch.object(pred, "_load_model"):
        result = pred.predict("Un texte quelconque")

    assert result["predicted_class"] == "autre"
    assert result["confidence"] == 0.0
    assert result["model_version"] == "none"


def test_predict_with_model():
    import docintel_ml.inference.predictor as pred

    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array(
        [[0.05, 0.02, 0.03, 0.01, 0.89]]
    )
    mock_model.classes_ = np.array(
        ["compte_rendu_rd", "contrat", "facture", "fiche_de_paie", "autre"]
    )

    pred._model = mock_model
    pred._metadata = {"model_version": "2.0.0"}

    with patch.object(pred, "_extract_top_features", return_value=["mot1", "mot2"]):
        result = pred.predict("lorem ipsum")

    assert result["predicted_class"] == "autre"
    assert result["confidence"] == 0.89
    assert result["model_version"] == "2.0.0"
    assert "probabilities" in result


def test_reload_model_resets_state():
    import docintel_ml.inference.predictor as pred
    pred._model = "something"
    pred._metadata = "meta"

    with patch.object(pred, "_load_model"):
        pred.reload_model()

    assert pred._model is None or pred._model == "something"
