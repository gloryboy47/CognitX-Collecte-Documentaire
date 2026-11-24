"""Extraction de champs metier depuis le texte OCR.

Chaque type de document a ses propres regles d'extraction (regex).
Les champs extraits sont stockes en base pour affichage dans la revue.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ExtractedFieldResult:
    field_name: str
    field_value: str
    source: str = "regex"


EXTRACTORS: dict[str, list[tuple[str, str]]] = {
    "facture": [
        ("numero_facture", r"(?:facture|invoice)\s*(?:n[°o]?\.?\s*)?[:.]?\s*([A-Z0-9][\w-]{2,20})"),
        ("montant_ht", r"(?:total|montant)\s*h\.?t\.?\s*[:.]?\s*([\d\s]+[.,]\d{2})\s*€?"),
        ("montant_ttc", r"(?:total|montant)\s*t\.?t\.?c\.?\s*[:.]?\s*([\d\s]+[.,]\d{2})\s*€?"),
        ("date_facture", r"(?:date|emise?\s*le)\s*[:.]?\s*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})"),
        ("tva", r"t\.?v\.?a\.?\s*[:.]?\s*([\d,]+)\s*%"),
    ],
    "fiche_de_paie": [
        ("salaire_brut", r"(?:salaire|remuneration)\s*brut[e]?\s*[:.]?\s*([\d\s]+[.,]\d{2})"),
        ("salaire_net", r"net\s*(?:a|à)\s*payer\s*[:.]?\s*([\d\s]+[.,]\d{2})"),
        ("periode", r"(?:periode|mois|p[ée]riode)\s*[:.]?\s*([\w\s]+\d{4})"),
        ("employeur", r"(?:employeur|entreprise|societe)\s*[:.]?\s*(.{3,60})"),
    ],
    "contrat": [
        ("type_contrat", r"contrat\s+(?:de\s+)?([\w\s]{3,30}?)(?:\s*entre|\s*n[°o])"),
        ("date_debut", r"(?:date\s*(?:de\s*)?(?:debut|d[ée]but|effet))\s*[:.]?\s*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})"),
        ("duree", r"(?:dur[ée]e)\s*[:.]?\s*(.{3,30})"),
    ],
    "compte_rendu_rd": [
        ("date_reunion", r"(?:date|du)\s*[:.]?\s*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})"),
        ("projet", r"(?:projet|programme)\s*[:.]?\s*(.{3,60})"),
        ("participants", r"(?:participants?|pr[ée]sents?)\s*[:.]?\s*(.{3,100})"),
    ],
}


def extract_fields(text: str, predicted_class: str) -> list[ExtractedFieldResult]:
    """Extrait les champs metier du texte selon la classe predite."""
    rules = EXTRACTORS.get(predicted_class, [])
    results = []
    text_lower = text.lower()

    for field_name, pattern in rules:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            results.append(ExtractedFieldResult(
                field_name=field_name,
                field_value=value,
            ))

    return results
