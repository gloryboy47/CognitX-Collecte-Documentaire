"""Evaluation complete : metriques, matrice de confusion, rapport par classe."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)


def full_evaluation(model, X, y_true, classes: list[str], split_name: str) -> dict:
    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)

    acc = accuracy_score(y_true, y_pred)
    f1_mac = f1_score(y_true, y_pred, average="macro", labels=classes)
    f1_w = f1_score(y_true, y_pred, average="weighted", labels=classes)

    cm = confusion_matrix(y_true, y_pred, labels=classes)
    cr = classification_report(y_true, y_pred, labels=classes, digits=4)

    max_label = max(len(c) for c in classes)
    header = " " * (max_label + 2) + "  ".join(f"{c[:6]:>6}" for c in classes)
    rows = []
    for i, cls in enumerate(classes):
        row_vals = "  ".join(f"{cm[i, j]:>6}" for j in range(len(classes)))
        rows.append(f"{cls:>{max_label}}  {row_vals}")
    cm_str = header + "\n" + "\n".join(rows)

    confidences = np.max(y_proba, axis=1)

    return {
        "split": split_name,
        "summary": {
            "accuracy": round(float(acc), 4),
            "f1_macro": round(float(f1_mac), 4),
            "f1_weighted": round(float(f1_w), 4),
            "mean_confidence": round(float(np.mean(confidences)), 4),
        },
        "confusion_matrix": cm.tolist(),
        "confusion_matrix_str": cm_str,
        "classification_report": cr,
    }
