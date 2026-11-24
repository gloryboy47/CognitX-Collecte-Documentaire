# Analyse des exigences : sujet n°1

Source : `docs/Projets_Industriels_ML_ESISA_Leyton-VF.pdf` (13 pages, lu en entier). Le document propose 4 sujets ; seul le **sujet n°1, « Plateforme intelligente de collecte documentaire »** (page 4) est traité ici. Les sujets 2, 3 et 4 ne sont pas utilisés. Les pages 1-3 et 10-13 contiennent des règles communes aux quatre sujets : elles sont citées explicitement comme telles.

## 1. Exigences officielles du sujet 1

### 1.1 Contexte et problème (p.4)
- Les pièces d'un dossier client (factures, fiches de paie, contrats, comptes-rendus R&D) sont collectées **par e-mail avec relances manuelles**.
- Aucune visibilité en temps réel sur ce qui manque ou est incorrect.
- Le travail des consultants est ralenti.
- Le métier (p.2) : dossier CIR/CII de Leyton (client innovant → **collecte des pièces justificatives** → rapport technique → déclaration → contrôle fiscal). Le sujet 1 couvre l'étape de collecte.

### 1.2 Ce que la solution doit faire (p.4)
1. **Une dropzone unique** : le client y dépose toutes ses pièces.
2. **Une IA qui vérifie** : elle **extrait, classe et valide** chaque document, puis **liste ce qui manque**.
3. **Un client informé** : **statut en temps réel** et **relances automatiques**, sans le consultant.
4. Parcours : **Dépôt → Lecture → Analyse → Validation → Statut du dossier**.

### 1.3 Brique ML obligatoire (p.3-4)
- Question posée : *comment la solution apprend-elle à reconnaître, vérifier et fiabiliser les documents déposés ?*
- « À vous d'identifier où l'apprentissage automatique apporte une vraie valeur, puis de l'intégrer au cœur de la solution et de prouver qu'il fonctionne. »
- Qualités attendues : **utile** (pas décorative), **intégrée** (au cœur, dans le parcours), **évaluée** (entraînée sur des données, métriques adaptées), **expliquée** (choix justifiés, apport montré).
- Le cahier des charges n'impose ni le type de tâche, ni l'algorithme.

### 1.4 Livrables (p.4)
1. Un prototype : dropzone, pipeline de traitement, tableau de statut du dossier.
2. La logique de validation documentée.
3. Une démo sur un jeu de documents fictifs.
4. La brique ML intégrée, évaluée et expliquée.

### 1.5 Points de vigilance (p.4)
- **Confidentialité : documents fictifs ou anonymisés uniquement.**
- **Une erreur de validation coûte cher au client : l'IA doit être transparente.**
- **Commencer par un parcours simple qui marche de bout en bout.**

### 1.6 Règles communes aux quatre sujets
| Règle | Page |
|---|---|
| Groupe de 3 à 5 étudiants, un groupe = un sujet = un dépôt Git | 1, 10 |
| Période : 16 novembre 2026 au 25 janvier 2027 ; dates des étapes communiquées en séance | 1, 11 |
| Dépôt `leyton-ml-gXX-sujetN` avec `README.md` (équipe, sujet, démo), `docs/`, `data/` (données fictives), `src/`, `reports/` ; accessible à l'encadrant ; créé dès le début | 10 |
| Chacun commite sous son nom, régulièrement : l'historique compte | 10 |
| Démarche : comprendre, découper, architecturer, coder ; « une solution simple qui marche de bout en bout vaut mieux qu'une brique parfaite isolée » | 10 |
| 7 étapes dont revue de mi-parcours devant l'encadrement ESISA avec intervention de Leyton | 11 |
| Évalué sur : le dépôt et la qualité du code, les revues de mi-parcours, les interventions entreprise, la soutenance finale (très importante) ; contribution de chaque membre | 12 |
| **Humain dans la boucle : l'IA propose, l'expert décide** | 12 |
| Données fictives ou anonymisées uniquement | 12 |
| IA générative autorisée comme outil, **à déclarer** | 12 |
| Chacun doit pouvoir expliquer tout le code du groupe | 12 |
| Compétition : les meilleures solutions sont distinguées | 12 |

## 2. Correspondance exigences ↔ architecture

| Exigence | Où elle est traitée | Statut |
|---|---|---|
| Dropzone unique | Module `documents` + écran Dropzone ([architecture §4, §7](architecture.md)) | Couvert |
| Lecture | Module `ocr` | Couvert |
| Classer | Module `classification` = brique ML | Couvert |
| Extraire | Module `extraction` (règles) | Couvert |
| Valider + logique documentée | Module `validation`, règles par type ; document final prévu en phase D | Couvert, document à rédiger |
| Lister ce qui manque | Module `cases` : pièces attendues vs documents confirmés | Couvert ; **liste des pièces attendues à obtenir** (Q1) |
| Statut du dossier en temps réel | `cases` + tableau de statut, polling | Couvert |
| Relances automatiques sans le consultant | Module `notifications` + planificateur | Couvert ; canal à préciser (Q4) |
| Brique ML utile, intégrée, évaluée, expliquée | [ml-methodology.md](ml-methodology.md), artefact chargé par le backend | Couvert sur le papier ; **aucun résultat à ce jour** |
| Transparence de l'IA | Explication de la prédiction, motif de chaque règle, version du modèle, historique de décisions | Couvert |
| L'IA propose, l'expert décide | États `PROPOSE_*` puis décision du consultant | Couvert ; niveau d'autonomie à préciser (Q2) |
| Documents fictifs ou anonymisés | Politique `data/README.md`, champ `provenance` | Couvert |
| Parcours simple de bout en bout d'abord | Roadmap : phase B = bout en bout avec baseline avant la comparaison d'algorithmes | Couvert |
| Structure de dépôt | `docs/`, `data/`, `src/`, `reports/`, `README.md` | Couvert ; **nom du dépôt à appliquer** |
| IA générative à déclarer | [declaration-ia.md](declaration-ia.md) | Couvert |
| Historique Git individuel | Règles dans README et roadmap ; **dépôt Git non encore initialisé** | À faire |
| Démo sur jeu fictif | Phase D ; le corpus est à créer | À faire |

## 3. Écarts relevés dans la version 1 et corrections

### 3.1 Hypothèses incorrectes

| Version 1 | Constat | Correction |
|---|---|---|
| « Aucun jeu fourni, l'équipe collecte » (H5), avec consentements, anonymisation de documents **réels**, et mention de la loi 09-08 / RGPD | Le sujet impose des documents **fictifs ou anonymisés** : pas de collecte de données réelles à gérer. Le volet juridique que j'avais ajouté n'est pas dans le cahier des charges. | Politique de données réécrite autour de la règle officielle ; mention juridique supprimée. |
| Documents synthétiques « uniquement dans le train, jamais dans validation ni test » | Incompatible avec le sujet : **toute** la démo et probablement tout le corpus sont fictifs. | Règle remplacée par un découpage groupé par gabarit, un jeu de test « stress » et un avertissement explicite sur la portée des scores. |
| « Volume académique de quelques milliers de documents » (H4) | Aucune donnée dans le sujet ; l'équipe fait 3 à 5 personnes sur ~9 semaines. | Supprimée. Les effectifs sont à mesurer, pas supposés. |
| Livrables « rapport académique, soutenance, démonstration » (H6) | Le sujet précise : prototype, logique de validation documentée, démo sur documents fictifs, brique ML ; soutenance finale. | Livrables réalignés sur la page 4 (roadmap, README). |
| Dépôt `frontend/ backend/ ml/ docs/` | Le cahier des charges décrit `README.md, docs/, data/, src/, reports/` (p.10). | Restructuration (voir 3.3). |
| Planning en phases génériques sans dates | Période officielle 16 nov 2026 - 25 janv 2027, 7 étapes dont la revue de mi-parcours. | Roadmap réécrite sur ce calendrier. |

### 3.2 Sur-conception retirée (complexité non justifiée)

Pour 3 à 5 étudiants et environ 9 semaines, avec « chacun doit pouvoir expliquer tout le code » :

| Retiré | Raison | Remplacé par |
|---|---|---|
| Celery + Redis | Deux composants à installer et déboguer ; traitement de quelques secondes par document | `BackgroundTasks` FastAPI, état en base |
| MinIO (S3) | Infrastructure sans besoin | Disque local derrière une petite interface |
| PostgreSQL + Alembic | Installation par membre, migrations inutiles tant que le schéma bouge | SQLite, `DATABASE_URL` portable |
| Docker Compose (Postgres, Redis, MinIO, Mailpit) | Plus rien à orchestrer | Supprimé |
| MLflow | Outil de plus à expliquer | Rapports JSON/Markdown dans `reports/` |
| Modules `audit` et `dashboard` | Doublons : l'historique de décisions est déjà dans `documents` ; le tableau de statut est dans `cases` | Fusionnés |
| Module `compliance` | Nom non aligné sur le sujet | Renommé `validation` (« logique de validation documentée ») |
| Dossier `workers/` | Plus de worker séparé | `pipeline/` qui reprend le parcours officiel |
| python-magic, boto3, psycopg, alembic, celery | Dépendances mortes | Retirées des `pyproject.toml` |

### 3.3 Restructuration

`ml/` → `src/ml/`, `backend/` → `src/backend/`, `frontend/` → `src/frontend/`, `ml/data/` → `data/`, `ml/reports/` → `reports/`, `ml/models/` → `src/ml/artifacts/`. Le contenu du `.gitignore` est adapté : les données fictives sont versionnables, `data/private/` est ignoré. Aucun fichier de code n'existait : rien n'a été perdu. Les Skills de `.claude/skills/` sont intacts.

### 3.4 Ajouts

- Machine à états distinguant **proposition de l'IA** et **décision du consultant** (exigence p.12, absente en v1 qui prévoyait une validation automatique).
- Section Transparence (exigence p.4).
- `docs/declaration-ia.md` (exigence p.12).
- Vocabulaire métier CIR/CII repris du sujet (p.2) dans cette analyse.

### 3.5 Éléments que j'avais ajoutés et qui ne sont **pas** demandés par le sujet

Conservés mais à ne pas présenter comme exigés :
- la classe `autre` (utile en pratique, à valider avec Leyton) ;
- la calibration des probabilités et la courbe couverture/précision (choix d'ingénierie pour répondre à « fiabiliser » et « une erreur coûte cher ») ;
- deux rôles client / consultant : le sujet parle de « client » et de « consultants » mais ne définit pas de comptes ;
- l'extraction par règles : « extrait » est demandé, la méthode ne l'est pas.

## 4. Décisions techniques et justifications

| Décision | Justification |
|---|---|
| ML = classification du type de document sur texte OCR + confiance calibrée | Porte la valeur du parcours (savoir quelle pièce est fournie), faisable avec un petit corpus fictif, expliquable. Le sujet laisse le choix de la tâche. Voir Q5 pour d'autres pistes. |
| Validation par règles explicites, ML seulement où il apporte | Transparence exigée (p.4) ; une règle lisible vaut mieux qu'un modèle opaque pour une vérification de conformité. |
| Modèles linéaires d'abord | Baseline forte, termes décisifs lisibles = explication gratuite ; plus rapide à justifier en soutenance. |
| Seuil de confiance → revue humaine | L'IA propose, l'expert décide ; une erreur coûte cher. |
| Découpage par gabarit + test « stress » | Un corpus fictif fait gonfler les scores ; on mesure la généralisation à d'autres gabarits et on dit les limites. |
| Architecture minimale (monolithe, SQLite, disque) | Calendrier et taille d'équipe ; chaque membre doit tout expliquer. Le pipeline reste isolé, donc évolutif. |
| React + Vite conservé | Dropzone et statut en continu se prêtent bien à une SPA ; risque de temps reconnu (architecture §11) avec un repli possible à la mi-parcours. |
| Aucun modèle externe pour décider de la classe | Le sujet demande une brique ML évaluée et expliquée ; l'IA générative reste un outil de développement déclaré. |

## 5. Questions restant à clarifier

À poser à l'encadrant ou lors des interventions de Leyton.

1. **Pièces attendues** : quelle est la liste exacte des pièces d'un dossier CIR/CII, et varie-t-elle selon le client ou le dispositif (CIR vs CII) ? Quelles règles de conformité Leyton applique-t-il à chaque pièce (période couverte, signature, montants, mentions) ? Sans cela, le module `validation` reste générique.
2. **Autonomie de l'IA** : le consultant confirme-t-il chaque document, ou seulement les cas incertains ? Un document à haute confiance peut-il être marqué « conforme » au client sans intervention humaine ? (« L'IA propose, l'expert décide » est posé, mais pas le niveau de détail.)
3. **Taxonomie** : les quatre types cités sont-ils exhaustifs ? Faut-il une classe `autre` ? D'autres pièces du dossier (relevés, déclarations, justificatifs de sous-traitance) sont-elles attendues ?
4. **Relances** : par quel canal (e-mail réel, simulation) et à quelle fréquence ? La démo doit-elle envoyer de vrais e-mails ?
5. **Choix de la brique ML** : la classification convient-elle pour « reconnaître, vérifier et fiabiliser », ou Leyton attend-il aussi un ML sur la vérification (détection d'anomalies, extraction de champs entraînée, qualité de lecture) ?
6. **Données** : Leyton peut-il fournir des exemples anonymisés ou des gabarits de pièces, pour que le corpus fictif soit réaliste ? Quels formats (PDF natifs, scans, photos) ?
7. **Compétition** : quels critères de comparaison entre groupes (métriques ML, démo, code) ?
8. **Dates** : date de la revue de mi-parcours et du rendu final ; modalités de la soutenance.
9. **Langues** : documents uniquement en français, ou aussi en anglais ?
10. **Frontend** : une interface web complète est-elle attendue, ou un tableau de statut simple suffit-il ? (Impacte l'effort et le choix React.)

## 6. Éléments hors périmètre

Rapport technique, veille réglementaire, génération vidéo (sujets 2, 3, 4) : non traités. Déploiement en production, authentification d'entreprise, intégration à un SI de Leyton : non mentionnés dans le sujet.
