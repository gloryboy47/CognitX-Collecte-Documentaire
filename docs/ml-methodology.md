# Méthodologie Machine Learning

Protocole de la brique ML du sujet n°1. **Le détail des données (classes, volumes, annotation, génération, découpage, évaluation) est dans [dataset-strategy.md](dataset-strategy.md), qui fait foi en cas de différence.** Le cahier des charges demande une brique **utile, intégrée, évaluée et expliquée** (p.3), « entraînée sur des données et mesurée avec des métriques adaptées ». Ce document fixe la méthode. Les sections « À renseigner » se remplissent avec des résultats réels uniquement.

## 1. Problème et justification

Le sujet pose la question : *« Comment votre solution apprend-elle à reconnaître, vérifier et fiabiliser les documents déposés ? »* (p.4).

**Notre réponse** :
- **Reconnaître** : classer chaque document dans un type (facture, fiche de paie, contrat, compte-rendu R&D, autre) à partir de son texte OCR. C'est la brique entraînée.
- **Fiabiliser** : produire une confiance calibrée. Sous un seuil, le document va à un consultant au lieu d'être accepté ou refusé automatiquement. Le coût d'une erreur est élevé (p.4), donc la capacité à dire « je ne sais pas » fait partie du modèle.
- **Vérifier** : en grande partie par règles explicites ([validation](architecture.md)), car elles sont lisibles et auditables. Pas de ML là où une règle suffit.

**Classes** : `facture`, `fiche_de_paie`, `contrat`, `compte_rendu_rd` (les quatre types cités page 4) + `autre`. La classe `autre` est notre ajout : un client déposera des documents hors liste, le système doit pouvoir les reconnaître comme tels. À confirmer avec Leyton.

## 2. Données

### 2.1 Cadre imposé

« Données fictives ou anonymisées uniquement » (p.4 et p.12) et un dépôt qui contient `data/` « données fictives » (p.10). Il n'existe pas de jeu fourni : **l'équipe doit constituer son corpus**.

### 2.2 Provenance

Chaque document est déclaré dans `data/annotations/manifest.csv` avec une provenance :

| Valeur | Sens |
|---|---|
| `fictif_manuel` | Rédigé ou mis en forme à la main par un membre. |
| `fictif_genere` | Produit par un script de génération de l'équipe (le script est versionné). |
| `anonymise` | Document réel dont toutes les données personnelles ont été retirées. |
| `public` | Modèle ou exemple publiquement disponible, licence notée. |

**Aucun document fictif n'est présenté comme réel**, dans le dépôt, le rapport ou la démo. Aucun résultat n'est annoncé avant d'avoir été mesuré.

### 2.3 Risque propre à un corpus fictif

Si l'on génère les documents à partir de quelques gabarits, un modèle apprend les gabarits, pas les types de document, et ses scores sont trompeusement élevés. Mesures :
1. **Diversité** : plusieurs gabarits par classe, émetteurs, mises en page, qualités de scan, langues (français dominant) et bruits d'OCR réalistes.
2. **Découpage par gabarit** (voir 2.5) : un gabarit n'apparaît que dans un seul des trois jeux.
3. **Jeu de test « stress »** : quelques documents créés par un membre qui n'a pas participé à la création du corpus d'entraînement, avec des mises en page volontairement différentes. Il est rapporté séparément.
4. **Limites dites clairement** dans le rapport : les scores mesurent la généralisation à d'autres gabarits fictifs, pas à des dossiers réels.

### 2.4 Annotation

Une étiquette par document, définie par un guide d'annotation (critères de chaque classe, cas limites, règle pour `autre`). Un échantillon est annoté par deux personnes ; l'accord (kappa de Cohen) est calculé. Pour un corpus fictif, l'étiquette est connue à la création ; le guide sert alors surtout aux documents ambigus et à l'équipe de revue. Les corrections des consultants dans l'application peuvent enrichir le corpus.

### 2.5 Découpage

Train / validation / test, **stratifié par classe et groupé par gabarit (ou émetteur)**. Le test n'est utilisé qu'une fois, à la fin. Les hyperparamètres se règlent par validation croisée groupée sur le train. Les effectifs sont inconnus à ce stade : la taille du corpus conditionne la ligne « plus lourd que la baseline » (§4).

À renseigner : effectifs par classe, par provenance, par gabarit.

## 3. Préparation

1. Lecture : couche texte du PDF si présente, sinon Tesseract. On garde la confiance de lecture.
2. Nettoyage : normalisation Unicode, minuscules, suppression du bruit évident ; on conserve chiffres et symboles monétaires.
3. Features : TF-IDF sur mots et sur n-grammes de caractères (robustes aux fautes d'OCR) ; indices simples (longueur, densité de chiffres, présence de montants, nombre de pages).
4. Tout est dans un `Pipeline` ajusté sur le train seul, pour éviter les fuites.

## 4. Algorithmes

Progression : chaque palier doit gagner sur la validation pour justifier le suivant.

| Palier | Modèle | Rôle |
|---|---|---|
| 0 | Classe majoritaire | Plancher à battre |
| 1 | TF-IDF + régression logistique | Baseline forte, interprétable |
| 2 | SVM linéaire, Naive Bayes complémentaire, forêt aléatoire (éventuellement XGBoost) | Comparaison d'algorithmes |
| 3 (optionnel) | Modèle de langue pré-entraîné adapté (fine-tuning) | Seulement si le corpus est assez riche et si l'équipe sait l'expliquer et l'héberger |

Un modèle pré-entraîné de palier 3 serait un point de départ de fine-tuning, entraîné et évalué par nous. Ce n'est pas un appel d'API.

À renseigner : tableau comparatif et choix final justifié.

## 5. Entraînement

- Configuration en YAML (`src/ml/configs/`), graine fixe, versions des dépendances notées.
- Déséquilibre : poids de classe avant tout rééchantillonnage.
- Calibration des probabilités (Platt ou isotonique), puis choix du seuil de confiance.
- Chaque exécution produit un fichier de résultats dans `reports/` (configuration, métriques, empreinte du corpus). Pas d'outil de suivi dédié au départ.
- Artefact : modèle, vectoriseur, liste de classes, métriques et manifeste, dans `src/ml/artifacts/`. Le backend refuse un artefact sans manifeste.

## 6. Évaluation

Sur le jeu de test, et séparément sur le jeu « stress » :
- exactitude, précision, rappel et F1 par classe, **F1 macro** comme métrique principale ;
- matrice de confusion et analyse des erreurs ;
- **courbe couverture / précision** selon le seuil : quelle part des documents est traitée sans consultant pour une précision cible. C'est la métrique qui relie le modèle au besoin (« une erreur coûte cher ») ;
- calibration (courbe de fiabilité, score de Brier) ;
- ablation des features, et performance selon la qualité de lecture.

**Critères d'acceptation** : à fixer après la mesure de la baseline, avec l'encadrement.

## 7. Limites à documenter

À renseigner à partir des résultats : taille et diversité du corpus fictif, dépendance à l'OCR, langues couvertes, comportement hors taxonomie, absence de validation sur des dossiers réels.

## 8. Livrables ML

- Code reproductible et configurations.
- Fiche de données (provenance, effectifs, annotation) et fiche modèle dans `reports/`.
- Rapport d'évaluation, figures incluses.
- Artefact consommé par le backend, **intégré au parcours** (exigence « intégrée au cœur de la solution », p.3).
