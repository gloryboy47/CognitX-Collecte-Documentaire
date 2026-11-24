"""Prepare le dataset a partir du corpus genere : extrait le texte OCR de chaque PDF."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


def extract_text_from_pdf(pdf_path: Path) -> str:
    import pymupdf
    doc = pymupdf.open(str(pdf_path))
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages).strip()


def build_dataset(data_dir: Path) -> pd.DataFrame:
    """Lit manifest.csv et extrait le texte de chaque PDF.

    Retourne un DataFrame avec colonnes: doc_id, classe, sous_type, split, text
    """
    annotations_dir = data_dir / "annotations"
    manifest = pd.read_csv(annotations_dir / "manifest.csv")
    splits = pd.read_csv(annotations_dir / "splits.csv")

    df = manifest.merge(splits, on="doc_id")
    if "split_x" in df.columns:
        df = df.rename(columns={"split_x": "split"})
        df = df.drop(columns=["split_y"], errors="ignore")

    raw_dir = data_dir / "raw"
    texts = []
    for _, row in df.iterrows():
        pdf_path = raw_dir / row["classe"] / f"{row['doc_id']}.pdf"
        if pdf_path.exists():
            text = extract_text_from_pdf(pdf_path)
        else:
            text = ""
        texts.append(text)

    df["text"] = texts
    df = df[df["text"].str.len() > 0].reset_index(drop=True)

    return df[["doc_id", "classe", "sous_type", "split", "text"]]


if __name__ == "__main__":
    import sys
    repo_root = Path(__file__).resolve().parents[5]
    data_dir = repo_root / "data"

    df = build_dataset(data_dir)
    out = data_dir / "processed" / "dataset.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Dataset: {len(df)} documents")
    print(df["classe"].value_counts())
    print(f"\nSplit distribution:")
    print(df.groupby(["split", "classe"]).size().unstack(fill_value=0))
    print(f"\nSaved to {out}")
