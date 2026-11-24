"""Compare plusieurs algorithmes sur le meme corpus."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import ComplementNB
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score, accuracy_score, classification_report

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from docintel_ml.features.text_features import build_feature_union

warnings.filterwarnings("ignore")

SEED = 42
CLASSES = ["facture", "fiche_de_paie", "contrat", "compte_rendu_rd", "autre"]


def main():
    repo = Path(__file__).resolve().parents[5]
    df = pd.read_csv(repo / "data" / "processed" / "dataset.csv")

    train = df[df["split"] == "train"]
    val = df[df["split"] == "val"]
    test = df[df["split"] == "test"]

    X_train, y_train = train["text"].values, train["classe"].values
    X_val, y_val = val["text"].values, val["classe"].values
    X_test, y_test = test["text"].values, test["classe"].values

    models = {
        "LogReg C=1": LogisticRegression(C=1.0, max_iter=5000, solver="lbfgs", random_state=SEED),
        "LogReg C=0.1": LogisticRegression(C=0.1, max_iter=5000, solver="lbfgs", random_state=SEED),
        "LogReg balanced": LogisticRegression(C=1.0, max_iter=5000, solver="lbfgs", random_state=SEED, class_weight="balanced"),
        "RandomForest": RandomForestClassifier(n_estimators=200, max_depth=15, random_state=SEED, class_weight="balanced"),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=SEED, learning_rate=0.1),
        "ComplementNB": ComplementNB(alpha=1.0),
    }

    print(f"{'Model':>25} | {'Val Acc':>8} | {'Val F1m':>8} | {'Test Acc':>9} | {'Test F1m':>9} | {'Test errors':>12}")
    print("-" * 90)

    for name, clf in models.items():
        pipe = Pipeline([
            ("features", build_feature_union()),
            ("clf", clf),
        ])
        pipe.fit(X_train, y_train)

        val_pred = pipe.predict(X_val)
        test_pred = pipe.predict(X_test)

        val_acc = accuracy_score(y_val, val_pred)
        val_f1 = f1_score(y_val, val_pred, average="macro", labels=CLASSES)
        test_acc = accuracy_score(y_test, test_pred)
        test_f1 = f1_score(y_test, test_pred, average="macro", labels=CLASSES)

        n_errors = (y_test != test_pred).sum()

        print(f"{name:>25} | {val_acc:>8.4f} | {val_f1:>8.4f} | {test_acc:>9.4f} | {test_f1:>9.4f} | {n_errors:>12}")

    print("\n--- Best model details ---")
    best_pipe = Pipeline([
        ("features", build_feature_union()),
        ("clf", RandomForestClassifier(n_estimators=200, max_depth=15, random_state=SEED, class_weight="balanced")),
    ])
    best_pipe.fit(X_train, y_train)
    test_pred = best_pipe.predict(X_test)
    print(classification_report(y_test, test_pred, labels=CLASSES, digits=4))

    test_df = test.copy()
    test_df["pred"] = test_pred
    wrong = test_df[test_df["classe"] != test_df["pred"]]
    if len(wrong) > 0:
        print("Remaining errors:")
        for _, r in wrong.iterrows():
            print(f"  {r['sous_type']:>30} -> {r['pred']}")


if __name__ == "__main__":
    main()
