"""Feature engineering: TF-IDF + indices simples (longueur, densite chiffres, montants)."""

from __future__ import annotations

import re

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from scipy.sparse import hstack, csr_matrix


class SimpleFeatures(BaseEstimator, TransformerMixin):
    """Indices numeriques extraits du texte brut."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = []
        for text in X:
            length = len(text)
            n_digits = sum(c.isdigit() for c in text)
            digit_density = n_digits / max(length, 1)
            n_amounts = len(re.findall(r"\d+[.,]\d{2}\s*€?", text))
            n_lines = text.count("\n") + 1
            n_upper = sum(c.isupper() for c in text)
            upper_ratio = n_upper / max(length, 1)
            features.append([length, digit_density, n_amounts, n_lines, upper_ratio])
        return csr_matrix(np.array(features, dtype=np.float64))


def normalize_spaced_text(text: str) -> str:
    """Collapse spaced-out headings like 'F A C T U R E' into 'FACTURE'."""
    def _collapse(m: re.Match) -> str:
        chars = m.group(0).split()
        return " ".join("".join(g) for g in _split_words(chars))

    def _split_words(chars: list[str]) -> list[list[str]]:
        words, current = [], []
        for c in chars:
            if len(c) == 1 and c.isalpha():
                current.append(c)
            else:
                if current:
                    words.append(current)
                    current = []
                words.append([c])
        if current:
            words.append(current)
        return words

    return re.sub(r"(?:[A-ZÀ-Ÿa-zà-ÿ]\s+){2,}[A-ZÀ-Ÿa-zà-ÿ]", _collapse, text)


class KeywordFeatures(BaseEstimator, TransformerMixin):
    """Indicateurs metier : comptages de mots-cles + ratios discriminants."""

    KEYWORD_GROUPS = {
        "kw_facture": [r"facture", r"honoraires", r"(?:e|é)ch(?:e|é)ance"],
        "kw_paie": [r"bulletin.*(?:paie|salaire)", r"salaire\s*(?:brut|net)", r"cotisation", r"net\s*(?:a|à)\s*payer"],
        "kw_contrat": [r"contrat", r"entre\s*les\s*(?:parties|soussign)", r"article\s*\d", r"il\s*est\s*convenu"],
        "kw_cr_rd": [r"r\s*(?:&|et)\s*d", r"recherche.*d(?:e|é)veloppement", r"(?:indicateur|kpi|livrable).*technique"],
        "kw_devis": [r"devis", r"non\s*contractuel", r"valable\s*jusqu"],
        "kw_releve": [r"rel(?:e|è)v(?:e|é).*compte", r"d(?:e|é)bit", r"cr(?:e|é)dit", r"virement"],
        "kw_cgv": [r"conditions\s*g(?:e|é)n(?:e|é)rales", r"mentions?\s*l(?:e|é)gales"],
        "kw_cr_nonrd": [r"(?:compte|c)[\s-]*rendu(?!.*(?:r.?d|recherche|technique))", r"r(?:e|é)union"],
    }

    BINARY_INDICATORS = [
        (r"facture", "has_facture"),
        (r"devis", "has_devis"),
        (r"rel(?:e|è)v(?:e|é)", "has_releve"),
        (r"bulletin", "has_bulletin"),
        (r"contrat", "has_contrat"),
        (r"(?:e|é)ch(?:e|é)ance", "has_echeance"),
        (r"non\s*contractuel", "has_non_contractuel"),
        (r"valable", "has_valable"),
        (r"d(?:e|é)bit", "has_debit"),
        (r"cr(?:e|é)dit", "has_credit"),
        (r"total\s*(?:ht|ttc)", "has_total_ht"),
        (r"tva", "has_tva"),
        (r"iban", "has_iban"),
        (r"solde", "has_solde"),
        (r"cotisation", "has_cotisation"),
        (r"article\s*\d", "has_article"),
        (r"r\s*(?:&|et)\s*d", "has_rd"),
    ]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = []
        for text in X:
            normalized = normalize_spaced_text(text).lower()
            row = []
            for group_patterns in self.KEYWORD_GROUPS.values():
                count = sum(len(re.findall(p, normalized)) for p in group_patterns)
                row.append(min(count, 10))
            for pattern, _ in self.BINARY_INDICATORS:
                row.append(1.0 if re.search(pattern, normalized) else 0.0)

            has_facture = bool(re.search(r"facture", normalized))
            has_devis = bool(re.search(r"devis", normalized))
            has_releve = bool(re.search(r"rel(?:e|è)v(?:e|é)", normalized))
            has_echeance = bool(re.search(r"(?:e|é)ch(?:e|é)ance", normalized))
            has_debit = bool(re.search(r"d(?:e|é)bit", normalized))
            has_total_ht = bool(re.search(r"total\s*(?:ht|ttc)", normalized))

            row.append(1.0 if has_facture and not has_devis else 0.0)
            row.append(1.0 if has_devis and not has_facture else 0.0)
            row.append(1.0 if has_releve and has_debit else 0.0)
            row.append(1.0 if has_total_ht and has_echeance and not has_devis else 0.0)
            row.append(1.0 if has_releve and not has_total_ht else 0.0)

            features.append(row)
        return csr_matrix(np.array(features, dtype=np.float64))


class TextNormalizer(BaseEstimator, TransformerMixin):
    """Normalise le texte OCR avant TF-IDF : collapse les lettres espacees, lowercase."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [normalize_spaced_text(text).lower() for text in X]


def build_feature_union() -> FeatureUnion:
    return FeatureUnion([
        ("tfidf_word", Pipeline([
            ("norm", TextNormalizer()),
            ("tfidf", TfidfVectorizer(
                analyzer="word",
                max_features=500,
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=1,
            )),
        ])),
        ("simple", SimpleFeatures()),
        ("keywords", KeywordFeatures()),
    ])
