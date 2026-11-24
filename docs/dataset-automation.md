# Étude : constitution automatisée d'un dataset hybride

> Statut : **étude et proposition**. Aucun jeu de données n'a été téléchargé, aucun document généré, aucun modèle entraîné, et l'architecture n'est pas modifiée. Cette étude **se plie à [dataset-strategy.md](dataset-strategy.md) (révision 2)** : 5 classes, plan minimal (38 gabarits), découpage par gabarit, pools d'entités disjoints, jeu stress indépendant, test évalué une fois. Si une idée ci-dessous entre en tension avec cette stratégie, c'est la stratégie qui l'emporte et la tension est signalée (§10).
>
> Les licences ont été vérifiées en ligne le 2026-11-24 ; pour chacune, le **niveau de vérification** est indiqué. Une licence doit être relue **sur la source primaire au moment du téléchargement** : les fiches de miroirs (Hugging Face, agrégateurs) se sont déjà révélées contradictoires pendant cette étude.

> **Révision du 2026-11-24 (après validation par l'équipe).** Décisions intégrées : (1) **Typst n'est pas ajouté** à l'architecture : le rendu reste HTML/CSS + Playwright ; (2) les **procès-verbaux municipaux sont écartés de la v1** (données personnelles) ; (3) les sources de niveau B ont été **vérifiées** (§2.4) : **FNFE-MPE, Kaggle et Roboflow sont écartés**. La composition finale est au §11. En cas de différence avec le §0 ou le §4 ci-dessous, ce sont le §2.4 et le §11 qui font foi.

## 0. Résumé et recommandation

1. **Les datasets publics n'apportent presque rien à notre problème.** Aucun jeu trouvé ne couvre des **fiches de paie** ni des **comptes-rendus R&D** en français, et les rares jeux de factures ou de contrats sont en anglais, en images sans couche texte, ou faits de **documents réels** (noms de personnes, dossiers d'entreprises) que la contrainte « aucun document personnel » nous interdit d'ingérer. La génération par code reste donc le cœur du corpus.
2. **Trois emprunts publics seulement, tous optionnels et tous hors entraînement en v1** : un petit sous-échantillon de **FATURA** (factures en images, 50 mises en page, CC BY 4.0 sur Zenodo) pour le jeu stress ; des pages **DocLayNet** (CDLA-Permissive-1.0) comme sondes « très éloignées » du §7.8.4 ; et, en option, des textes de lois sous **Licence Ouverte** comme matière brute pour `cgv_notice`.
3. **Ce qu'on automatise vraiment** : les étiquettes et la vérité terrain (gratuites par construction), le rendu, les dégradations, les contrôles de doublons et de fuite, les contrôles de rendu. **Ce qu'on assiste** : les gabarits HTML/CSS (brouillon par IA générative, déclaré, relu à l'image) et les blocs de texte libre.
4. **Estimation honnête** : ≈ 30 à 35 % du travail humain de création et de validation disparaît, mais le gain de temps total n'est que de ≈ 14 à 21 h sur ≈ 100 h, parce que l'automatisation coûte elle-même de l'ingénierie. Validation humaine résiduelle : **≈ 9 à 13 h pour toute l'équipe** (§6).
5. **Condition de passage** : un **pilote de 2 à 4 h** (§8.2) mesure le temps réel par gabarit assisté. S'il dépasse 1 h par gabarit, on revient aux gabarits écrits à la main et le plan reste celui de la révision 2.

## 1. Ce que la stratégie (révision 2) impose

| Règle de la révision 2 | Conséquence sur l'automatisation |
|---|---|
| 5 classes ; `autre` faite de **voisins trompeurs**, pas de bruit | Les documents `autre` doivent être générés par sous-type voulu (devis, CR non R&D, CGV/notice, relevé). Un dataset public « autre » aléatoire ne convient pas. |
| Plan minimal : 38 gabarits générés, 348 documents, + ≈ 30 de stress | L'effort est dans les **gabarits**, pas dans les documents : générer 10 000 documents n'a aucun intérêt. |
| Découpage **par gabarit** ; un gabarit = un seul ensemble | Aucune variation cosmétique d'un moteur de gabarits ne compte comme un nouveau gabarit (§3.3). |
| Pools d'entités et domaines R&D disjoints entre train, val, test | Les générateurs de noms prennent un **pool en paramètre** ; assertion automatique de disjonction (§5). |
| Français seul en v1, anglais seulement comme **sonde en stress** | Les jeux publics anglais ne peuvent entrer que dans le stress. |
| Stress : conçu par un membre indépendant, hors générateur | Un sous-échantillon public est compatible (il vient « hors générateur »), mais **ne remplace pas** la conception humaine. |
| Provenance obligatoire : `fictif_genere`, `fictif_manuel`, `anonymise`, `public` | Un document public synthétique est étiqueté `public` **avec une note « non réel »** : jamais présenté comme réel. |
| Texte libre : blocs écrits par l'équipe ; brouillon assisté permis, **relu et déclaré** (§5.4) | Les textes libres assistés par IA sont permis, tracés par `source_texte`, avec ablation E5. |
| Test évalué **une fois** ; aucune donnée ajoutée au test après coup | Aucun jeu public ne nourrit le test des classes principales. |

## 2. Datasets publics : étude

Niveaux de vérification : **P** = lu sur la source primaire ; **S** = lu seulement via une source secondaire (fiche de miroir, agrégateur) ; **N** = non trouvé.

| Jeu | Contenu | Langue | Licence trouvée (vérification) | Documents réels ? | Verdict |
|---|---|---|---|---|---|
| **FATURA** (Zenodo) | 10 000 images de factures générées à partir de **50 gabarits** (200 par gabarit), annotations JSON ; une v2 ajoute des fonds colorés | Anglais (métadonnée Zenodo) | **CC BY 4.0** sur les deux versions (P). Un agrégateur annonçait CC BY-NC-SA 4.0 (S) : contradiction à lever au téléchargement | Non : factures produites à partir de gabarits | **Utilisable en sonde stress** (§4.1). Hors entraînement en v1. |
| **DocLayNet** (IBM) | Pages réelles annotées en mise en page : rapports financiers, manuels, articles scientifiques, lois, brevets, appels d'offres | Majoritairement anglais (à vérifier) | **CDLA-Permissive-1.0** (S : fiches de dataset ; l'en-tête YAML d'une fiche indique « other » : à contrôler) | Oui : pages publiées | **Utilisable en sondes très éloignées** (≈ 20 à 30 pages), jamais comme classe. |
| **CUAD** | ≈ 510 contrats commerciaux réels annotés par des juristes | Anglais | **CC BY 4.0** (S : fiches Hugging Face, IEEE DataPort ; dépôt officiel non lu) | **Oui** : contrats déposés auprès de la SEC, avec noms d'entreprises et de signataires | **Écarté du corpus.** Voir ci-dessous. |
| **RVL-CDIP** | 16 classes (lettres, mémos, factures…) tirées de l'archive de l'industrie du tabac | Anglais | « other » : conditions du portail UCSF à lire (S) | **Oui** : documents internes réels, contenant des personnes | **Écarté.** |
| **FUNSD** | Formulaires bruités | Anglais | Non confirmée : un miroir indique MIT, un autre « fournie par les auteurs » (N/S) | Oui, dérivé de RVL-CDIP | **Écarté.** |
| **SROIE** | ≈ 1 000 tickets de caisse | Principalement malais/anglais | **N** | Oui | **Écarté** : hors classes, licence introuvable. |
| **CORD** | Tickets de caisse annotés | Indonésien | CC BY 4.0 (P : dépôt `clovaai/cord`) | Oui | **Écarté** : hors classes. |
| **DocILE** | Documents d'affaires (factures, commandes), dont 100 k synthétiques | Anglais en majorité | **N** (conditions sur le site du projet, non lues) | Oui pour le jeu annoté | **Écarté** en l'état : licence non établie. |
| **Kleister NDA / Charity** | NDA américains ; rapports de fondations britanniques | Anglais | **N** | Oui, documents publics | **Écarté** : licence non établie, hors classes. |
| **Nemotron-Personas-France** (Pleias / NVIDIA) | **Profils** de personnes françaises synthétiques, pas des documents | Français | **N** | Non | **Optionnel** : source d'identités cohérentes ; Faker suffit. |
| **Données fictives de gestion commerciale** (data.gouv.fr, DOPHIS) | Données fictives de gestion commerciale ; contenu précis non lu | Français | **Licence Ouverte 2.0** (S : page data.gouv.fr) | Non | **À examiner** comme source de catalogues et lignes de facture. Contenu non vérifié. |
| **Textes de loi, Licence Ouverte 2.0** | Textes officiels réutilisables | Français | Licence Ouverte 2.0 : réutilisation libre, **attribution obligatoire**, respect des règles sur les données personnelles (P). Conditions propres à Légifrance **non lues** | Non personnels | **Optionnel** : matière brute pour `cgv_notice`. |

**Non examinés** : Tobacco800, Industry Documents Library, jeux dérivés de Common Crawl (PDF), EDGAR, HAL, Cerfa. Aucune conclusion à leur sujet.

### 2.1 Pourquoi CUAD, RVL-CDIP et leurs semblables sont écartés

Tous trois contiennent des **documents réels d'entreprises**. Même publics, ils portent des noms de signataires et d'entreprises : c'est le type de document que la consigne exclut (« jamais de documents personnels ou confidentiels ») et que le cahier des charges limite (« fictifs ou anonymisés uniquement », p.4 et p.12). Les anonymiser automatiquement (détection de noms) serait peu fiable et ajouterait un risque de fuite de noms réels. Ils sont aussi en anglais, ce qui n'est pas notre cible v1. **Ces jeux restent utilisables à titre d'inspiration** (quelles clauses on trouve dans un contrat), sans copie de texte.

### 2.2 Constat sur la couverture

| Classe | Couverture publique | Conclusion |
|---|---|---|
| `facture` | FATURA : 50 mises en page, anglais, images | Sonde stress seulement |
| `fiche_de_paie` | **Rien trouvé** | Génération seule |
| `contrat` | CUAD, Kleister : réels et anglais | Génération seule |
| `compte_rendu_rd` | **Rien trouvé** | Génération seule |
| `autre` | DocLayNet (sondes éloignées) ; lois (Licence Ouverte) comme matière | Génération + emprunts marginaux |

### 2.3 Risques propres aux jeux publics

| Risque | Détail | Parade |
|---|---|---|
| **Licence mal lue** | Miroirs contradictoires (FATURA : CC BY 4.0 sur Zenodo contre NC-SA ailleurs ; DocLayNet : « other » dans un en-tête, CDLA dans le texte). | Source primaire seulement ; capture de la page de licence dans `data/annotations/licences/` au moment du téléchargement. |
| **Redistribution** | Un dépôt Git lisible par l'encadrant ou public **redistribue** les fichiers qu'on y met. | Ne **pas** committer les fichiers publics : on committe un script de récupération, la liste des identifiants et l'attribution. Chaque document public est dans `data/interim/` ou `data/private/`, ignoré par Git. |
| **Faux réalisme** | FATURA est fait de gabarits : le présenter comme « factures réelles » serait faux. | Provenance `public` + note « généré, non réel » ; mention dans le rapport. |
| **Langue** | Anglais : le vocabulaire diffère de nos documents. | Sonde stress uniquement, rapportée à part. |
| **Documents réels cachés** | Un lot « public » peut contenir des données personnelles (DocLayNet : pages réelles). | Sondes éloignées uniquement (rapports, manuels, brevets), contrôle visuel des pages retenues, aucune page avec nom de personne. |
| **Fuite par gabarit** | Un gabarit FATURA présent à la fois en stress et en entraînement fausserait l'évaluation. | `gabarit_id` = identifiant du gabarit FATURA ; un gabarit va dans **un seul** ensemble. |
| **Dérive de version** | v1 et v2 de FATURA diffèrent (fonds colorés). | Version et empreinte notées dans le manifeste. |
| **Attribution oubliée** | CC BY 4.0 et Licence Ouverte exigent l'attribution. | Fichier `data/ATTRIBUTIONS.md` tenu à jour, rempli par le script de récupération. |

### 2.4 Vérification des sources de niveau B (2026-11-24)

Pages lues le 2026-11-24 ; **P** = lu sur la page de la source, **S** = lu via une recherche ou un miroir, **N** = non établi.

| | FNFE-MPE (exemples Factur-X) | Kaggle « High-Quality Invoice Images for OCR » | Roboflow Universe (projets « payslip ») |
|---|---|---|---|
| **Lien** | <https://fnfe-mpe.org/factur-x/> | <https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr> ; port Hugging Face : <https://huggingface.co/datasets/Voxel51/high-quality-invoice-images-for-ocr> | <https://universe.roboflow.com/sherin/salary-payslip>, <https://universe.roboflow.com/doingproject/payslip-zk13y>, <https://universe.roboflow.com/arya-btl0l/cheque-payslip>, <https://universe.roboflow.com/document-classification/document_classification-clhzu> |
| **Licence originale** | **Aucune licence ouverte pour les exemples** (P). Page Factur-X : aucune mention de licence ni de réutilisation. [Mentions légales](https://fnfe-mpe.org/mentions-legales/) (P) : contenus « protégés par le Code de la propriété intellectuelle » et « propriété exclusive de l'association » ; reproduction, adaptation ou exploitation, même partielles, interdites « sauf accord écrit préalable ». Les licences BSD (`akretion/factur-x`) et Apache-2.0 (`mustangproject`) couvrent le **code**, pas les exemples. | **Non lue** : la page Kaggle ne s'affiche pas en lecture automatique (seul le titre est renvoyé). Le port Hugging Face est **incohérent** : métadonnée `odbl` mais corps du texte « licence d'origine de Kaggle » (P). | **Non lue** : les quatre pages renvoient HTTP 403. Les listes de recherche annoncent CC BY 4.0 pour `payslip-zk13y`, `cheque-payslip` et `document_classification` (S) ; pour `salary-payslip`, 6 images et aucune description (S). Le forum Roboflow indique que la licence est **choisie par l'utilisateur** qui dépose le jeu (S) : elle ne prouve ni qu'il en détient les droits ni que les personnes ont consenti. |
| **Provenance des documents** | Association FNFE-MPE ; exemples « sous tous les profils et pour différentes situations ». **Non décrits comme fictifs**, nombre non indiqué. Téléchargement derrière un **formulaire e-mail**. | Port Hugging Face : « factures synthétiques à mises en page réalistes », outil de génération non nommé. Un miroir (Papers with Code) la décrit au contraire comme des « documents numérisés et capturés numériquement », datée de 2021 : **contradiction non résolue** (S). | **Inconnue** : aucune description lue ; images réelles ou synthétiques, pays et langue non établis. |
| **Données personnelles** | Non déterminable sans ouvrir l'archive. | Port Hugging Face : noms, adresses, identifiants fiscaux et IBAN « fictifs » (P, déclaration non vérifiable). | **Risque élevé** : une fiche de paie réelle contient des données personnelles, quelle que soit la licence. Aucune garantie lue. |
| **Gabarits distincts** | Inconnu (non vérifié). | **≈ 1** : « Uniform Layout / similar template structure » (P) pour 8 181 images annoncées (8 106 lignes visibles). | Inconnu ; projets de 6 images pour `salary-payslip`. |
| **Réutilisation académique** | **Non établie** : aucune autorisation écrite. | **Non établie** : licence et provenance non résolues. | **Non établie**. |
| **Verdict** | **Écarté de la v1.** Seule voie : demander par courriel un accord écrit à l'association (en parallèle, sans dépendre de la réponse). | **Écarté** : licence et provenance irrésolues ; et, même résolues, un seul gabarit n'apporte qu'**un** gabarit. | **Écarté** : non vérifiable, volume dérisoire, risque personnel. Réévaluer seulement si un membre ouvre la page dans un navigateur et y trouve des documents clairement fictifs, d'origine documentée, avec une licence lisible. |

Autres sources confirmées ou retenues depuis la première étude :

| Source | Statut vérifié | Remarque |
|---|---|---|
| [Cabinet Digital, 10 factures d'exemple](https://www.cabinetdigital.fr/facture-electronique/exemples-de-factures/) | P : « Données fictives · licence CC BY 4.0 », réutilisation libre y compris commerciale avec un lien vers la page ; 10 factures en Factur-X, CII et UBL (32 fichiers) ; français ; entreprises fictives | Site commercial, pas une source officielle. Les numéros SIREN fictifs sont repris des exemples du FNFE-MPE ; seuls des identifiants sont repris, la licence annoncée est celle de Cabinet Digital. Risque résiduel faible, à écrire dans le journal des licences. **Un seul gabarit** (mise en page non vérifiée comme multiple). |
| [FATURA](https://zenodo.org/records/10371464) | P : CC BY 4.0 sur Zenodo ; 50 gabarits ; anglais | Sonde stress seulement. |
| [Open Terms Archive](https://www.data.gouv.fr/datasets/france-collection-dataset) | S : ODbL ; 124 fournisseurs (jeu France), 388 (jeu contrib) ; Markdown | Matière brute de `cgv_notice` (voir §11). Partage à l'identique à respecter ; fichiers non committés. |
| [DocLayNet](https://huggingface.co/datasets/ds4sd/DocLayNet/blob/main/README.md?code=true) | S : CDLA-Permissive-1.0 | Sondes éloignées uniquement. |

### 2.5 Décisions de l'équipe et conséquences

- **Typst écarté.** Les paquets de factures de Typst Universe (MIT, MIT-0, ISC selon les fiches) ne sont pas utilisés : le rendu reste **HTML/CSS + Playwright**. Il n'y a donc **aucun gabarit « récupéré puis adapté » confirmé** pour l'instant (voir §2.6).
- **Procès-verbaux municipaux écartés de la v1** : noms d'élus et d'habitants, licences souvent « non spécifiées ». `compte_rendu_non_rd` est entièrement généré.

### 2.6 Gabarits HTML/CSS ouverts : candidats à vérifier

Recherche complémentaire (S, indexeurs tiers ; **le fichier LICENSE de chaque dépôt doit être lu avant tout emploi**) :

| Candidat | Licence annoncée | Remarque |
|---|---|---|
| [sparksuite/simple-html-invoice-template](https://awesome.ecosyste.ms/projects/github.com%2Fsparksuite%2Fsimple-html-invoice-template) | MIT | Une mise en page minimale à tableau, avec styles d'impression. |
| [inambe/html-invoice-template](https://awesome.ecosyste.ms/projects/github.com%2Finambe%2Fhtml-invoice-template) | MIT | Facture simple imprimable. |
| [anvilco/html-pdf-invoice-template](https://www.github.com/anvilco/html-pdf-invoice-template) | MIT | `invoice.html`, `invoice.css`, `invoice-pdf.css`. **Ne réutiliser que le HTML/CSS** : le script d'exemple dépend d'une API commerciale. |

Chacun est **une** mise en page simple. Règle : un candidat ne compte comme **gabarit distinct** que s'il diffère de nos autres gabarits d'au moins 3 axes structurels (§3.3) ; sinon il est ignoré. Estimation prudente : **0 à 2 gabarits utilisables** après adaptation (contenu français, champs de notre schéma, notice MIT conservée dans l'en-tête du fichier). Ce chiffre est une hypothèse, pas un acquis.

## 3. Chaîne de génération proposée

### 3.1 Vue d'ensemble

```
 conception du gabarit        ┌────────────── automatique, piloté par une graine ──────────────┐
 (brief + brouillon assisté   │                                                                 │
  + relecture à l'image)      │  entités ─► contenu ─► rendu ─► dégradation ─► lecture ─► contrôles
        │                     │  (pool par  (champs,   (HTML    (Augraphy /    (texte du   (doublons,
        ▼                     │   ensemble) lignes,    → PDF)   OpenCV)        pipeline)   fuites,
   gabarit_id (groupe)  ──────┤             textes)                                         rendu)
                              │                 │                                              │
                              │                 └─► vérité terrain + manifeste ◄───────────────┘
                              └─────────────────────────────────────────────────────────────────┘
                                                               │
                              échantillons à regarder (planches-contact) ◄── validation humaine minimale
```

Une graine unique par document. `python -m datagen build --plan minimal` régénère tout à l'identique. Le code est prévu dans `src/datagen/` (création après validation, conformément à la révision 2).

### 3.2 Outils Python

Les licences marquées « connue » viennent de ma connaissance générale et sont à relire à l'installation ; seule la licence d'Augraphy a été confirmée pendant cette étude (PyPI : MIT).

| Besoin | Outil recommandé | Alternative | Licence | Remarque |
|---|---|---|---|---|
| Identités, adresses, montants | **Faker** (`fr_FR`) | Mimesis | connue : MIT | Les valeurs sont plausibles, pas réelles ; voir règles d'identifiants invalides (§3.5). |
| Gabarits | **Jinja2** | | connue : BSD | Le gabarit est du code versionné, revu comme du code. |
| HTML → PDF | **Playwright (Chromium)**, `page.pdf()` | WeasyPrint ; ReportLab (Python pur, sans navigateur) | connue : Apache-2.0 / BSD | **Chromium seulement** pour l'export PDF (confirmé). Plan B si l'installation sous Windows échoue : ReportLab, en pure Python mais avec moins de liberté de mise en page. WeasyPrint demande des bibliothèques système (Pango) réputées pénibles sous Windows. |
| PDF « Word » (gabarits faits à la main) | LibreOffice en ligne de commande | | connue : MPL | Pour les gabarits `fictif_manuel` issus d'un traitement de texte. |
| Rasterisation PDF → image | **pypdfium2** | PyMuPDF | connue : Apache/BSD | PyMuPDF est, à ma connaissance, sous **AGPL-3.0** : à vérifier avant d'en faire une dépendance de livrable ; le backend le déclare aujourd'hui dans `pyproject.toml` (point à examiner séparément). |
| Dégradations de scan | **Augraphy** | OpenCV + Pillow | **MIT (confirmé)** | Simule impression, scan, plis, bruit, encre. Paramètres tirés par graine. |
| Perspective, rotation, flou | OpenCV, Pillow | | connue : Apache-2.0 / HPND | Photo, perspective, flou, JPEG. |
| OCR | **Tesseract** (`fra`) via pytesseract | | connue : Apache-2.0 | Version et paramètres figés dans le manifeste. |
| Doublons exacts / quasi-exacts | `hashlib` (SHA-256), **imagehash** (hachage perceptuel), **datasketch** (MinHash sur le texte) | RapidFuzz | connue : BSD / MIT | §5. |
| Schémas du manifeste | **Pydantic** + pandas | | connue : MIT / BSD | Validation de chaque ligne avant écriture. |
| Découpage | scikit-learn `StratifiedGroupKFold` | | connue : BSD | Déjà dans la dépendance ML. |
| Brouillon de gabarits et de textes | IA générative (outil déclaré) | Écriture manuelle | n/a | Voir §3.3 et §3.4. |

### 3.3 Gabarits : le vrai poste de travail

Les 38 gabarits coûtent le plus (47 à 78 h à la main selon le §2.3 de la révision 2). Piste d'assistance :

1. **Brief de conception tiré au hasard** : pour chaque gabarit, un script échantillonne des choix sur les axes du §5.2 de la révision 2 (colonnes, position de l'en-tête, style de tableau, police, formules, formats de date et de nombre, éléments graphiques, nombre de pages).
2. **Brouillon HTML/CSS par IA générative** à partir du brief et du schéma de données du type de document ; le gabarit reçoit le contenu par Jinja2, pas par texte figé.
3. **Rendu automatique** d'un échantillon, avec une **planche-contact** (12 rendus du même gabarit).
4. **Relecture humaine de 3 à 5 minutes** : le gabarit ressemble-t-il à un vrai document de ce type ? Texte qui déborde, polices manquantes, mise en page absurde → retouche ou rejet.

**Honnêteté sur l'hypothèse** : j'estime 0,5 à 0,9 h par gabarit assisté contre 1,5 à 2,5 h manuel. C'est une **hypothèse**, à mesurer sur le pilote (§8.2). Les gabarits assistés doivent rester des **gabarits indépendants** :

- **Piège d'inflation** : trois habillages CSS d'une même structure ne sont pas trois gabarits ; compter trois gabarits indépendants fabriquerait une fuite déguisée entre train et test. Règle : deux gabarits ne sont distincts que s'ils diffèrent sur **au moins 3 des axes structurels** du brief (pas seulement couleur ou police).
- **Signature de structure** : chaque gabarit reçoit une signature automatique (séquence des blocs, nombre de colonnes, type de tableau, position de l'en-tête). Un contrôle compare les signatures **entre ensembles** et signale toute paire trop proche (§5). Un gabarit de test trop proche d'un gabarit d'entraînement est **refait**.
- **Homogénéité d'un seul assistant** : des brouillons produits par la même IA risquent d'avoir un style commun. Parade : briefs aléatoires, sources de gabarit mélangées comme prévu en §5.2 de la révision 2 (équipe, modèles publics, faits à la main) et ablation E5.
- **Déclaration** : chaque usage est noté dans [declaration-ia.md](declaration-ia.md). Chacun doit pouvoir expliquer le code du gabarit qu'il valide.

### 3.4 Textes libres

`compte_rendu_rd` et le corps de `contrat` sont les parties les plus fragiles (révision 2, §5.4). Chaîne proposée :

1. **Plan des blocs** : par domaine R&D (disjoints entre ensembles), une liste de rubriques (objectif, travaux, verrou technique, résultats, prochaines étapes).
2. **Brouillons assistés** de paragraphes, par rubrique et par domaine, en grande quantité.
3. **Filtres automatiques** : langue française, longueur, **liste de noms interdits** (entreprises et personnes réelles courantes), détection de **doublons et de quasi-doublons** entre blocs, détection des domaines qui fuient d'un ensemble à l'autre (un mot-clé d'un domaine de test dans un bloc de train).
4. **Lecture humaine d'un échantillon** de blocs (≈ 10 %), jusqu'à obtenir un taux de défauts acceptable ; chaque bloc garde `source_texte = brouillon_llm_relu`.
5. **Recombinaison** par le générateur (ordre, omissions, longueurs) comme dans la révision 2.
6. Le **stress** contient du texte écrit à la main sans réemploi de ces blocs.

### 3.5 Particularités par classe

| Classe | Génération | Points d'attention |
|---|---|---|
| `facture` | Lignes tirées d'un catalogue fictif (éventuellement issu de la base DOPHIS si son contenu convient) ; HT, TVA, TTC **calculés** ; échéance ; mentions légales ; défauts injectés (montant incohérent, mention absente). | Les identifiants (SIREN, TVA, IBAN) ont une **somme de contrôle volontairement invalide**. |
| `fiche_de_paie` | Employeur, salarié (pool fictif), période, brut, cotisations **cohérentes entre elles**, net à payer ; variantes de présentation. | Les taux sont **illustratifs** : le but est un document plausible, pas une conformité de paie. Le dire dans le rapport. |
| `contrat` | Clauses tirées d'une bibliothèque par type (prestation/sous-traitance, travail, collaboration de recherche) ; parties issues des pools ; numérotation d'articles variable. | Plus l'ordre et la longueur varient, moins le modèle apprend un plan fixe. Domaines de collaboration disjoints entre ensembles. |
| `compte_rendu_rd` | Blocs par domaine (§3.4) ; participants ; ordre du jour ; tableaux d'indicateurs. | Domaines R&D disjoints entre train, val et test. |
| `autre` | Un générateur par sous-type du plan minimal : `devis`, `compte_rendu_non_rd`, `cgv_notice` (matière : textes de lois ou rédactions propres), `releve_bancaire`, plus l'inconnu `attestation_emploi`. | Chaque sous-type doit **ressembler** à sa cible trompeuse (§1.2 de la révision 2), sinon `autre` redevient trop facile. |

Toutes les classes : adresses de courriel sur un domaine réservé (`example.org`), numéros de téléphone dans les plages réservées à la fiction (à vérifier avant usage), logos et tampons produits par code.

### 3.6 Dégradations et cas difficiles

Appliquées par script, par niveau (0 / 1 / 2) comme défini en §5.5 de la révision 2 : rotation, flou, bruit, JPEG, faible résolution, plis, taches, ombres, perspective, rognage, texte masqué, page manquante, page de garde, quasi-vide, rotation de 90°. Les paramètres de chaque dégradation sont écrits dans `degradations` du manifeste. Le niveau est stratifié **par ensemble** pour que le test ne soit pas plus facile que le train.

## 4. Où les sources publiques entrent

### 4.1 FATURA : sonde stress pour `facture`

- **Quoi** : 2 à 3 factures issues de **2 à 3 gabarits FATURA distincts**, sur les 5 factures du stress. Les 2 ou 3 autres sont écrites à la main en français par le porteur du stress.
- **Pourquoi** : une mise en page produite par un tiers, en dehors de notre générateur, est exactement l'esprit du stress ; coût humain faible.
- **Limites** : anglais et images (OCR obligatoire, pas de couche texte) ; synthétique ; présenté comme tel.
- **Règles** : provenance `public`, note « généré, non réel », `gabarit_id` = identifiant du gabarit FATURA, licence et version archivées, **fichiers non committés**, attribution.
- **Extension (vague 2 seulement)** : on peut envisager des gabarits FATURA en entraînement pour la diversité de mise en page, mais **jamais** un gabarit déjà utilisé dans le stress ; décision après la vague 1, car l'anglais risque de brouiller le modèle français.

### 4.2 DocLayNet : sondes éloignées (§7.8.4)

20 à 30 pages de catégories sans rapport (manuel, brevet, article scientifique), contrôlées à l'œil pour exclure tout nom de personne. Elles servent uniquement de **cas trivial de contrôle** pour la détection de documents inconnus. Elles ne rejoignent aucune classe, ne comptent pas dans les métriques et n'entrent jamais en entraînement.

### 4.3 Textes de lois : matière pour `cgv_notice` (optionnel)

Articles réutilisables sous Licence Ouverte pour garnir le corps de documents `cgv_notice`. Seulement du **texte brut** inséré dans nos gabarits. À confirmer : les conditions propres de la source choisie (Légifrance n'a pas été lu).

**Mise à jour (2026-11-24)** : la source retenue pour `cgv_notice` est **Open Terms Archive** (ODbL, textes français de conditions générales), à la place des textes de lois. Les textes de lois restent une option de secours. Contrainte de fuite : **chaque fournisseur n'apparaît que dans un seul ensemble** (§11.3).

### 4.4 Ce qui n'entre pas

CUAD, ContractNLI, RVL-CDIP, FUNSD, SROIE, CORD, DocILE, Kleister (§2) ; **FNFE-MPE, Kaggle « High-Quality Invoice Images », Roboflow, Mendeley, katanaml (§2.4)** ; les procès-verbaux municipaux ; Typst. Aucun document personnel ou confidentiel, aucun document réel dans les classes.

## 5. Garde-fous automatiques : doublons et fuites

Un script `check_dataset` s'exécute à chaque régénération et **échoue** (avec un rapport) si un contrôle est violé. Aucun découpage n'est figé tant qu'il n'est pas vert.

| Contrôle | Méthode | Seuil d'échec |
|---|---|---|
| Doublons exacts | SHA-256 des fichiers et du texte normalisé | Tout doublon |
| Doublons visuels | Hachage perceptuel (imagehash) de la première page | Distance inférieure à un seuil, **entre ensembles** |
| Quasi-doublons de texte | MinHash sur n-grammes de caractères | Similarité supérieure à un seuil, **entre ensembles** |
| Gabarit unique par ensemble | Chaque `gabarit_id` n'apparaît que dans un `split` | Toute occurrence multiple |
| Signature de structure | Distance entre signatures de gabarits (§3.3) | Paire train/test (ou val/test) trop proche |
| Pools d'entités | Intersection de noms (entreprises, personnes, projets) entre pools A, B, C | Toute intersection non vide |
| Domaines R&D | Intersection des domaines entre ensembles ; mots-clés d'un domaine dans un autre ensemble | Toute intersection |
| Dérivés | Un document dérivé (`derived_from`) reste dans l'ensemble de sa source | Tout écart |
| Artefacts | Un classifieur test, nourri **seulement** de métadonnées PDF, noms de fichiers, tailles et résolutions, doit rester au niveau du hasard | Écart significatif |
| Mot-titre | Part des documents dont le titre est le seul indice (info pour l'expérience E2) | Information, pas échec |
| Provenance | Chaque ligne a `provenance`, `licence` si `public`, `seed_generation` | Champ manquant |
| Échantillon public | Aucun fichier public dans le dépôt Git | Tout fichier dont l'empreinte est dans la liste `public` |
| Qualité de rendu | Aller-retour : texte extrait du PDF natif contre `texte_reference` ; CER de l'OCR sur les scans ; détection de page vide, débordement, glyphes manquants, nombre de pages hors bornes | Seuils fixés sur le pilote |
| Équilibre | Effectifs par classe, par niveau de dégradation, par provenance, par gabarit | Écart à la table du §2.2 |

Les seuils chiffrés sont **fixés sur le pilote**, pas ici : je ne les invente pas.

## 6. Validation humaine minimale

Le principe : **on regarde peu, mais on regarde les bons endroits**, avec des planches-contact plutôt que des fichiers un à un.

| Contrôle humain | Quantité | Temps unitaire | Total |
|---|---|---|---|
| Planche-contact de chaque gabarit (le gabarit ressemble-t-il à un vrai document de son type ?) | 38 | 4 min | ≈ 2,5 h |
| Échantillon de documents générés : étiquette plausible, rendu lisible (10 %, tiré par classe et niveau) | ≈ 35 | 3 min | ≈ 2 h |
| Paires trompeuses : vérifier que les quasi-jumeaux sont bien d'une classe différente | ≈ 15 paires | 4 min | ≈ 1 h |
| Lecture d'un échantillon de blocs de texte assistés | ≈ 40 blocs | 3 min | ≈ 2 h |
| Contrôle des pages publiques retenues (aucun nom de personne) | ≈ 30 | 1 min | ≈ 0,5 h |
| Double annotation indépendante du **stress** (second lecteur) | ≈ 30 | 2 min | ≈ 1 h |
| Relecture du rapport de fuite et décisions sur les alertes | 1 passage par vague | | ≈ 1,5 h |
| Journal des licences et attributions | | | ≈ 1 h |
| **Total** | | | **≈ 11 h** (fourchette 9 à 13 h) |

Ces 11 h concernent l'ensemble de l'équipe. Le coefficient de Cohen n'est calculé que sur le stress et les documents annotés par des humains (§3.4 de la révision 2) : pour les documents générés, l'étiquette est déterministe.

## 7. Estimation : part automatisée et temps

### 7.1 Comparaison avec la révision 2

| Poste | Révision 2, plan minimal (§2.3) | Approche hybride | Remarque |
|---|---|---|---|
| Pilote et chaîne de rendu | inclus dans l'infrastructure | 4 à 6 h | Mesure indispensable |
| Générateur, entités, contenu, vérité terrain, manifeste | 25 à 40 h (infra) | 18 à 28 h | Code à écrire une fois |
| Dégradations | inclus | 5 à 8 h | Augraphy / OpenCV |
| Scripts : découpage, fuites, qualité de rendu | 8 à 12 h | 12 à 18 h | **Plus d'automatisation = plus de code** |
| 38 gabarits | 47 à 78 h (24 principaux à 1,5-2,5 h, 12 `autre` à 0,75-1,25 h, 2 inconnus) | 19 à 34 h (0,5 à 0,9 h par gabarit assisté) | **Hypothèse à mesurer** |
| Blocs de texte | non isolé dans la révision 2 | 5 à 8 h | |
| Stress (≈ 30, dont 2-3 factures publiques) | 12 à 15 h | 9 à 13 h | Reste humain |
| Sources publiques (récupération, licences, OCR, contrôle) | 0 | 3 à 5 h | |
| Validation humaine (§6, hors double annotation du stress) | 5 à 8 h (QA) | 8 à 12 h | |
| **Total** | **97 à 153 h** | **≈ 83 à 132 h** | Économie ≈ 14 à 21 h (≈ 14 %) |

Les totaux sont des sommes de lignes (bas : 4 + 18 + 5 + 12 + 19 + 5 + 9 + 3 + 8 = 83 ; haut : 6 + 28 + 8 + 18 + 34 + 8 + 13 + 5 + 12 = 132). Le tableau de la révision 2 ne séparait pas les blocs de texte : la comparaison est donc approximative sur ce poste.

### 7.2 Pourcentage de travail automatisable

| Activité | Part automatisée ou machine | Détail |
|---|---|---|
| **Étiquettes de classe et vérité terrain** (texte de référence, champs, défauts) | **≈ 100 %** | Connues du générateur. Déjà gratuites dans la révision 2. |
| Rendu, dégradations, OCR, manifeste, découpage | ≈ 95 % (après écriture du code) | |
| Contrôles de doublons, de fuite, de rendu | ≈ 90 % | La décision face à une alerte reste humaine. |
| **Gabarits** | **≈ 50 à 60 %** du temps humain | Brouillon automatique ; conception, choix du brief et relecture restent humains. |
| Textes libres | ≈ 60 à 70 % | Brouillon assisté ; filtrage automatique ; lecture humaine d'un échantillon. |
| Stress | ≈ 10 à 20 % | Doit rester humain et indépendant. |
| Contrôle final de réalisme | **0 %** | Aucun script ne juge si un document « fait vrai ». |

**Synthèse chiffrée (milieu de fourchette)** : le travail **humain de création et de validation** passe d'environ 83 h (gabarits, stress, QA) à environ 55 h (gabarits assistés, textes, stress, validation), soit **≈ 33 % de réduction**. En contrepartie, l'effort d'**ingénierie** (code du générateur et des contrôles) reste **≈ 35 à 55 h**, incompressible. Au total, on économise **≈ 14 à 21 h sur ≈ 100 h** : l'automatisation ne fait pas disparaître le coût, elle le déplace du fichier vers le code, et elle rend le corpus **reproductible et contrôlable**. Ces pourcentages sont des estimations de planification, pas des mesures.

## 8. Recommandation pour 4 étudiants

### 8.1 Répartition

| Rôle | Responsabilités | Charge indicative |
|---|---|---|
| **A, responsable des données** | Générateur central, manifeste, découpage, `check_dataset`, pools d'entités | 25 à 35 h |
| **B** | Gabarits `facture`, `fiche_de_paie`, `contrat` ; rendu Playwright ; lignes et calculs | 18 à 28 h |
| **C** | Gabarits `compte_rendu_rd` et `autre` ; blocs de texte ; dégradations | 18 à 28 h |
| **D, indépendant** | **Stress** (rédigé sans voir les gabarits de développement), second lecteur, journal des licences, sources publiques ; le reste de son temps sur l'application | 14 à 20 h |

D ne réalise **aucun** gabarit de développement : c'est la condition d'indépendance du stress. Total des rôles : 75 à 111 h ; les ≈ 8 à 21 h restantes (pilote en commun, validation humaine du §6, relecture croisée) sont partagées entre les quatre, soit 83 à 132 h au total.

### 8.2 Calendrier (J0 = démarrage, sous réserve de la validation par l'équipe)

| Quand | Étape | Sortie | Porte |
|---|---|---|---|
| J0 à J1 | **Pilote (2 à 4 h)** : installer Playwright et Chromium sous Windows ; rendre un PDF ; faire produire 3 gabarits assistés ; mesurer le temps réel ; essai Augraphy sur 3 documents ; vérifier Tesseract `fra` | Mesures de temps ; liste de problèmes | **Porte G1** : temps par gabarit assisté ≤ 1 h et rendu acceptable, sinon gabarits manuels |
| Fin de S1 | **Vague 0** : générateur de base, 2 gabarits par classe principale, 1 par sous-type de `autre`, 8 documents par gabarit | Corpus d'amorçage pour le parcours de bout en bout | Aucun score publié |
| S2 | Gabarits restants, blocs de texte, dégradations, `check_dataset` vert, stress par D | **Vague 1** : plan minimal complet | **Porte G2** : tous les contrôles du §5 verts + validation humaine du §6 |
| Fin de S2 | **Découpage verrouillé**, `splits.csv` versionné, test et stress figés | Étiquette Git `corpus-v1` | Test non regardé |
| S4 à S5, si possible | **Vague 2** : gabarits supplémentaires en train et val seulement ; éventuel versement de gabarits FATURA en train | Courbe d'apprentissage (E4) | Test inchangé |

Si la porte G1 échoue : on garde le plan de la révision 2 (gabarits à la main), et tout le reste de cette étude (contrôles automatiques, textes assistés, sondes publiques) reste valable.

### 8.3 Ce que je recommande de ne **pas** faire

- Télécharger un gros jeu public « pour voir » : 0 gain pour nos 5 classes, risque de contamination par des données personnelles.
- Multiplier les habillages CSS d'un même gabarit pour atteindre un nombre de gabarits : fuite déguisée.
- Faire générer le stress par le même assistant et les mêmes briefs que le développement : il perdrait son indépendance.
- Utiliser l'IA générative pour étiqueter : les étiquettes viennent du générateur, jamais d'un modèle.
- Committer les fichiers de FATURA ou de DocLayNet dans le dépôt.

## 9. Risques

| Risque | Gravité | Parade |
|---|---|---|
| Playwright/Chromium non installable ou instable sous Windows chez un membre | Moyenne | Pilote J0 ; plan B ReportLab ; un seul poste « générateur » par défaut |
| Gabarits assistés trop similaires | **Élevée** (fuite déguisée) | Briefs aléatoires, signatures de structure, contrôle entre ensembles, refaire tout gabarit de test trop proche |
| Textes assistés homogènes, ou « signature de style » liée à une classe | Moyenne | Ablation E5 ; stress rédigé à la main ; lecture d'un échantillon |
| Noms réels générés par l'assistant | Moyenne | Liste de noms interdits ; recherche ponctuelle des noms d'entreprises inventés ; aucune donnée issue d'un document réel |
| Corpus « trop propre » | Moyenne | Dégradations, stress, documents quasi-jumeaux, mesure de l'écart entre propre et dégradé |
| Licence d'un jeu public mal comprise | Moyenne | Source primaire, capture au téléchargement, fichiers non committés, attribution |
| Surcoût d'ingénierie de l'automatisation | Moyenne | Pilote et portes ; priorité au générateur minimal avant les contrôles avancés |
| Dépendance de licence (ex. AGPL de PyMuPDF) | Faible à moyenne | Vérification à l'installation ; alternative pypdfium2 |
| Résultats trop bons malgré tout | **Élevée** | Découpage par gabarit, stress indépendant, limites écrites dans le rapport : les scores ne valent que pour des documents fictifs |

## 10. Tensions avec la révision 2 et points à décider

1. **Stress « hors générateur »** : les 2 à 3 factures FATURA sont compatibles, mais le stress reste surtout humain. L'équipe doit confirmer qu'un sous-échantillon public compte comme « hors générateur ».
2. **Provenance** : FATURA est synthétique, mais la valeur `public` de la révision 2 ne le dit pas. Proposition : conserver `public` et ajouter une note de manifeste « généré, non réel », sans nouvelle valeur.
3. **Gabarits assistés** : la révision 2 prévoit trois origines de gabarits (équipe, modèles publics, faits à la main). Les brouillons assistés ajoutent une **quatrième origine** à déclarer dans le manifeste (`auteur_gabarit` = `ia_relu`).
4. **Langue** : les sources publiques sont anglaises. Elles ne peuvent entrer que dans le stress en v1, comme la révision 2 le prévoit.
5. **À confirmer avec l'encadrant** : l'usage d'IA générative pour produire des **gabarits et des textes** de documents de test est-il compatible avec « IA générative autorisée comme outil, à déclarer » (p.12) ? Je le lis ainsi, mais la question est posée.
6. **À vérifier avant tout téléchargement** : relire le fichier de licence de FATURA (Zenodo), de Cabinet Digital, de DocLayNet, d'Open Terms Archive et de chaque dépôt HTML/CSS candidat (§2.6), ainsi que les outils non confirmés (§3.2). FNFE-MPE, Kaggle et Roboflow sont écartés (§2.4). Le jeu DOPHIS n'a pas été examiné et n'est pas retenu.
7. **PyMuPDF** : à examiner, car il figure dans les dépendances du backend et pourrait être sous AGPL ; sans modification de l'architecture à ce stade.

## 11. Composition finale du dataset v1

Plan : **minimal** de la révision 2 de la stratégie (38 gabarits, 348 documents + ≈ 30 de stress). Trois catégories, sans mélange :

- **Récupérés légalement** : fichiers pris tels quels, sous licence vérifiée.
- **Récupérés puis adaptés** : gabarits (code HTML/CSS) ou textes sous licence ouverte, que nous transformons.
- **Générés automatiquement** : produits par notre générateur à partir de gabarits que nous écrivons.

### 11.1 Par classe

| Classe | Gabarits | Documents récupérés tels quels | Gabarits récupérés puis adaptés | Gabarits écrits par nous | Documents générés |
|---|---|---|---|---|---|
| `facture` | 6 | **10** (Cabinet Digital, 1 gabarit) | **0 à 2** (candidats HTML/CSS MIT du §2.6, sous réserve) | 3 à 5 | 50 |
| `fiche_de_paie` | 6 | 0 | 0 | 6 | 60 |
| `contrat` | 6 | 0 | 0 | 6 | 60 |
| `compte_rendu_rd` | 6 | 0 | 0 | 6 | 60 |
| `autre` vue (4 sous-types × 3 gabarits) | 12 | 0 | 0 (un devis peut dériver d'un gabarit de facture) | 12 | 96, dont **24** de `cgv_notice` au corps de texte récupéré (§11.3) |
| `autre` inconnue (`attestation_emploi`) | 2 | 0 | 0 | 2 | 12 |
| **Corpus généré (hors stress)** | **38** | **10** | **0 à 2** | **35 à 37** (le gabarit récupéré compte pour 1) | **338** |

Vérification : 10 + 338 = 348 documents ; les gabarits de `facture` : 1 récupéré + (0 à 2) adaptés + (3 à 5) écrits = 6.

**Jeu stress (≈ 30)** : **2 à 3** factures FATURA (anglais, gabarits distincts, images ; récupérées légalement) et **≈ 27 à 28** documents rédigés à la main par le porteur du stress, hors générateur. **Sondes très éloignées** (hors comptage) : 20 à 30 pages DocLayNet (récupérées légalement), jamais rattachées à une classe.

### 11.2 Part de chaque catégorie

| Mesure | Récupéré tel quel | Récupéré puis adapté | Généré |
|---|---|---|---|
| Documents du corpus (348) | 10, soit **≈ 2,9 %** | 0 (le texte récupéré est compté au §11.3) | 338, soit **≈ 97,1 %** |
| Gabarits (38) | 1, soit ≈ 2,6 % | 0 à 2, soit jusqu'à ≈ 5 % | 35 à 37 |
| Avec le stress (378 documents) | 12 à 13, soit ≈ 3,2 à 3,4 % | n/a | le reste |

**Lecture honnête** : la recherche légale ne remplace presque pas la génération. Environ **97 % du corpus est généré**. Sont récupérés légalement : un gabarit de facture, les textes des CGV, deux ou trois factures de stress et quelques pages de sondes. Avec FNFE-MPE, Kaggle, Roboflow, Typst et les procès-verbaux municipaux écartés, **l'économie de temps est marginale** : de l'ordre de **2 à 6 h** (un gabarit de facture, éventuellement un ou deux gabarits HTML/CSS adaptés, et la rédaction du corps des CGV). L'estimation du §7.1 reste donc valable telle quelle.

### 11.3 Règles d'attribution aux ensembles pour les éléments récupérés

Elles respectent la séparation par gabarit de [dataset-strategy.md](dataset-strategy.md).

| Élément | Ensemble | Règle |
|---|---|---|
| Factures Cabinet Digital (1 gabarit, 10 documents) | **train** (`facture`) | `gabarit_id` unique ; les 10 documents restent ensemble ; provenance `public`, note « fictif, non réel » ; licence CC BY 4.0 et lien enregistrés ; fichiers non committés. |
| Gabarits HTML/CSS MIT adaptés | décidé **avant toute expérience**, comme un gabarit écrit par nous | Un gabarit = un seul ensemble ; `auteur_gabarit` = `public_adapte` ; notice MIT conservée. |
| Corps de texte des `cgv_notice` (Open Terms Archive) | Un fournisseur = **un seul ensemble** | Les fournisseurs sont répartis en trois pools disjoints (train, val, test) **avant** la génération : 8 fournisseurs par ensemble pour 3 gabarits × 8 documents. Aucun texte d'un fournisseur ne passe d'un ensemble à l'autre, y compris ses versions successives. Provenance `public` + texte récupéré ; ODbL et attribution notées. |
| Factures FATURA (2 à 3) | **stress** | Un gabarit FATURA par document ; aucun gabarit de stress n'est utilisé ailleurs. |
| Pages DocLayNet | Sondes (hors métriques de classes) | Jamais en entraînement. |

### 11.4 Ce qu'il reste à faire avant toute génération

1. Lire le fichier LICENSE de chaque candidat HTML/CSS et décider lesquels sont réellement distincts de nos gabarits (§2.6).
2. Relire la licence de FATURA, de Cabinet Digital, d'Open Terms Archive et de DocLayNet **sur la source primaire au moment du téléchargement**, avec capture dans le journal des licences.
3. **Option en parallèle** : demander un accord écrit au FNFE-MPE pour l'usage académique de ses exemples. Le projet n'en dépend pas.
4. Ouvrir manuellement (navigateur) les projets Roboflow si un membre souhaite lever l'incertitude ; sinon, les fiches de paie restent entièrement générées.

## Sources consultées

- FATURA, Zenodo v2 : <https://zenodo.org/records/10371464> (licence CC BY 4.0 lue sur la page) et v1 : <https://zenodo.org/record/8261508>. Article : <https://ar5iv.labs.arxiv.org/html/2311.11856> (un agrégateur de l'article annonçait CC BY-NC-SA 4.0).
- CUAD : <https://huggingface.co/datasets/cuad/blame/main/README.md>, <https://arxiv.org/abs/2103.06268>.
- RVL-CDIP : <https://huggingface.co/datasets/chainyo/rvl-cdip/blob/main/README.md>.
- DocLayNet : <https://huggingface.co/datasets/ds4sd/DocLayNet/blob/main/README.md?code=true>.
- CORD : <https://github.com/clovaai/cord>.
- DocILE : <https://arxiv.org/abs/2302.05658v1> ; Kleister : <https://arxiv.org/abs/2003.02356>.
- Augraphy : <https://pypi.org/project/augraphy/>.
- Licence Ouverte 2.0 : <https://www.data.gouv.fr/pages/legal/licences/etalab-2.0>.
- Jeu DOPHIS : <https://www.data.gouv.fr/datasets/donnees-fictives-de-gestion-commerciale>.
- Export PDF de Playwright (Chromium seulement) : <https://www.checklyhq.com/docs/learn/playwright/generating-pdfs/>.
- Vérifications du 2026-11-24 : <https://fnfe-mpe.org/mentions-legales/> et <https://fnfe-mpe.org/factur-x/> (FNFE-MPE) ; <https://huggingface.co/datasets/Voxel51/high-quality-invoice-images-for-ocr> et <https://paperswithcode2.com/dataset/11840> (jeu Kaggle) ; pages Roboflow listées au §2.4 (HTTP 403 à la lecture automatique) ; <https://github.com/akretion/factur-x> (BSD) et <https://github.com/ZUGFeRD/mustangproject> (Apache-2.0) ; <https://www.cabinetdigital.fr/facture-electronique/exemples-de-factures/> ; <https://www.github.com/anvilco/html-pdf-invoice-template>.
