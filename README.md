# Plateforme intelligente de collecte documentaire

Projet industriel de machine learning ESISA × Leyton CognitX, 2026-2027 : **sujet n°1**. Encadrement : Youssef Mekouar, ESISA.

**Équipe** : à compléter (nom, prénom, classe de chaque membre) · **Groupe** : gXX · **Dépôt** : à renommer `leyton-ml-gXX-sujet1`

## Le besoin

Aujourd'hui, les pièces d'un dossier client (factures, fiches de paie, contrats, comptes-rendus R&D) sont collectées par e-mail, avec des relances manuelles. Personne ne voit en temps réel ce qui manque ou est incorrect, et le travail des consultants est ralenti.

La solution : une **dropzone unique** où le client dépose ses pièces ; une **IA qui extrait, classe et valide** chaque document, puis liste ce qui manque ; un **client informé** par un statut en temps réel et des relances automatiques.

```
Dépôt → Lecture → Analyse → Validation → Statut du dossier
```

## La brique ML

Un modèle de **classification du type de document**, entraîné et évalué par l'équipe sur le texte lu par OCR, avec une confiance calibrée qui décide de l'envoi d'un document en revue par le consultant. L'IA propose, l'expert décide, et chaque décision est expliquée. Détails : [docs/ml-methodology.md](docs/ml-methodology.md).

## Livrables attendus (cahier des charges, p.4)

- [ ] Prototype : dropzone, pipeline de traitement, tableau de statut du dossier
- [ ] Logique de validation documentée
- [ ] Démo sur un jeu de documents fictifs
- [ ] Brique ML intégrée, évaluée et expliquée

## Données

**Documents fictifs ou anonymisés uniquement.** Aucun document réel non anonymisé n'entre dans le dépôt. Règles dans [data/README.md](data/README.md).

## Documentation

| Document | Contenu |
|----------|---------|
| [docs/requirements-analysis.md](docs/requirements-analysis.md) | Exigences officielles du sujet 1, couverture, corrections, questions ouvertes |
| [docs/architecture.md](docs/architecture.md) | Architecture, modules, états, décisions techniques |
| [docs/dataset-strategy.md](docs/dataset-strategy.md) | Classes, volume, annotation, génération, découpage sans fuite, évaluation |
| [docs/dataset-automation.md](docs/dataset-automation.md) | Étude : datasets publics, génération automatisée, validation humaine minimale |
| [docs/ml-methodology.md](docs/ml-methodology.md) | Données, algorithmes, évaluation, limites |
| [docs/roadmap.md](docs/roadmap.md) | Planning aligné sur les 7 étapes officielles |
| [docs/declaration-ia.md](docs/declaration-ia.md) | Registre de l'usage d'IA générative |

## Structure

```
docs/       cadrage, architecture, méthodologie
data/       documents fictifs ou anonymisés, annotations
src/
  backend/  API FastAPI, modules, pipeline
  frontend/ application React (dropzone, statut, revue)
  ml/       package docintel_ml : données, entraînement, évaluation, inférence
reports/    rapports d'évaluation, fiche de données, fiche modèle
```

## Prérequis

Python 3.11+, Node.js 20+, [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) avec les langues `fra` et `eng`. Aucun service externe : base SQLite et fichiers sur disque.

## Démarrage

Pas encore implémenté. Une fois la phase A terminée :

```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate    # Windows : .venv\Scripts\activate
pip install -e "src/ml[dev]" -e "src/backend[dev]"
uvicorn app.main:app --reload --app-dir src/backend

cd src/frontend && npm install && npm run dev
```

## Travail en équipe

Une branche par fonctionnalité, relecture croisée, commits sous le nom de chacun (l'historique est évalué). Chacun doit pouvoir expliquer tout le code. Usage d'IA générative déclaré dans [docs/declaration-ia.md](docs/declaration-ia.md).
