"""Tests unitaires pour le module de features."""

import numpy as np
import pytest

from docintel_ml.features.text_features import (
    SimpleFeatures,
    KeywordFeatures,
    TextNormalizer,
    normalize_spaced_text,
    build_feature_union,
)


class TestNormalizeSpacedText:
    def test_collapse_spaced_heading(self):
        assert "FACTURE" in normalize_spaced_text("F A C T U R E")

    def test_no_change_normal_text(self):
        text = "Ceci est un texte normal."
        assert normalize_spaced_text(text) == text

    def test_mixed_content(self):
        result = normalize_spaced_text("F A C T U R E n°12345")
        assert "FACTURE" in result
        assert "12345" in result


class TestSimpleFeatures:
    def setup_method(self):
        self.transformer = SimpleFeatures()

    def test_output_shape(self):
        texts = ["Bonjour le monde", "Facture n°123 : 1500,00 €"]
        result = self.transformer.fit_transform(texts)
        assert result.shape == (2, 5)

    def test_digit_density(self):
        result = self.transformer.transform(["123456"]).toarray()
        assert result[0, 1] == 1.0  # 100% digits

    def test_amounts_detected(self):
        result = self.transformer.transform(["Total: 1500,00 € et 200,50 €"]).toarray()
        assert result[0, 2] == 2  # 2 montants

    def test_empty_text(self):
        result = self.transformer.transform([""]).toarray()
        assert result[0, 0] == 0  # length = 0


class TestKeywordFeatures:
    def setup_method(self):
        self.transformer = KeywordFeatures()

    def test_output_shape(self):
        texts = ["facture de prestation"]
        result = self.transformer.fit_transform(texts)
        n_groups = len(KeywordFeatures.KEYWORD_GROUPS)
        n_binary = len(KeywordFeatures.BINARY_INDICATORS)
        n_combos = 5
        assert result.shape == (1, n_groups + n_binary + n_combos)

    def test_facture_keywords(self):
        result = self.transformer.transform(["FACTURE n°2024-001 echeance 30 jours"]).toarray()
        assert result[0, 0] > 0  # kw_facture group

    def test_paie_keywords(self):
        result = self.transformer.transform(
            ["Bulletin de salaire - Salaire brut - cotisation - Net a payer"]
        ).toarray()
        assert result[0, 1] > 0  # kw_paie group

    def test_contrat_keywords(self):
        result = self.transformer.transform(
            ["CONTRAT entre les parties - Article 1 - il est convenu"]
        ).toarray()
        assert result[0, 2] > 0  # kw_contrat group

    def test_rd_keywords(self):
        result = self.transformer.transform(
            ["Recherche et developpement - indicateur technique"]
        ).toarray()
        assert result[0, 3] > 0  # kw_cr_rd group

    def test_no_keywords(self):
        result = self.transformer.transform(["lorem ipsum dolor sit amet"]).toarray()
        for i in range(len(KeywordFeatures.KEYWORD_GROUPS)):
            assert result[0, i] == 0


class TestTextNormalizer:
    def test_lowercase(self):
        norm = TextNormalizer()
        result = norm.fit_transform(["HELLO World"])
        assert result[0] == "hello world"

    def test_spaced_collapsed(self):
        norm = TextNormalizer()
        result = norm.fit_transform(["F A C T U R E"])
        assert "facture" in result[0]


class TestBuildFeatureUnion:
    def test_builds_pipeline(self):
        fu = build_feature_union()
        assert len(fu.transformer_list) == 3

    def test_fit_transform(self):
        fu = build_feature_union()
        texts = [
            "Facture n°123 total HT 1500,00 € TVA 20%",
            "Bulletin de salaire cotisations net a payer",
            "Contrat entre les parties article 1",
        ]
        X = fu.fit_transform(texts)
        assert X.shape[0] == 3
        assert X.shape[1] > 20  # tfidf + simple(5) + keywords features
