# Compte Rendu — Projet CognitX : Plateforme Intelligente de Collecte Documentaire

**Date** : 24 novembre 2026
**Equipe** : Binome ESISA M1 Informatique
**Client** : Leyton — Dossiers CIR/CII
**Statut** : Toutes les briques livrees et fonctionnelles

---

## 1. Vision du Projet

Construire une plateforme web qui **collecte, classifie et valide automatiquement** des documents d'entreprise (factures, fiches de paie, contrats, comptes rendus R&D) pour constituer des dossiers de Credit d'Impot Recherche (CIR/CII).

**Principe directeur** : « L'IA propose, l'expert decide » — le modele ML fournit une classification avec un score de confiance, et un consultant humain valide ou corrige chaque decision.

---

## 2. Architecture Livree

```
Monolithe modulaire
├── Frontend : React 18 + TypeScript + Vite + TanStack Query
├── Backend  : FastAPI + SQLAlchemy + SQLite
├── ML       : docintel-ml (scikit-learn, TF-IDF + RandomForest)
└── Datagen  : Generateur de corpus fictif (Jinja2 + WeasyPrint)
```

**Flux document complet** :

```
DEPOSE → EN_LECTURE (OCR PyMuPDF/Tesseract)
       → EN_ANALYSE (classification ML RandomForest)
       → PROPOSE_CONFORME / PROPOSE_REJET (decision IA automatique)
       → CONFIRME / REJETE (validation humaine par le consultant)
```

**Communication** : Frontend React ←(REST/JSON + polling 5s)→ Backend FastAPI ←(import)→ Package ML

---

## 3. Etat d'Avancement — Tout est FAIT

| Composant | Statut | Technologies |
|-----------|--------|-------------|
| **Documentation** | Fait (binome) | Markdown — architecture, ML methodology, dataset strategy |
| **Generateur de corpus** | Fait | Jinja2, WeasyPrint, PyMuPDF, 24 templates HTML |
| **Backend API** | Fait | FastAPI, SQLAlchemy, SQLite, JWT (bcrypt), BackgroundTasks |
| **Modele ML** | Fait | TF-IDF + Keywords metier + RandomForest (F1 test = 0.987) |
| **Frontend SPA** | Fait | React 18, react-router-dom, TanStack Query, CSS Modules |
| **Integration E2E** | Fait | Pipeline upload → OCR → classification → decision testee |

---

## 4. Brique 1 — Generation de Donnees (`src/datagen/`)

### 4.1 Corpus

| Metrique | Valeur |
|----------|--------|
| Total documents | 240 |
| Templates HTML | 24 (3 variantes × 8 types) |
| Types de documents | 8 (4 classes + 4 hard negatives "autre") |
| Taille sur disque | ~58 Mo (raw + degrades) |

### 4.2 Distribution par classe

| Classe | Train | Val | Test | Total |
|--------|-------|-----|------|-------|
| facture | 10 | 10 | 10 | 30 |
| fiche_de_paie | 10 | 10 | 10 | 30 |
| contrat | 10 | 10 | 10 | 30 |
| compte_rendu_rd | 10 | 10 | 10 | 30 |
| **autre** (devis, CR non-RD, releve, CGV) | 40 | 40 | 40 | **120** |
| **TOTAL** | **80** | **80** | **80** | **240** |

### 4.3 Sous-types "autre" (hard negatives)

| Sous-type | Docs | Confusion ciblee |
|-----------|------|-----------------|
| devis | 30 | Confusable avec facture (montants, lignes de prix) |
| compte_rendu_non_rd | 30 | Confusable avec CR R&D (meme structure) |
| releve_bancaire | 30 | Confusable avec facture (montants, debits/credits) |
| cgv_notice | 30 | Confusable avec contrat (articles, clauses) |

### 4.4 Degradation

| Niveau | Description | % corpus |
|--------|-------------|----------|
| 0 | PDF natif (propre) | 34% |
| 1 | Scan correct (rotation legere, bruit faible) | 40% |
| 2 | Scan difficile (flou, bruit fort, taches) | 26% |

### 4.5 Garanties d'integrite

- **Split par gabarit** : v1 → train, v2 → val, v3 → test (pas de fuite visuelle)
- **Pools d'entites disjoints** : Pool A (train), Pool B (val), Pool C (test)
- **Reproductibilite** : seed=42, graine derivee par document
- **Annotations** : `manifest.csv` (240 lignes), `splits.csv`

---

## 5. Brique 2 — Backend API (`src/backend/`)

### 5.1 Endpoints REST

| Methode | Route | Description | Acces |
|---------|-------|-------------|-------|
| POST | `/api/v1/auth/register` | Inscription (email, mot de passe, nom, role) | Public |
| POST | `/api/v1/auth/login` | Connexion → JWT token | Public |
| POST | `/api/v1/cases` | Creer un dossier | Client |
| GET | `/api/v1/cases` | Lister ses dossiers (ou tous pour consultant) | Authentifie |
| GET | `/api/v1/cases/{id}` | Detail dossier + liste documents | Authentifie |
| POST | `/api/v1/documents/upload/{case_id}` | Deposer un document (PDF, PNG, JPEG, TIFF) | Authentifie |
| GET | `/api/v1/documents/{id}` | Detail document (OCR, predictions, decisions) | Authentifie |
| POST | `/api/v1/documents/{id}/decide` | Confirmer ou rejeter (consultant) | Consultant |

### 5.2 Modele de donnees (10 tables SQLAlchemy)

- **User** : id, email, password_hash, full_name, role (client/consultant)
- **Case** : id, name, description, state (INCOMPLET/EN_COURS/A_VALIDER/VALIDE), owner_id
- **Document** : id, case_id, original_filename, stored_path, file_hash, file_size, state
- **OcrResult** : id, document_id, text, confidence, engine
- **Prediction** : id, document_id, predicted_class, confidence, probabilities, top_features, model_version
- **Decision** : id, document_id, actor (IA/CONSULTANT), decision, comment
- **DocumentType** : types attendus par dossier (facture, fiche_de_paie, etc.)
- **CaseRequirement** : exigences de types de documents par dossier
- **Notification** : alertes pour le consultant

### 5.3 Pipeline de traitement (BackgroundTasks)

```
upload(file) → sauvegarde disque + DB
  └→ run_pipeline(document_id) en arriere-plan :
       1. OCR (PyMuPDF text extraction, fallback Tesseract)
       2. Classification ML (RandomForest predict_proba)
       3. Extraction de champs metier (regex par type de document)
       4. Validation metier (regles de coherence)
       5. Decision IA automatique :
          - confiance >= 80% → PROPOSE_CONFORME
          - confiance < 80%  → A_REVOIR
```

### 5.4 Extraction de champs (`modules/extraction/`)

Regles regex par type de document :
- **Facture** : numero, montant HT/TTC, date, TVA
- **Fiche de paie** : salaire brut/net, periode, employeur
- **Contrat** : type, date debut, duree
- **Compte rendu R&D** : date reunion, projet, participants

### 5.5 Validation metier (`modules/validation/`)

| Regle | Type | Description |
|-------|------|-------------|
| texte_minimum | Commun | Texte OCR > 50 caracteres |
| qualite_ocr | Commun | Ratio alphabetique > 30% |
| montant_present | Facture | Montant HT ou TTC detecte |
| numero_facture | Facture | Numero de facture present |
| mention_tva | Facture | TVA mentionnee |
| net_a_payer | Fiche de paie | Net a payer detecte |
| salaire_brut | Fiche de paie | Salaire brut detecte |
| mention_signature | Contrat | Clause de signature presente |
| parties_identifiees | Contrat | Parties du contrat identifiees |
| mention_rd | CR R&D | Reference R&D detectee |
| date_reunion | CR R&D | Date de reunion presente |

### 5.6 Securite

- Authentification JWT (HS256, expiration 12h)
- Hachage bcrypt des mots de passe
- Verification de role pour les endpoints consultant
- CORS configure (origines autorisees)
- Validation extensions fichiers (PDF, PNG, JPEG, TIFF)
- Limite taille fichier (20 Mo)

---

## 6. Brique 3 — Modele ML (`src/ml/`)

### 6.1 Pipeline de features

```
Texte OCR brut
  │
  ├── TextNormalizer       → Nettoie les lettres espacees ("F A C T U R E" → "facture")
  │
  ├── TF-IDF (word)        → 500 features (unigrammes + bigrammes)
  │
  ├── SimpleFeatures (5)   → longueur, densite chiffres, nb montants, nb lignes, ratio majuscules
  │
  ├── KeywordFeatures
  │   ├── 8 groupes metier → kw_facture, kw_paie, kw_contrat, kw_cr_rd,
  │   │                      kw_devis, kw_releve, kw_cgv, kw_cr_nonrd
  │   ├── 17 indicateurs binaires → has_facture, has_devis, has_releve, has_bulletin,
  │   │                              has_contrat, has_echeance, has_non_contractuel, etc.
  │   └── 5 features combinatoires → facture_not_devis, devis_not_facture,
  │                                   releve_and_debit, facture_echeance_no_devis,
  │                                   releve_no_total
  │
  └── RandomForestClassifier(n_estimators=200, max_depth=15, class_weight="balanced")
```

### 6.2 Resultats

| Metrique | Validation | Test |
|----------|-----------|------|
| **Accuracy** | 1.0000 | 0.9875 |
| **F1 macro** | 1.0000 | 0.9870 |
| **F1 weighted** | 1.0000 | 0.9872 |

### 6.3 Matrice de confusion (Test)

```
                 factur  fiche_  contra  compte   autre
        facture       9       0       0       0       1
  fiche_de_paie       0      10       0       0       0
        contrat       0       0      10       0       0
compte_rendu_rd       0       0       0      10       0
          autre       0       0       0       0      40
```

**1 seule erreur sur 80 documents test** : une facture classee "autre" (sur un gabarit v3 jamais vu a l'entrainement).

### 6.4 Comparaison des algorithmes

| Algorithme | Val F1 | Test F1 | Erreurs test |
|------------|--------|---------|-------------|
| **RandomForest** | **1.000** | **0.987** | **1** |
| LogisticRegression | 0.979 | 0.966 | 3 |
| GradientBoosting | 0.959 | 0.900 | 6 |
| ComplementNB | 0.933 | 0.908 | 5 |

RandomForest choisi pour ses performances superieures et sa robustesse au changement de gabarit.

### 6.5 Problemes resolus

| Probleme | Cause | Solution |
|----------|-------|----------|
| F1 = 0.48 initial | 10K features TF-IDF sur 80 docs = overfitting | Reduction a 500 features |
| Confusion facture/devis | Memes montants et mises en page | Features `facture_not_devis`, `devis_not_facture` |
| Confusion facture/releve | Montants dans les deux | Features `releve_and_debit`, `releve_no_total` |
| "F A C T U R E" non detecte | Templates avec lettres espacees | `TextNormalizer` (regex espacement) |
| Generalisation gabarit-split | Modele apprend le style, pas le contenu | Features invariantes (keywords metier) |

---

## 7. Brique 4 — Frontend React (`src/frontend/`)

### 7.1 Ecrans livres (5 ecrans)

**Ecran 1 — Dropzone client** (`CaseDetailPage` + `UploadZone`)
- Glisser-deposer multi-fichiers avec barre de progression
- Accepte PDF, PNG, JPEG, TIFF (max 20 Mo)
- Toast notification succes/echec par upload
- Export CSV des decisions du dossier

**Ecran 2 — Tableau de statut** (`DashboardPage` + `CaseDetailPage`)
- Liste des dossiers avec badges de statut (Incomplet, En cours, Valide)
- **Recherche** par nom/description + **filtre par etat**
- Creation de dossier (clients uniquement) avec toast de confirmation
- Tableau des documents par dossier : fichier, taille, statut, action
- **Loading skeletons** (animation shimmer) pendant le chargement
- Rafraichissement automatique toutes les 5 secondes (polling)
- **Dashboard metriques** (StatsPanel) : documents traites, confiance moyenne, distribution par classe

**Ecran 3 — Revue consultant** (`ReviewPage`)
- Classe predite + score de confiance
- Barres de probabilites par classe
- Mots-cles influents (explication IA)
- **Champs extraits** (numero facture, montants, dates, etc.)
- **Validation metier** : checks pass/fail avec indicateurs visuels
- Texte OCR extrait (avec confiance OCR)
- Historique des decisions (IA + consultant)
- Boutons Confirmer / Rejeter avec commentaire + toast de confirmation
- Mention "L'IA propose, l'expert decide"

**Ecran 4 — Notifications** (`NotificationsPage`)
- Liste des notifications avec indicateur lu/non lu
- Marquer comme lu individuellement ou tout d'un coup
- Badge compteur dans le header avec polling 10s

**Ecran 5 — Page 404** (`NotFoundPage`)
- Page d'erreur avec lien retour au dashboard

### 7.2 Authentification

- Login / Register avec roles (client / consultant)
- Token JWT stocke en localStorage
- Redirection automatique si non authentifie
- Deconnexion avec nettoyage session
- Header avec nom + role de l'utilisateur

### 7.3 UX / Accessibilite

- **Dark mode** complet avec toggle dans le header (persistence localStorage)
- **Toast notifications** globales (success/error/info) avec animation slide-in
- **Loading skeletons** shimmer pour dashboard (cards) et case detail (table)
- **Barre de progression** upload multi-fichiers
- **Responsive mobile** : header, grille, table avec scroll horizontal, filtres en colonne
- **Focus visible** (`outline` 2px) sur tous les elements interactifs
- **aria-labels** sur les boutons et champs de formulaire
- **sr-only** class pour texte accessible aux lecteurs d'ecran

### 7.4 Stack technique

| Technologie | Version | Usage |
|------------|---------|-------|
| React | 18.3 | UI composants |
| react-router-dom | 6.26 | Routage SPA |
| @tanstack/react-query | 5.51 | Cache, polling, mutations |
| Vite | 5.4 | Build + dev server + proxy |
| TypeScript | 5.5 | Typage strict |
| CSS Modules | — | Styles scopes par composant |

---

## 8. Test End-to-End Realise

Le parcours complet a ete teste avec succes :

```
1. Inscription client (test@example.com)
2. Connexion → Dashboard vide
3. Creation dossier "Dossier CIR 2025"
4. Upload de 3 documents : facture, contrat, fiche de paie
5. Pipeline automatique : OCR → Classification ML
6. Resultat : 3/3 documents PROPOSE_CONFORME (confiance 96.5% - 100%)
7. Deconnexion client
8. Connexion consultant (consul@example.com)
9. Revue du dossier → 3 documents avec boutons "Revoir"
10. Consultation classification IA + texte OCR + probabilites
11. Decision consultant : "Confirmer" → statut passe a CONFIRME
```

**Resultat** : Parcours complet fonctionnel de bout en bout.

---

## 9. Choix Techniques Justifies

| Choix | Justification |
|-------|--------------|
| **Monolithe** (pas microservices) | 2 personnes, 9 semaines — pas de benefice a multiplier les composants |
| **SQLite** (pas PostgreSQL) | Portable, zero config, suffisant pour le volume |
| **BackgroundTasks** (pas Celery) | Volume faible, pas besoin de file d'attente distribuee |
| **TF-IDF + RandomForest** (pas deep learning) | 80 docs d'entrainement, interpretable, F1=0.987 |
| **CSS Modules** (pas Tailwind) | Chacun doit pouvoir expliquer tout le code |
| **Polling 5s** (pas WebSocket) | Plus simple, suffisant pour l'usage |
| **PyMuPDF + Tesseract** (pas OCR cloud) | Gratuit, local, pas de donnees envoyees a l'exterieur |

---

## 10. Conformite avec le Cahier des Charges

| Exigence | Statut | Implementation |
|----------|--------|---------------|
| Dropzone unique de depot | Fait | UploadZone (drag & drop + click) |
| IA qui classifie et valide | Fait | RandomForest + seuil confiance 80% |
| Liste ce qui manque | Fait | Tableau statut avec badges par document |
| Client informe (statut temps reel) | Fait | Polling 5s + badges colores |
| L'IA propose, l'expert decide | Fait | Decision IA automatique + revue consultant |
| Documents fictifs uniquement | Fait | 240 docs generes, pools d'entites fictives |
| Chacun peut expliquer tout le code | Fait | Stack simple, peu de dependances, pas de magie |
| ML utile, integree, evaluee, expliquee | Fait | F1=0.987, top features, rapport d'evaluation |

---

## 11. Arborescence du Projet

```
Collecte-Documents-Intelligente/
├── docs/                              # Documentation (binome)
│   ├── architecture.md
│   ├── dataset-strategy.md
│   ├── ml-methodology.md
│   └── requirements-analysis.md
├── data/
│   ├── raw/{classe}/                  # 240 PDFs generes
│   ├── interim/{classe}/              # PDFs degrades
│   ├── processed/dataset.csv          # Textes OCR extraits
│   └── annotations/                   # manifest.csv, splits.csv
├── reports/
│   ├── compte-rendu-projet.md         # Ce document
│   └── ml-evaluation.md               # Rapport evaluation ML
├── src/
│   ├── datagen/                       # Generateur de corpus
│   │   ├── templates/ (24 HTML)
│   │   ├── generate.py
│   │   ├── entities.py
│   │   └── degrade.py
│   ├── backend/app/                   # API FastAPI
│   │   ├── main.py
│   │   ├── core/ (config, security, deps)
│   │   ├── db/ (base, models)
│   │   ├── api/v1/ (auth, cases, documents, schemas)
│   │   ├── modules/ (ocr, classification, extraction, validation)
│   │   ├── pipeline/ (process)
│   │   └── tests/ (unit + integration)
│   ├── ml/                            # Package docintel-ml
│   │   ├── artifacts/current/ (model.joblib, metadata.json)
│   │   └── src/docintel_ml/
│   │       ├── features/text_features.py
│   │       ├── training/ (train, compare)
│   │       ├── evaluation/evaluate.py
│   │       └── inference/predictor.py
│   │   └── tests/ (test_features, test_evaluation, test_predictor)
│   └── frontend/                      # SPA React
│       ├── index.html
│       ├── vite.config.ts
│       └── src/
│           ├── app/ (App, Layout, CSS)
│           ├── features/ (auth, cases, documents, review, notifications, errors, stats)
│           └── shared/ (api, hooks/useAuth+useTheme, ui/StatusBadge+Toast+Skeleton)
├── .github/workflows/ci.yml           # CI GitHub Actions
└── .venv/                             # Environnement Python
```

---

## 12. Comment Lancer le Projet

### Backend
```bash
cd Collecte-Documents-Intelligente
source .venv/bin/activate
python -m uvicorn app.main:app --app-dir src/backend --port 8000
```

### Frontend
```bash
cd src/frontend
npm install
npm run dev
```

### Entrainer le modele ML (si besoin)
```bash
PYTHONPATH=src/ml/src .venv/bin/python -W ignore src/ml/src/docintel_ml/training/train.py
```

### Acceder a l'application
- Frontend : http://localhost:5173
- API docs : http://localhost:8000/docs

---

## 13. Tests Automatises

### 13.1 Tests ML (`src/ml/tests/`)

| Fichier | Tests | Couverture |
|---------|-------|-----------|
| `test_features.py` | SimpleFeatures, KeywordFeatures, TextNormalizer, build_feature_union | Features d'entree du modele |
| `test_evaluation.py` | Metriques, matrice de confusion, format de sortie | Module d'evaluation |
| `test_predictor.py` | Prediction avec/sans modele, fallback, reload | Module d'inference |

### 13.2 Tests Backend (`src/backend/tests/`)

| Fichier | Tests | Couverture |
|---------|-------|-----------|
| `unit/test_security.py` | Hash/verify password, create/decode JWT | Auth et securite |
| `unit/test_models.py` | Enums (DocumentState, CaseState, Role, DecisionActor) | Modele de donnees |
| `unit/test_pipeline.py` | Logique de decision IA (seuils, cas limites) | Decision automatique |
| `integration/test_api_auth.py` | Register, login, doublons, mauvais mot de passe | API auth complete |
| `integration/test_api_cases.py` | CRUD dossiers, isolation client/consultant, 403 | API cases complete |

### 13.3 CI/CD (`.github/workflows/ci.yml`)

4 jobs paralleles sur chaque push/PR :
1. **Tests ML** : pytest sur docintel-ml
2. **Tests Backend** : pytest sur le backend (avec base in-memory)
3. **Lint Backend** : ruff check
4. **Lint Frontend** : TypeScript `tsc --noEmit`

---

## 14. Ameliorations Possibles

| Amelioration | Impact | Effort |
|-------------|--------|--------|
| ~~Tests unitaires et integration~~ | ~~Qualite logicielle~~ | **FAIT** |
| ~~Docker Compose (one-click deploy)~~ | ~~Demo jour J~~ | **FAIT** |
| ~~Export decisions en CSV~~ | ~~Livrable client~~ | **FAIT** |
| ~~Notifications consultant~~ | ~~Alertes automatiques~~ | **FAIT** |
| Mode batch (N documents d'un coup) | Usage reel Leyton | Moyen |
| ~~Dashboard metriques ML dans le frontend~~ | ~~Maturite IA~~ | **FAIT** |
| ~~Dark mode~~ | ~~UX moderne~~ | **FAIT** |
| ~~Recherche + filtre dossiers~~ | ~~Productivite~~ | **FAIT** |
| ~~Toast notifications~~ | ~~Feedback utilisateur~~ | **FAIT** |
| ~~Loading skeletons~~ | ~~UX percue~~ | **FAIT** |
| ~~Responsive mobile~~ | ~~Accessibilite mobile~~ | **FAIT** |
| ~~Progress bar upload~~ | ~~UX upload~~ | **FAIT** |
| ~~Page 404~~ | ~~Robustesse~~ | **FAIT** |
| ~~Champs extraits + validation dans ReviewPage~~ | ~~Transparence IA~~ | **FAIT** |
| ~~Page Notifications~~ | ~~Workflow consultant~~ | **FAIT** |
| ~~Accessibilite (aria, focus)~~ | ~~Conformite~~ | **FAIT** |
| CamemBERT (si GPU disponible) | Meilleur modele possible | Eleve |
| ~~CI/CD GitHub Actions~~ | ~~Professionnalisme~~ | **FAIT** |

---

*Genere le 24 novembre 2026 — Projet CognitX Leyton ESISA*
