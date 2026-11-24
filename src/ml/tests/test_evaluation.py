"""Tests unitaires pour le module d'evaluation."""

import numpy as np
import pytest
from unittest.mock import MagicMock

from docintel_ml.evaluation.evaluate import full_evaluation


class TestFullEvaluation:
    def setup_method(self):
        self.classes = ["facture", "fiche_de_paie", "contrat", "compte_rendu_rd", "autre"]

    def _make_mock_model(self, y_pred, y_proba):
        model = MagicMock()
        model.predict.return_value = np.array(y_pred)
        model.predict_proba.return_value = np.array(y_proba)
        return model

    def test_perfect_predictions(self):
        y_true = ["facture", "contrat", "autre"]
        y_pred = ["facture", "contrat", "autre"]
        y_proba = [
            [0.95, 0.01, 0.02, 0.01, 0.01],
            [0.01, 0.01, 0.95, 0.02, 0.01],
            [0.01, 0.01, 0.01, 0.01, 0.96],
        ]
        model = self._make_mock_model(y_pred, y_proba)
        result = full_evaluation(model, ["t1", "t2", "t3"], y_true, self.classes, "test")

        assert result["split"] == "test"
        assert result["summary"]["accuracy"] == 1.0
        assert result["summary"]["f1_macro"] == 1.0
        assert "confusion_matrix" in result
        assert "classification_report" in result
        assert "confusion_matrix_str" in result

    def test_partial_predictions(self):
        y_true = ["facture", "facture", "contrat"]
        y_pred = ["facture", "contrat", "contrat"]
        y_proba = [
            [0.9, 0.02, 0.05, 0.02, 0.01],
            [0.3, 0.1, 0.5, 0.05, 0.05],
            [0.05, 0.02, 0.9, 0.02, 0.01],
        ]
        model = self._make_mock_model(y_pred, y_proba)
        result = full_evaluation(model, ["t1", "t2", "t3"], y_true, self.classes, "val")

        assert result["summary"]["accuracy"] < 1.0
        assert result["summary"]["mean_confidence"] > 0

    def test_confusion_matrix_shape(self):
        y_true = ["facture", "contrat"]
        y_pred = ["facture", "contrat"]
        y_proba = [
            [0.95, 0.01, 0.02, 0.01, 0.01],
            [0.01, 0.01, 0.95, 0.02, 0.01],
        ]
        model = self._make_mock_model(y_pred, y_proba)
        result = full_evaluation(model, ["t1", "t2"], y_true, self.classes, "test")

        cm = result["confusion_matrix"]
        assert len(cm) == len(self.classes)
        assert len(cm[0]) == len(self.classes)
