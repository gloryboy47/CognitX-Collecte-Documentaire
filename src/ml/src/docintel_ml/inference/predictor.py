"""Module d'inference : charge le modele et predit la classe d'un document."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np


_model = None
_metadata = None
_artifacts_dir = Path(__file__).resolve().parents[3] / "artifacts" / "current"


def _load_model():
    global _model, _metadata
    model_path = _artifacts_dir / "model.joblib"
    meta_path = _artifacts_dir / "metadata.json"
    if not model_path.exists():
        return
    _model = joblib.load(model_path)
    if meta_path.exists():
        with open(meta_path) as f:
            _metadata = json.load(f)


def predict(text: str) -> dict[str, Any]:
    """Predit la classe d'un document a partir de son texte OCR.

    Returns dict avec: predicted_class, confidence, probabilities, model_version
    """
    if _model is None:
        _load_model()

    if _model is None:
        return {
            "predicted_class": "autre",
            "confidence": 0.0,
            "probabilities": {},
            "top_features": [],
            "model_version": "none",
        }

    proba = _model.predict_proba([text])[0]
    classes = _model.classes_.tolist()
    predicted_idx = int(np.argmax(proba))
    predicted_class = classes[predicted_idx]
    confidence = float(proba[predicted_idx])

    probabilities = {cls: round(float(p), 4) for cls, p in zip(classes, proba)}

    top_features = _extract_top_features(text, predicted_class, classes)

    version = _metadata["model_version"] if _metadata else "unknown"

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "probabilities": probabilities,
        "top_features": top_features,
        "model_version": version,
    }


def _extract_top_features(text: str, predicted_class: str, classes: list[str]) -> list[str]:
    """Extrait les mots les plus influents pour la prediction."""
    try:
        feature_union = _model.named_steps["features"]
        clf = _model.named_steps["clf"]

        tfidf_step = feature_union.transformer_list[0]
        if hasattr(tfidf_step[1], "named_steps"):
            tfidf = tfidf_step[1].named_steps["tfidf"]
        else:
            tfidf = tfidf_step[1]

        feature_names = tfidf.get_feature_names_out()

        if hasattr(clf, "coef_"):
            class_idx = classes.index(predicted_class)
            coefs = clf.coef_[class_idx] if clf.coef_.ndim > 1 else clf.coef_[0]
            n_tfidf = len(feature_names)
            tfidf_coefs = coefs[:n_tfidf]
            top_indices = np.argsort(tfidf_coefs)[-5:][::-1]
            return [feature_names[i] for i in top_indices if tfidf_coefs[i] > 0]
        elif hasattr(clf, "feature_importances_"):
            importances = clf.feature_importances_
            n_tfidf = len(feature_names)
            tfidf_imp = importances[:n_tfidf]
            top_indices = np.argsort(tfidf_imp)[-5:][::-1]
            return [feature_names[i] for i in top_indices if tfidf_imp[i] > 0]

        return []
    except Exception:
        return []


def reload_model():
    """Force le rechargement du modele (apres un re-entrainement)."""
    global _model, _metadata
    _model = None
    _metadata = None
    _load_model()
