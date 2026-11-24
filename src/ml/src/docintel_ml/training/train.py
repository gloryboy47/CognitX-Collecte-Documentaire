"""Entrainement du pipeline TF-IDF + Logistic Regression (baseline P1)."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from docintel_ml.features.text_features import build_feature_union
from docintel_ml.evaluation.evaluate import full_evaluation

SEED = 42
CLASSES = ["facture", "fiche_de_paie", "contrat", "compte_rendu_rd", "autre"]


def train_model(data_dir: Path, artifacts_dir: Path, reports_dir: Path) -> dict:
    df = pd.read_csv(data_dir / "processed" / "dataset.csv")

    train = df[df["split"] == "train"]
    val = df[df["split"] == "val"]
    test = df[df["split"] == "test"]

    X_train, y_train = train["text"].values, train["classe"].values
    X_val, y_val = val["text"].values, val["classe"].values
    X_test, y_test = test["text"].values, test["classe"].values

    pipeline = Pipeline([
        ("features", build_feature_union()),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            random_state=SEED,
            class_weight="balanced",
        )),
    ])

    t0 = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - t0

    results_val = full_evaluation(pipeline, X_val, y_val, CLASSES, "validation")
    results_test = full_evaluation(pipeline, X_test, y_test, CLASSES, "test")

    out = artifacts_dir / "current"
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, out / "model.joblib")

    metadata = {
        "model_name": "tfidf_rf_v2",
        "model_version": "2.0.0",
        "algorithm": "TF-IDF (word) + Keywords metier + RandomForest",
        "classes": CLASSES,
        "seed": SEED,
        "train_samples": len(train),
        "val_samples": len(val),
        "test_samples": len(test),
        "train_time_s": round(train_time, 2),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "val_metrics": results_val["summary"],
        "test_metrics": results_test["summary"],
    }
    with open(out / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    reports_dir.mkdir(parents=True, exist_ok=True)
    report_lines = _format_report(metadata, results_val, results_test)
    (reports_dir / "ml-evaluation.md").write_text("\n".join(report_lines))

    return metadata


def _format_report(meta: dict, val_res: dict, test_res: dict) -> list[str]:
    lines = [
        "# Evaluation du modele ML — Baseline P1",
        "",
        f"**Algorithme** : {meta['algorithm']}",
        f"**Version** : {meta['model_version']}",
        f"**Date** : {meta['trained_at']}",
        f"**Temps d'entrainement** : {meta['train_time_s']}s",
        "",
        f"## Corpus",
        f"- Train : {meta['train_samples']} documents",
        f"- Validation : {meta['val_samples']} documents",
        f"- Test : {meta['test_samples']} documents",
        "",
    ]
    for name, res in [("Validation", val_res), ("Test", test_res)]:
        s = res["summary"]
        lines.extend([
            f"## {name}",
            f"- **Accuracy** : {s['accuracy']:.4f}",
            f"- **F1 macro** : {s['f1_macro']:.4f}",
            f"- **F1 weighted** : {s['f1_weighted']:.4f}",
            "",
            "### Matrice de confusion",
            "```",
            res["confusion_matrix_str"],
            "```",
            "",
            "### Rapport par classe",
            "```",
            res["classification_report"],
            "```",
            "",
        ])
    return lines


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[5]
    meta = train_model(
        data_dir=repo / "data",
        artifacts_dir=repo / "src" / "ml" / "artifacts",
        reports_dir=repo / "reports",
    )
    print(f"\nModele entraine: {meta['model_name']} v{meta['model_version']}")
    print(f"Val  F1 macro: {meta['val_metrics']['f1_macro']:.4f}")
    print(f"Test F1 macro: {meta['test_metrics']['f1_macro']:.4f}")
