# Roadmap

Calendrier officiel : projet du **16 novembre 2026 au 25 janvier 2027** (p.1). Les dates précises de chaque étape « seront communiquées en séance » (p.11) : les semaines ci-dessous sont indicatives et à caler dès que l'on connaît la date de la revue de mi-parcours et celle du rendu.

Principe directeur (p.10) : *« une solution simple qui marche de bout en bout vaut mieux qu'une brique parfaite isolée »*. On construit donc un parcours complet minimal d'abord, puis on l'améliore.

## Correspondance avec les 7 étapes officielles

| Étape officielle (p.11) | Ce que cela donne ici | Statut |
|---|---|---|
| 1. Lancement | Groupe, sujet 1, dépôt Git `leyton-ml-gXX-sujet1`, inscription Google Sheet | À faire / à confirmer par l'équipe |
| 2. Comprendre et découper | Vocabulaire métier, briques, corpus fictif | En cours : voir `requirements-analysis.md` |
| 3. Architecture | `docs/architecture.md` | Fait (v2), à valider avec l'encadrant |
| 4. Développement | Phases A à C ci-dessous | À venir |
| 5. Revue de mi-parcours | Parcours de bout en bout démontrable avec la baseline | Date à connaître |
| 6. Amélioration et finalisation | Phase D | |
| 7. Rendu et soutenance | Dépôt final, démo, défense des choix | Date à connaître |

## Phase 0 : cadrage (semaine du 23 nov.)

- [x] Architecture alignée sur le cahier des charges
- [ ] Créer le dépôt Git au bon nom, donner l'accès à l'encadrant, chacun commite sous son nom
- [ ] Inscrire le groupe au Google Sheet
- [ ] Répartir les rôles (backend, frontend, ML/données), relecture croisée
- [ ] Poser les questions de [requirements-analysis.md §5](requirements-analysis.md) à l'encadrant ou à Leyton
- [ ] Figer la liste des pièces attendues et des règles de validation de chaque type

## Phase A : corpus et parcours minimal (semaines 1-2)

**Données (chemin critique, démarre tout de suite)**
- [ ] Guide d'annotation et plan de création des documents fictifs (gabarits multiples, bruit réaliste)
- [ ] Premier lot de documents par classe, manifeste avec provenance
- [ ] Découpage groupé par gabarit

**Application**
- [ ] Backend : base, auth à deux rôles, dossier et pièces attendues, dépôt de fichier
- [ ] Frontend : connexion, dropzone, tableau de statut (squelette)
- [ ] Module `ocr` sur quelques documents

**Sortie** : un client dépose un fichier, le texte est lu et affiché.

## Phase B : de bout en bout avec la baseline (semaines 3-4)

- [ ] Baseline ML (palier 1), premières métriques, artefact chargé par le backend
- [ ] Pipeline complet : lecture → classification → extraction → validation → statut du dossier
- [ ] Règles de validation par type, documentées
- [ ] Tableau de statut qui reflète l'état réel, polling
- [ ] Relances automatiques (journal en démo)

**Sortie : version présentable à la revue de mi-parcours.** Un parcours simple qui marche, même avec un modèle modeste, et la méthodologie ML déjà documentée.

## Phase C : brique ML et revue humaine (semaines 5-7)

- [ ] Comparaison d'algorithmes, calibration, choix du seuil de confiance
- [ ] Revue consultant : confirmer / corriger, explication de la prédiction
- [ ] Réintégration des corrections dans le corpus
- [ ] Jeu de test « stress » et évaluation finale du test (une seule fois)
- [ ] Palier 3 uniquement si justifié

## Phase D : finalisation (semaines 8-9)

- [ ] Prise en compte des retours de la mi-parcours
- [ ] Fiche de données, fiche modèle, rapport d'évaluation dans `reports/`
- [ ] Démo scénarisée sur un jeu de documents fictifs
- [ ] README avec équipe, sujet, démo ; guide d'installation
- [ ] Préparation de la soutenance : chacun sait expliquer tout le code

## Livrables officiels (p.4) et où ils sont traités

| Livrable | Phase |
|---|---|
| Prototype : dropzone, pipeline de traitement, tableau de statut du dossier | A, B, C |
| Logique de validation documentée | B (règles), D (document final) |
| Démo sur un jeu de documents fictifs | D |
| Brique ML intégrée, évaluée et expliquée | B (baseline intégrée), C (évaluation), D (rapport) |

## Responsabilités

| Zone | Responsable | Relecteur |
|---|---|---|
| `src/backend` | à désigner | responsable ML (contrat d'inférence) |
| `src/frontend` | à désigner | responsable backend (contrat d'API) |
| `src/ml`, `data/`, `reports/` | à désigner | responsable backend |
| `docs/` | tous | |

## Definition of done

1. Relu par un second membre ; **le relecteur doit pouvoir expliquer le code** (exigence p.12).
2. Tests écrits et passants.
3. Contrat d'API ou d'inférence mis à jour s'il change.
4. Documentation mise à jour.
5. Aucun secret, aucun document réel non anonymisé.
6. Tout usage notable d'IA générative est noté dans [declaration-ia.md](declaration-ia.md).
