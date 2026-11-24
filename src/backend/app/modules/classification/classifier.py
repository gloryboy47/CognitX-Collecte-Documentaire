"""Classification de documents par le texte OCR.

Charge le modele ML entraine s'il existe, sinon fallback par mots-cles.
"""

import json
import sys
from pathlib import Path

import numpy as np

from app.core.config import settings

_model = None
_metadata = None
_model_loaded = False


def _resolve_model_path() -> Path:
    p = Path(settings.ML_MODEL_PATH)
    if p.is_absolute():
        return p
    backend_dir = Path(__file__).resolve().parents[3]
    for candidate in [backend_dir / p, backend_dir.parent.parent / p]:
        if (candidate / "model.joblib").exists():
            return candidate
    return p


def _load_model():
    global _model, _metadata, _model_loaded
    _model_loaded = True
    model_dir = _resolve_model_path()
    model_file = model_dir / "model.joblib"
    if not model_file.exists():
        return

    try:
        ml_src = str(model_dir.parent.parent / "src")
        if ml_src not in sys.path:
            sys.path.insert(0, ml_src)

        import joblib
        _model = joblib.load(model_file)
        meta_file = model_dir / "metadata.json"
        if meta_file.exists():
            _metadata = json.loads(meta_file.read_text())
    except Exception:
        _model = None


KEYWORD_RULES = {
    "facture": ["facture", "total ht", "total ttc", "tva", "montant", "echeance", "paiement"],
    "fiche_de_paie": ["bulletin", "salaire", "cotisations", "net a payer", "brut", "conges", "prelevement"],
    "contrat": ["contrat", "entre les soussignes", "article", "il est convenu", "signatures", "clause"],
    "compte_rendu_rd": ["verrou", "r&d", "recherche", "technique", "innovation", "prototype", "brevet"],
}


def classify(text: str) -> dict:
    """Retourne {predicted_class, confidence, probabilities, top_features, model_version}."""
    if not _model_loaded:
        _load_model()

    if _model is not None:
        return _classify_ml(text)
    return _classify_keywords(text)


def _classify_ml(text: str) -> dict:
    proba = _model.predict_proba([text])[0]
    classes = _model.classes_.tolist()
    idx = int(np.argmax(proba))
    predicted = classes[idx]
    confidence = float(proba[idx])
    probabilities = {c: round(float(p), 4) for c, p in zip(classes, proba)}

    top_features = []
    try:
        feature_union = _model.named_steps["features"]
        clf = _model.named_steps["clf"]
        tfidf_step = feature_union.transformer_list[0]
        if hasattr(tfidf_step[1], "named_steps"):
            tfidf = tfidf_step[1].named_steps["tfidf"]
        else:
            tfidf = tfidf_step[1]
        feature_names = tfidf.get_feature_names_out()

        if hasattr(clf, "feature_importances_"):
            imp = clf.feature_importances_[:len(feature_names)]
            top_idx = np.argsort(imp)[-5:][::-1]
            top_features = [feature_names[i] for i in top_idx if imp[i] > 0]
        elif hasattr(clf, "coef_"):
            class_idx = classes.index(predicted)
            coefs = clf.coef_[class_idx] if clf.coef_.ndim > 1 else clf.coef_[0]
            tfidf_coefs = coefs[:len(feature_names)]
            top_idx = np.argsort(tfidf_coefs)[-5:][::-1]
            top_features = [feature_names[i] for i in top_idx if tfidf_coefs[i] > 0]
    except Exception:
        pass

    version = _metadata.get("model_version", "ml") if _metadata else "ml"

    return {
        "predicted_class": predicted,
        "confidence": round(confidence, 4),
        "probabilities": json.dumps(probabilities, ensure_ascii=False),
        "top_features": ", ".join(top_features) if top_features else "",
        "model_version": version,
    }


def _classify_keywords(text: str) -> dict:
    text_lower = text.lower()
    scores = {}
    for classe, keywords in KEYWORD_RULES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[classe] = score / len(keywords)

    if max(scores.values()) == 0:
        return {
            "predicted_class": "autre",
            "confidence": 0.5,
            "probabilities": json.dumps({**scores, "autre": 0.5}, ensure_ascii=False),
            "top_features": "aucun mot-cle detecte",
            "model_version": "keywords-fallback-v1",
        }

    best = max(scores, key=scores.get)
    total = sum(scores.values()) or 1
    confidence = scores[best] / total
    probabilities = {k: round(v / total, 4) for k, v in scores.items()}
    probabilities["autre"] = round(1 - sum(probabilities.values()), 4)
    matched = [kw for kw in KEYWORD_RULES[best] if kw in text_lower]

    return {
        "predicted_class": best,
        "confidence": round(confidence, 4),
        "probabilities": json.dumps(probabilities, ensure_ascii=False),
        "top_features": ", ".join(matched[:10]),
        "model_version": "keywords-fallback-v1",
    }
