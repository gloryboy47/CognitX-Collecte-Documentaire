"""Validation metier des documents.

Verifie la coherence des champs extraits selon des regles par type de document.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ValidationResult:
    rule_name: str
    passed: bool
    message: str


def validate_document(text: str, predicted_class: str, extracted_fields: dict[str, str]) -> list[ValidationResult]:
    """Execute les regles de validation pour un type de document."""
    results = []

    results.extend(_validate_common(text))

    validators = {
        "facture": _validate_facture,
        "fiche_de_paie": _validate_fiche_de_paie,
        "contrat": _validate_contrat,
        "compte_rendu_rd": _validate_compte_rendu_rd,
    }

    validator = validators.get(predicted_class)
    if validator:
        results.extend(validator(text, extracted_fields))

    return results


def _validate_common(text: str) -> list[ValidationResult]:
    results = []

    if len(text.strip()) < 50:
        results.append(ValidationResult(
            rule_name="texte_minimum",
            passed=False,
            message="Le texte extrait est trop court (< 50 caracteres)",
        ))
    else:
        results.append(ValidationResult(
            rule_name="texte_minimum",
            passed=True,
            message="Texte suffisamment long",
        ))

    if len(text.strip()) > 0:
        alpha_ratio = sum(c.isalpha() for c in text) / len(text)
        if alpha_ratio < 0.3:
            results.append(ValidationResult(
                rule_name="qualite_ocr",
                passed=False,
                message=f"Ratio alphabetique faible ({alpha_ratio:.0%}), OCR potentiellement mauvais",
            ))
        else:
            results.append(ValidationResult(
                rule_name="qualite_ocr",
                passed=True,
                message="Qualite OCR acceptable",
            ))

    return results


def _validate_facture(text: str, fields: dict[str, str]) -> list[ValidationResult]:
    results = []

    if "montant_ttc" in fields or "montant_ht" in fields:
        results.append(ValidationResult("montant_present", True, "Montant detecte"))
    else:
        results.append(ValidationResult("montant_present", False, "Aucun montant detecte"))

    if "numero_facture" in fields:
        results.append(ValidationResult("numero_facture", True, "Numero de facture detecte"))
    else:
        results.append(ValidationResult("numero_facture", False, "Numero de facture manquant"))

    text_lower = text.lower()
    if re.search(r"t\.?v\.?a\.?", text_lower):
        results.append(ValidationResult("mention_tva", True, "Mention TVA presente"))
    else:
        results.append(ValidationResult("mention_tva", False, "Mention TVA absente"))

    return results


def _validate_fiche_de_paie(text: str, fields: dict[str, str]) -> list[ValidationResult]:
    results = []

    if "salaire_net" in fields:
        results.append(ValidationResult("net_a_payer", True, "Net a payer detecte"))
    else:
        results.append(ValidationResult("net_a_payer", False, "Net a payer manquant"))

    if "salaire_brut" in fields:
        results.append(ValidationResult("salaire_brut", True, "Salaire brut detecte"))
    else:
        results.append(ValidationResult("salaire_brut", False, "Salaire brut manquant"))

    return results


def _validate_contrat(text: str, fields: dict[str, str]) -> list[ValidationResult]:
    results = []

    text_lower = text.lower()
    has_signatures = bool(re.search(r"sign(?:ature|e)", text_lower))
    results.append(ValidationResult(
        "mention_signature",
        has_signatures,
        "Mention de signature detectee" if has_signatures else "Aucune mention de signature",
    ))

    has_parties = bool(re.search(r"(?:entre|soussign)", text_lower))
    results.append(ValidationResult(
        "parties_identifiees",
        has_parties,
        "Parties identifiees" if has_parties else "Parties non identifiees",
    ))

    return results


def _validate_compte_rendu_rd(text: str, fields: dict[str, str]) -> list[ValidationResult]:
    results = []

    text_lower = text.lower()
    has_rd = bool(re.search(r"r\s*(?:&|et)\s*d|recherche.*d[ée]veloppement", text_lower))
    results.append(ValidationResult(
        "mention_rd",
        has_rd,
        "Mention R&D detectee" if has_rd else "Aucune mention R&D",
    ))

    if "date_reunion" in fields:
        results.append(ValidationResult("date_reunion", True, "Date de reunion detectee"))
    else:
        results.append(ValidationResult("date_reunion", False, "Date de reunion manquante"))

    return results
