#!/usr/bin/env python3
"""Script principal : genere le corpus de documents fictifs.

Usage:
    python generate.py                    # Plan minimal complet
    python generate.py --count 2          # 2 docs par gabarit (test rapide)
    python generate.py --classes facture   # Une seule classe
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

from entities.fake_entities import generate_pools
from content_generators import GENERATORS
from renderer import render_html, html_to_pdf
from degradations.degrade import degrade

ROOT = Path(__file__).resolve().parent.parent.parent  # repo root
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
ANNOTATIONS_DIR = DATA_DIR / "annotations"

# Plan minimal (dataset-strategy.md §2.2)
PLAN_MINIMAL = {
    "facture": {"gabarits": ["v1", "v2", "v3"], "split": {}},
    "fiche_de_paie": {"gabarits": ["v1", "v2", "v3"], "split": {}},
    "contrat": {"gabarits": ["v1", "v2", "v3"], "split": {}},
    "compte_rendu_rd": {"gabarits": ["v1", "v2", "v3"], "split": {}},
    "devis": {"gabarits": ["v1", "v2", "v3"], "split": {}},
    "compte_rendu_non_rd": {"gabarits": ["v1", "v2", "v3"], "split": {}},
    "releve_bancaire": {"gabarits": ["v1", "v2", "v3"], "split": {}},
    "cgv_notice": {"gabarits": ["v1", "v2", "v3"], "split": {}},
}

CLASS_TO_POOL = {
    "train": "A",
    "val": "B",
    "test": "C",
}

DEGRADATION_WEIGHTS = {0: 0.35, 1: 0.40, 2: 0.25}


def _pick_degradation_level(seed: int) -> int:
    random.seed(seed)
    r = random.random()
    if r < DEGRADATION_WEIGHTS[0]:
        return 0
    elif r < DEGRADATION_WEIGHTS[0] + DEGRADATION_WEIGHTS[1]:
        return 1
    return 2


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _assign_splits(gabarits: list[str], classe: str) -> dict[str, str]:
    """Simple split assignment: first gabarits train, then val, then test."""
    splits = {}
    n = len(gabarits)
    if n == 1:
        splits[gabarits[0]] = "train"
    elif n == 2:
        splits[gabarits[0]] = "train"
        splits[gabarits[1]] = "test"
    elif n == 3:
        splits[gabarits[0]] = "train"
        splits[gabarits[1]] = "val"
        splits[gabarits[2]] = "test"
    else:
        # 3 train, 1 val, 2 test for 6 gabarits
        for i, g in enumerate(gabarits):
            if i < n - 3:
                splits[g] = "train"
            elif i < n - 2:
                splits[g] = "val"
            else:
                splits[g] = "test"
    return splits


def main():
    parser = argparse.ArgumentParser(description="Genere le corpus de documents fictifs")
    parser.add_argument("--count", type=int, default=10, help="Documents par gabarit")
    parser.add_argument("--classes", nargs="*", help="Classes a generer (toutes si omis)")
    parser.add_argument("--seed", type=int, default=42, help="Graine globale")
    args = parser.parse_args()

    print(f"=== Generateur de corpus fictif ===")
    print(f"Documents par gabarit : {args.count}")
    print(f"Graine : {args.seed}")
    print()

    pools = generate_pools(seed=args.seed)
    manifest_rows = []
    verite_terrain_rows = []
    doc_counter = 0

    classes_to_gen = args.classes or list(GENERATORS.keys())

    for classe_or_subtype in classes_to_gen:
        generator = GENERATORS.get(classe_or_subtype)
        if not generator:
            print(f"  [SKIP] Generateur inconnu : {classe_or_subtype}")
            continue

        config = PLAN_MINIMAL.get(classe_or_subtype, {"gabarits": ["v1"], "split": {}})
        gabarits = config["gabarits"]
        splits = config.get("split") or _assign_splits(gabarits, classe_or_subtype)

        print(f"--- {classe_or_subtype} ({len(gabarits)} gabarits x {args.count} docs) ---")

        for gabarit_id in gabarits:
            split = splits.get(gabarit_id, "train")
            pool_id = CLASS_TO_POOL.get(split, "A")
            pool = pools[pool_id]

            for i in range(args.count):
                doc_counter += 1
                doc_id = f"d{doc_counter:05d}"
                seed_doc = args.seed * 10000 + doc_counter

                try:
                    result = generator(pool, gabarit_id, seed_doc)
                except Exception as e:
                    print(f"  [ERR] {doc_id} : {e}")
                    continue

                classe = result["classe"]
                sous_type = result["sous_type"]
                template_name = result["template"]
                data = result["data"]

                # Pick the template that exists, fallback to v1
                from pathlib import Path as P
                templates_dir = P(__file__).parent / "templates"
                if not (templates_dir / template_name).exists():
                    # fallback: use v1 of the base type
                    base = classe_or_subtype if classe_or_subtype in GENERATORS else classe
                    template_name = f"{base}_v1.html"
                    if not (templates_dir / template_name).exists():
                        print(f"  [SKIP] Template introuvable : {template_name}")
                        continue

                # Render
                try:
                    html = render_html(template_name, data)
                except Exception as e:
                    print(f"  [ERR] Rendu {doc_id} : {e}")
                    continue

                pdf_raw = RAW_DIR / classe / f"{doc_id}.pdf"
                try:
                    html_to_pdf(html, pdf_raw)
                except Exception as e:
                    print(f"  [ERR] PDF {doc_id} : {e}")
                    continue

                # Degradation
                deg_level = _pick_degradation_level(seed_doc)
                deg_descriptions = []

                if deg_level == 0:
                    final_path = pdf_raw
                    format_source = "pdf_natif"
                else:
                    try:
                        final_path, deg_level, deg_descriptions = degrade(
                            pdf_raw, INTERIM_DIR / classe, deg_level, seed_doc
                        )
                        format_source = "pdf_scan"
                    except Exception as e:
                        print(f"  [WARN] Degradation {doc_id} : {e} — on garde le PDF natif")
                        final_path = pdf_raw
                        deg_level = 0
                        format_source = "pdf_natif"

                sha = _sha256(final_path)

                manifest_rows.append({
                    "doc_id": doc_id,
                    "sha256": sha,
                    "classe": classe,
                    "sous_type": sous_type,
                    "provenance": "fictif_genere",
                    "gabarit_id": f"{classe_or_subtype}_{gabarit_id}",
                    "auteur_gabarit": "equipe",
                    "pool_entites": pool_id,
                    "jeu": "dev" if split in ("train", "val") else split,
                    "split": split,
                    "langue": "fr",
                    "format_source": format_source,
                    "niveau_degradation": deg_level,
                    "degradations": "|".join(deg_descriptions),
                    "nb_pages": 1,
                    "seed_generation": seed_doc,
                })

                if result.get("verite_terrain"):
                    vt = result["verite_terrain"].copy()
                    vt["doc_id"] = doc_id
                    verite_terrain_rows.append(vt)

                print(f"  {doc_id} [{classe}] gabarit={gabarit_id} split={split} deg={deg_level}")

    # Write manifest
    ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = ANNOTATIONS_DIR / "manifest.csv"
    if manifest_rows:
        fieldnames = list(manifest_rows[0].keys())
        with open(manifest_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(manifest_rows)
        print(f"\nManifeste : {manifest_path} ({len(manifest_rows)} documents)")

    # Write verite terrain
    if verite_terrain_rows:
        vt_path = ANNOTATIONS_DIR / "verite_terrain.jsonl"
        with open(vt_path, "w", encoding="utf-8") as f:
            for row in verite_terrain_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"Verite terrain : {vt_path} ({len(verite_terrain_rows)} entrees)")

    # Write splits
    splits_path = ANNOTATIONS_DIR / "splits.csv"
    with open(splits_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["doc_id", "split"])
        writer.writeheader()
        for row in manifest_rows:
            writer.writerow({"doc_id": row["doc_id"], "split": row["split"]})
    print(f"Splits : {splits_path}")

    print(f"\n=== Termine : {len(manifest_rows)} documents generes ===")


if __name__ == "__main__":
    main()
