# Architecture technique : sujet n°1, Plateforme intelligente de collecte documentaire

> Version 2, alignée sur le cahier des charges officiel (`Projets_Industriels_ML_ESISA_Leyton-VF.pdf`, page 4 pour le sujet, pages 3 et 10-12 pour les règles communes). Le raisonnement et les écarts avec la version 1 sont dans [requirements-analysis.md](requirements-analysis.md).

## 1. Ce que l'architecture doit servir

Le sujet demande une **dropzone unique** où le client dépose ses pièces, une **IA qui extrait, classe et valide** chaque document puis **liste ce qui manque**, et un **client informé** (statut en temps réel, relances automatiques sans le consultant). Parcours officiel :

```
Dépôt → Lecture → Analyse → Validation → Statut du dossier
```

Contraintes qui pèsent sur les choix :

| Contrainte (source) | Conséquence |
|---|---|
| ~9 semaines restantes, 3 à 5 étudiants (p.1, p.10) | Architecture minimale : un backend, un frontend, un package ML. Pas d'infrastructure à opérer. |
| « Commencer par un parcours simple qui marche de bout en bout » ; règle d'or p.10 | On livre d'abord un parcours complet avec une baseline, puis on améliore. |
| Documents fictifs ou anonymisés uniquement (p.4, p.12) | Les données sont versionnables dans `data/`, mais l'équipe doit les produire. Les limites en découlent (§6). |
| « L'IA doit être transparente » (p.4) ; « l'IA propose, l'expert décide » (p.12) | Chaque décision est expliquée et le consultant a le dernier mot. |
| ML « utile, intégrée, évaluée, expliquée » (p.3) | La brique ML est dans le parcours, avec un protocole d'évaluation et des choix justifiables. |
| Chacun doit pouvoir expliquer tout le code (p.12) | Peu de technologies, pas de framework superflu. |

## 2. Vue d'ensemble

Un **monolithe modulaire** : une API FastAPI qui exécute le pipeline en tâche de fond, une SPA React, et un package ML autonome importé par le backend.

```
┌───────────────────┐   REST/JSON    ┌───────────────────────────────────────┐
│ Frontend React    │ ─────────────► │ Backend FastAPI                       │
│ • Dropzone client │ ◄───────────── │  auth · cases · documents             │
│ • Tableau statut  │   (polling)    │  notifications                        │
│ • Revue consultant│                │  ┌─────────── pipeline ────────────┐  │
└───────────────────┘                │  │ ocr → classification →          │  │
                                     │  │ extraction → validation → statut│  │
         SQLite (données)  ◄─────────┤  └───────────┬─────────────────────┘  │
         Disque (fichiers) ◄─────────┤              │ import                 │
                                     └──────────────┼────────────────────────┘
                                                    ▼
                                        ┌───────────────────────┐
                                        │ docintel_ml           │ entraîné hors ligne
                                        │ (inference seulement) │ artefact versionné
                                        └───────────────────────┘
```

Aucune file de messages, aucun conteneur, aucun stockage objet : le prototype démarre avec `uvicorn` et `npm run dev`. L'exécution en tâche de fond (`BackgroundTasks` de FastAPI) suffit pour un traitement de quelques secondes par document ; l'état de chaque étape est écrit en base, donc le client voit l'avancement par polling. Si la charge l'exigeait un jour, le pipeline est déjà isolé dans `app/pipeline/` et pourrait passer sur une vraie file.

## 3. Structure du dépôt

Elle suit le dépôt type du cahier des charges (p.10 : `README.md`, `docs/`, `data/`, `src/`, `reports/`). Le dossier devra être nommé `leyton-ml-gXX-sujet1` à la création du dépôt Git (XX = numéro de groupe).

```
leyton-ml-gXX-sujet1/
├── README.md                    # équipe, sujet, démo
├── docs/                        # cadrage, architecture, validation, méthodologie ML, déclaration IA
├── data/                        # documents FICTIFS ou ANONYMISÉS uniquement
│   ├── raw/  interim/  processed/  annotations/
├── src/
│   ├── backend/app/
│   │   ├── core/  db/  api/v1/
│   │   ├── modules/{auth,cases,documents,ocr,classification,extraction,validation,notifications}
│   │   └── pipeline/            # orchestration Dépôt → … → Statut
│   ├── frontend/src/{app,pages,features,shared}
│   └── ml/                      # package docintel_ml + configs, notebooks, artifacts
│       └── src/docintel_ml/{data,features,models,training,evaluation,inference}
└── reports/                     # rapports d'évaluation, fiche de données, fiche modèle
```

**Règle de dépendance** : `frontend` → HTTP → `backend` → import → `docintel_ml.inference`. Le backend n'importe jamais `training` ni `evaluation`. Le package ML ignore la base et FastAPI.

## 4. Modules backend

Correspondance directe avec le parcours officiel.

| Étape officielle | Module | Responsabilité |
|---|---|---|
| (accès) | `auth` | Deux rôles : client et consultant. Un client ne voit que ses dossiers. |
| Dépôt | `documents` | Réception, contrôle du fichier (extension, signature, taille), stockage, états, historique des décisions. |
| Lecture | `ocr` | Texte d'un PDF (couche texte si présente, sinon Tesseract) ou d'une image. Renvoie texte et confiance de lecture. |
| Analyse | `classification` | **Brique ML** : type du document, probabilités, explication (termes qui ont pesé), version du modèle. |
| Analyse | `extraction` | Champs clés (dates, montants, identifiants, parties) par règles et expressions régulières. |
| Validation | `validation` | **Logique de validation documentée** : règles par type, pièces manquantes, motifs explicites. Propose un statut. |
| Statut du dossier | `cases` | Pièces attendues d'un dossier, statut du dossier dérivé des états des documents, données du tableau de statut. |
| Relances | `notifications` | Relances automatiques des pièces manquantes ou incorrectes, notification des changements de statut. |

### États

Le principe officiel est « l'IA propose, l'expert décide ». Les états distinguent donc la **proposition de l'IA** de la **décision du consultant**.

```
Document :  DEPOSE → EN_LECTURE → EN_ANALYSE ─┬─ PROPOSE_CONFORME ─┐
                                               ├─ PROPOSE_REJET     ├─► CONFIRME / REJETE  (décision consultant)
                                               └─ A_REVOIR ─────────┘
Dossier  :  INCOMPLET · EN_COURS · A_VALIDER · VALIDE
```

- `A_REVOIR` : confiance sous le seuil, texte illisible ou règles contradictoires.
- Le statut dossier est **calculé** à partir des documents et de la liste des pièces attendues, jamais saisi à la main.
- Le client voit sa propre vue : pièce reçue, en cours d'analyse, à corriger (avec le motif), confirmée.
- Le niveau d'autonomie (le consultant confirme-t-il tout, ou seulement les cas incertains ?) est une **question ouverte** pour Leyton (voir requirements-analysis, §5). Le modèle d'états supporte les deux cas.

### Transparence

« Une erreur de validation coûte cher au client » (p.4). Pour chaque document, l'interface et la base conservent : le texte lu, la classe proposée avec ses probabilités, les termes qui l'expliquent, les champs extraits et leur source, la règle de validation appliquée et son motif, la version du modèle, et qui a décidé quoi. Un rejet n'est jamais « refusé » sans motif.

## 5. Données applicatives

SQLite via SQLAlchemy pour le prototype : zéro installation, un fichier à copier pour la démo. Les modèles restent portables vers PostgreSQL en changeant `DATABASE_URL`. Le schéma est créé par SQLAlchemy au démarrage ; pas de migrations Alembic tant que le schéma bouge chaque semaine.

```
users ──< cases ──< case_requirements >── document_types
              │
              └──< documents (fichier, hash, état)
                       ├──< ocr_results        (texte, confiance)
                       ├──< predictions        (type, probabilités, model_version)
                       ├──< extracted_fields   (clé, valeur, source)
                       ├──< validation_checks  (règle, résultat, motif)
                       └──< decisions          (acteur : ia | consultant, décision, date)
notifications (destinataire, type, lu)
```

Une prédiction est une **ligne** (avec la version du modèle), pas une colonne : on peut comparer deux modèles sur les mêmes documents, et les corrections du consultant (`decisions`) servent d'étiquettes pour améliorer le modèle.

## 6. Brique ML

Détails et protocole : [ml-methodology.md](ml-methodology.md).

**Où est la valeur ?** Le sujet demande d'identifier où l'apprentissage apporte de la valeur pour « reconnaître, vérifier et fiabiliser ». Notre choix : **classification du type de document à partir du texte OCR**, avec une **confiance calibrée** qui décide de l'envoi en revue humaine. C'est le point qui rend les étapes suivantes possibles (savoir quelle pièce attendue est couverte, quelles règles appliquer) et celui où les règles seules échouent (formats variés, textes bruités). Les règles métier de validation restent des règles : elles sont explicites et auditables.

- Le modèle est développé, entraîné et évalué par l'équipe sur des données fictives ou anonymisées. Aucun LLM ni API ne décide de la classe. L'IA générative reste autorisée comme outil de développement, à déclarer ([declaration-ia.md](declaration-ia.md)).
- Progression : règle triviale → TF-IDF + régression logistique (baseline, interprétable) → comparaison d'algorithmes → plus lourd seulement si justifié.
- Les modèles linéaires sont retenus d'abord aussi pour la transparence : les termes qui pèsent dans la décision se lisent directement.
- **Limite à annoncer** : puisque les données sont fictives, les scores mesurent la capacité à reconnaître *nos* documents fictifs, pas la performance sur des dossiers réels. Les découpages par gabarit et le jeu de test « stress » (§ ml-methodology) limitent l'optimisme, ils ne le suppriment pas.

## 7. Frontend

React + TypeScript + Vite, organisé par fonctionnalité. Trois écrans suffisent au cahier des charges :

1. **Dropzone** client : glisser-déposer, retour immédiat par fichier.
2. **Tableau de statut du dossier** (client et consultant) : pièces attendues, état de chacune, ce qui manque, motifs.
3. **Revue consultant** : document, classe proposée et explication, champs extraits, boutons confirmer / corriger.

La direction visuelle sera définie avec le Skill `frontend-design` au démarrage de l'interface, à partir du contenu réel de ces écrans.

## 8. Qualité et tests

- Backend : tests unitaires des règles de validation et des états ; un test bout en bout dépôt → statut.
- ML : tests du découpage (pas de fuite), des métriques et du chargement de l'artefact. La qualité du modèle se juge par le rapport d'évaluation.
- Frontend : tests limités aux composants critiques (dropzone, tableau de statut).
- Git : une branche par fonctionnalité, commits sous le nom de chacun, relecture croisée. L'historique est évalué (p.10).

## 9. Sécurité

Proportionnée au prototype : mots de passe hachés, JWT, autorisation par dossier côté serveur, type de fichier vérifié par signature et taille limitée, nom de fichier jamais utilisé comme chemin, secrets en variables d'environnement. Le cahier des charges impose surtout de **ne jamais utiliser de document réel non anonymisé** (p.4) : c'est la règle de confidentialité du projet.

## 10. Décisions et alternatives écartées

| Décision | Choix | Écarté, pourquoi |
|---|---|---|
| Découpage | Monolithe modulaire | Microservices : aucun bénéfice à 3-5 personnes et 9 semaines. |
| Exécution du pipeline | `BackgroundTasks` FastAPI + état en base | Celery/Redis : composants à installer et déboguer pour un gain nul à ce volume. |
| Base | SQLite (portable vers PostgreSQL) | PostgreSQL dès le départ : installation pour chaque membre sans bénéfice immédiat. |
| Fichiers | Disque local derrière une petite interface | MinIO/S3 : infrastructure superflue. |
| Relances | Planificateur APScheduler dans le backend ; e-mail si SMTP configuré, sinon journal | Service de notifications dédié. |
| OCR | PyMuPDF + Tesseract | OCR cloud : coût et confidentialité. |
| Entrée du modèle | Texte OCR | Image brute : plus de données et de calcul ; piste d'extension. |
| Extraction | Règles et regex | NER entraîné : prématuré sans annotation au niveau des champs ; extension possible. |
| Suivi d'expériences | Rapports JSON/Markdown dans `reports/` | MLflow : outil de plus à maîtriser et expliquer. Réintégrable si le besoin apparaît. |
| Frontend | React + Vite | Plus lourd qu'une application à pages simples ; retenu pour la dropzone et le statut en continu. Voir le risque en §11. |

## 11. Risques

| Risque | Mitigation |
|---|---|
| Calendrier court : fin des étapes à confirmer en séance | Parcours minimal de bout en bout en premier ; jalons dans la [roadmap](roadmap.md). |
| Pas de jeu de données fourni : il faut produire des documents fictifs réalistes | Lancer la création du corpus dès maintenant ; variabilité de gabarits ; honnêteté sur les limites. |
| Interface React qui consomme le temps de l'équipe | Trois écrans seulement ; si le retard s'installe, repli sur une interface plus simple. Décision à la revue de mi-parcours. |
| Corpus fictif trop propre, résultats trop beaux | Gabarits multiples, bruit d'OCR et scans dégradés réalistes, jeu de test « stress » créé par un autre membre. |
| OCR dégradé sur scans | Mesurer la qualité de lecture ; état `A_REVOIR` plutôt qu'une classe hasardeuse. |
