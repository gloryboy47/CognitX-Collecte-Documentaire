# Stratégie de données et d'évaluation

> Statut : **stratégie, révision 2** (revue de faisabilité et de cohérence). À valider par l'équipe avant toute génération. La révision 2 corrige la présentation des effectifs (§2.0), ajoute un **plan minimal** recommandé (§2.2 à §2.5) et une stratégie de **détection de documents inconnus** (§7.8). Aucun document n'a été produit, aucun modèle entraîné : **ce document ne contient aucun résultat expérimental**. Toute phrase du type « on s'attend à… » est une hypothèse à tester, et elle est signalée comme telle.
>
> Cadre officiel (cahier des charges ESISA × Leyton, p.4 et p.12) : documents **fictifs ou anonymisés uniquement**, brique ML « entraînée sur des données et mesurée avec des métriques adaptées », parcours simple de bout en bout d'abord. Voir [requirements-analysis.md](requirements-analysis.md).

## 0. Le principe qui structure tout

Dans un corpus fictif, **ce qui compte n'est pas le nombre de fichiers, c'est le nombre de gabarits indépendants**. Un script peut produire 10 000 factures en une minute, mais si elles viennent de 3 gabarits, le modèle apprend à reconnaître 3 gabarits et le score annoncé n'a aucun sens. Toute la stratégie en découle :

1. la **diversité** se planifie (gabarits, mises en page, auteurs, entités, thèmes) ;
2. le **découpage** se fait par gabarit, pas par fichier ;
3. l'**honnêteté** de l'évaluation vient d'un jeu « stress » conçu hors du générateur ;
4. les **limites** (corpus fictif, petit) sont écrites noir sur blanc dans le rapport.

## 1. Classes documentaires

### 1.1 Décision

Cinq classes. Quatre viennent du sujet (p.4) ; la cinquième est un ajout justifié par le fonctionnement réel d'une dropzone.

| Classe | Définition opérationnelle | Indices attendus (non exhaustifs) |
|---|---|---|
| `facture` | Demande de paiement émise par un fournisseur pour des biens ou services livrés. | N° de facture, date, émetteur et destinataire, lignes de prestation, HT / TVA / TTC, échéance, coordonnées bancaires. |
| `fiche_de_paie` | Bulletin de salaire d'un salarié pour une période. | Employeur, salarié, période, brut, cotisations, net à payer, congés, cumuls. |
| `contrat` | Accord écrit engageant des parties. Sous-types retenus : prestation / sous-traitance, travail, collaboration de recherche. | Parties, objet, articles numérotés, durée, prix, résiliation, loi applicable, signatures. |
| `compte_rendu_rd` | Compte-rendu ou suivi d'une activité de R&D : réunion de projet, avancement, suivi d'essais. | Date, participants, ordre du jour, travaux réalisés, verrous / incertitudes techniques, résultats, prochaines étapes. |
| `autre` | Tout document **qui n'est pas** l'une des quatre classes, y compris les voisins trompeurs. | Voir 1.2. |

**Pourquoi `autre` ?** Un client déposera un jour un devis à la place d'une facture, ou le mauvais PDF. Sans classe de rejet, le modèle classera de force dans une des quatre classes et validera à tort, ce qui est précisément l'erreur coûteuse que le sujet signale (p.4). **À valider avec Leyton** (question Q3 de la précédente analyse).

### 1.2 Contenu de `autre` : des voisins trompeurs, pas du bruit

Si `autre` ne contenait que des documents évidemment différents (recette de cuisine, page blanche), le modèle réussirait sans rien prouver. `autre` est donc composé de **hard negatives** qui ressemblent à une classe cible :

| Sous-type de `autre` | Confondable avec | Différence réelle |
|---|---|---|
| `devis` | `facture` | Même structure, mais proposition commerciale, pas une demande de paiement. |
| `bon_commande` | `facture` | Mêmes lignes et montants ; c'est un engagement d'achat. |
| `releve_bancaire` | `facture`, `fiche_de_paie` | Tableaux de montants et de dates ; pas de prestation ni de salaire. |
| `courrier_administratif` | `contrat`, `fiche_de_paie` | Attestations, courriers : texte formel, parties, mais pas d'engagement contractuel. |
| `compte_rendu_non_rd` | `compte_rendu_rd` | Réunion commerciale, RH, copropriété : même forme, mais sans activité de R&D. |
| `cgv_notice` | `contrat` | Articles juridiques numérotés, mais sans parties identifiées ni objet précis. |
| `attestation_emploi` *(sous-type réservé au test)* | `fiche_de_paie`, `contrat` | Voir 1.3. |

Le **plan minimal recommandé (§2.2)** retient quatre de ces sous-types : `devis`, `compte_rendu_non_rd`, `cgv_notice`, `releve_bancaire`. Le plan complet (§2.1) en retient cinq : `devis`, `bon_commande`, `releve_bancaire`, `courrier_administratif`, `compte_rendu_non_rd` (sans `cgv_notice`). Les deux plans ne couvrent donc pas exactement les mêmes confusions : le minimal garde `cgv_notice` (contrat), car `contrat` n'aurait sinon aucun voisin trompeur.

### 1.3 Documents inconnus : un problème distinct de la classification

`attestation_emploi` n'apparaît **jamais** dans le train ni la validation. Ce n'est pas parce que `autre` existe que le système reconnaîtra ce type comme inconnu : un classifieur entraîné sur cinq classes range par construction tout document dans l'une d'elles, souvent avec une confiance élevée. `autre` apprend à rejeter **les négatifs vus**, pas les types jamais vus. La détection de documents inconnus est donc traitée comme une fonction à part entière, avec ses propres mécanismes et sa propre évaluation, **sans garantie** : voir §7.8.

### 1.4 Ce qui n'est pas une classe

- **Illisible / vide / trop dégradé** : ce n'est pas un type de document, c'est un problème de lecture. Il est traité en amont par un **contrôle de qualité de lecture** (confiance OCR, longueur du texte) qui envoie le document en `A_REVOIR`, sans passer par le classifieur. Il est évalué à part (§7).
- **Avoir, relevé de TVA, fiche de poste, PDF multi-documents** : hors périmètre v1. Un avoir ressemble beaucoup à une facture : décision métier à demander (Q ci-dessous), et non à deviner. Un fichier contenant plusieurs documents est un cas connu non traité ; il est déclaré comme limite.
- **Langue** : v1 en **français uniquement**. Un petit lot en anglais sert de sonde hors distribution dans le jeu stress. Si Leyton attend de l'anglais en production, il faudra des gabarits dédiés dans chaque jeu.

## 2. Volume, faisabilité et recommandation

### 2.0 Composition exacte des effectifs

Les cinq classes ne sont pas construites de la même façon, d'où l'écart avec le produit 5 × 8 × 15 = 600.

- **4 classes principales** (`facture`, `fiche_de_paie`, `contrat`, `compte_rendu_rd`) : même plan pour chacune.
- **`autre` « vue »** : ce n'est pas un type de document mais un ensemble de sous-types. Ses gabarits se comptent **par sous-type**, pas par classe.
- **`autre` « inconnue »** : sous-type réservé au test (§7.8).
- **Jeu stress** : documents conçus à la main, hors du générateur. Ils ne comptent pas dans les gabarits générés.

Les totaux ci-dessous sont des sommes de lignes, pas des estimations.

### 2.1 Plan complet

| Classe | Gabarits (train / val / test) | Documents / gabarit | Docs train | Docs val | Docs test | Total |
|---|---|---|---|---|---|---|
| `facture` | **8** (4 / 2 / 2) | 15 | 60 | 30 | 30 | 120 |
| `fiche_de_paie` | **8** (4 / 2 / 2) | 15 | 60 | 30 | 30 | 120 |
| `contrat` | **8** (4 / 2 / 2) | 15 | 60 | 30 | 30 | 120 |
| `compte_rendu_rd` | **8** (4 / 2 / 2) | 15 | 60 | 30 | 30 | 120 |
| `autre` vue : 5 sous-types (devis, bon de commande, relevé bancaire, courrier administratif, CR non R&D) | **20** = 5 × 4 (2 / 1 / 1 par sous-type) | 8 | 80 | 40 | 40 | 160 |
| `autre` inconnue : `attestation_emploi` | **2** (0 / 0 / 2) | 8 | 0 | 0 | 16 | 16 |
| **Corpus généré** | **54** | | **320** | **160** | **176** | **656** |
| Jeu stress (hors générateur) | ≈ 40 conceptions individuelles | 1 | 0 | 0 | 40 (stress) | 40 |
| **Total** | | | | | | **696** |

Vérification : 4 × 8 + 5 × 4 + 2 = 54 gabarits ; 4 × 120 + 160 + 16 = 656 documents ; 656 + 40 = 696.

### 2.2 Plan minimal

Principe : **ne rien retirer à la rigueur, retirer du volume**. On garde, pour chaque classe principale, des gabarits de test indépendants (2), un jeu stress, la validation croisée groupée et la baseline à règles. On réduit le nombre de gabarits d'entraînement, le nombre de documents par gabarit et la couverture de `autre`.

| Classe | Gabarits (train / val / test) | Documents / gabarit | Docs train | Docs val | Docs test | Total |
|---|---|---|---|---|---|---|
| `facture` | **6** (3 / 1 / 2) | 10 | 30 | 10 | 20 | 60 |
| `fiche_de_paie` | **6** (3 / 1 / 2) | 10 | 30 | 10 | 20 | 60 |
| `contrat` | **6** (3 / 1 / 2) | 10 | 30 | 10 | 20 | 60 |
| `compte_rendu_rd` | **6** (3 / 1 / 2) | 10 | 30 | 10 | 20 | 60 |
| `autre` vue : 4 sous-types (devis, CR non R&D, CGV/notice, relevé bancaire) | **12** = 4 × 3 (1 / 1 / 1 par sous-type) | 8 | 32 | 32 | 32 | 96 |
| `autre` inconnue : `attestation_emploi` | **2** (0 / 0 / 2) | 6 | 0 | 0 | 12 | 12 |
| **Corpus généré** | **38** | | **152** | **72** | **124** | **348** |
| Jeu stress (hors générateur) | ≈ 30 conceptions individuelles (20 classes principales + 10 `autre`, dont 5 de types inconnus) | 1 | 0 | 0 | 30 (stress) | 30 |
| **Total** | | | | | | **378** |

Vérification : 4 × 6 + 4 × 3 + 2 = 38 gabarits ; 4 × 60 + 96 + 12 = 348 documents ; 348 + 30 = 378.

Choix de ce plan :
- **6 gabarits par classe principale** : 3 en train, 1 en validation, **2 en test**. Les 4 gabarits de développement (train + val) servent à une **validation croisée « un gabarit retenu à la fois »** (4 plis) pour choisir le modèle, au lieu de décider sur un seul gabarit de validation.
- **4 sous-types de `autre` plutôt que 5**, choisis pour couvrir **la confusion probable de chaque classe principale** : devis ↔ facture, CR non R&D ↔ CR R&D, CGV ↔ contrat, relevé ↔ fiche de paie. Chaque sous-type est vu avec un gabarit en train et testé avec un autre gabarit.
- **Test inchangé en rigueur** : 2 gabarits indépendants par classe principale, comme dans le plan complet.

### 2.3 Comparaison des deux plans

Hypothèses d'estimation (à confirmer sur les deux premiers gabarits réalisés) : gabarit principal de 1,5 à 2,5 h (conception, champs, variantes, vérification, débogage) ; gabarit `autre` de 0,75 à 1,25 h ; gabarit inconnu de 1 à 1,5 h ; document de stress ≈ 25 à 30 min.

| Poste (heures) | Plan complet | Plan minimal | Remarque |
|---|---|---|---|
| Gabarits classes principales | 32 × (1,5 à 2,5) = 48 à 80 | 24 × (1,5 à 2,5) = 36 à 60 | |
| Gabarits `autre` vue | 20 × (0,75 à 1,25) = 15 à 25 | 12 × (0,75 à 1,25) = 9 à 15 | |
| Gabarits inconnus | 2 × (1 à 1,5) = 2 à 3 | 2 × (1 à 1,5) = 2 à 3 | |
| Infrastructure : générateur, entités, dégradations, manifeste, vérité terrain | 25 à 40 | 25 à 40 | **Incompressible** : identique |
| Scripts : découpage, contrôle de fuite, contrôles d'artefacts | 8 à 12 | 8 à 12 | Incompressible |
| Jeu stress | 40 × (0,4 à 0,5) = 16 à 20 | 30 × (0,4 à 0,5) = 12 à 15 | Porté par un membre indépendant |
| Contrôle qualité (10 % relu) | 8 à 12 | 5 à 8 | |
| **Total** | **≈ 122 à 192 h** | **≈ 97 à 153 h** | Écart ≈ 25 à 40 h (≈ 20 %) |

Correction : la version précédente annonçait « 54 gabarits ≈ 80 h ». Avec les hypothèses de gabarit ci-dessus, les gabarits seuls représentent 65 à 108 h dans le plan complet. L'ancien chiffre était trop bas et non étayé.

Charge par personne (corpus seulement, sans backend, frontend ni modèle) :

| Équipe | Plan complet | Plan minimal |
|---|---|---|
| 3 étudiants | 41 à 64 h chacun | 32 à 51 h chacun |
| 4 étudiants | 31 à 48 h chacun | 24 à 38 h chacun |
| 5 étudiants | 24 à 38 h chacun | 19 à 31 h chacun |

**Le gain du plan minimal est modeste (≈ 20 %)** parce que le générateur et les scripts coûtent autant dans les deux cas. Le vrai levier est l'**ordre de livraison** (§2.4) : chaque palier donne un corpus valide.

| | Plan complet | Plan minimal |
|---|---|---|
| **Responsabilités** (4 membres) | R1 : génération et scripts (responsable des données). R2 : gabarits `facture`, `fiche_de_paie`. R3 : gabarits `contrat`, `compte_rendu_rd`. R4 : `autre` et contrôle qualité. **Un membre indépendant** conçoit le stress : il ne réalise aucun gabarit de développement, donc en pratique un cinquième rôle. | Même répartition, charges plus légères. À **3 membres** : deux se partagent les gabarits, le troisième porte le stress puis le contrôle qualité. À **5** : un membre dédié à `autre` et au contrôle qualité. |
| **Risque calendrier** | **Élevé** : 120 à 190 h en parallèle du backend, du frontend et du modèle ; le parcours de bout en bout prend du retard. | **Modéré** : tient en deux semaines à 4 membres si l'infrastructure est prête à la fin de la semaine 1. |
| **Risque scientifique** | Test à 2 gabarits par classe, intervalles larges ; entraînement plus diversifié (4 gabarits par classe). | **Même test**, entraînement plus pauvre (3 gabarits par classe) : généralisation potentiellement plus basse et plus variable. C'est un résultat à rapporter, pas un défaut du protocole. |
| **Risque de qualité** | Fatigue : les derniers gabarits sont bâclés, donc moins variés. | Moins de gabarits donc plus de soin ; moins de redondance si l'un est raté. |
| **Couverture de `autre`** | 5 sous-types vus + 1 inconnu | 4 sous-types vus + 1 inconnu ; moins de confusions couvertes |
| **Détection d'inconnus** | 6 types évaluables (5 simulés + 1 en test) | 5 types (4 simulés + 1 en test), plus 5 types dans le stress |

### 2.4 Livraison par vagues

**Chaque vague produit un corpus utilisable, et le test est figé dès la vague 1.**

| Vague | Quand | Contenu | Règle |
|---|---|---|---|
| 0 | fin de la semaine 1 | Infrastructure prête et **2 gabarits par classe principale, 1 par sous-type de `autre`, 8 documents par gabarit** : suffit pour construire le parcours de bout en bout. | Aucun score publié : effectifs trop faibles. |
| 1 | fin de la semaine 2 | **Plan minimal complet** (§2.2), test et stress figés. | Découpage verrouillé ; `splits.csv` versionné. |
| 2 | semaines 4 à 5, **si le calendrier le permet** | Gabarits supplémentaires versés **uniquement en train et validation** (jusqu'à 4 train + 2 val par classe principale, 5e sous-type de `autre`). | **Le test de la vague 1 ne bouge pas.** |

Intérêt scientifique de la vague 2 : elle fournit la **courbe d'apprentissage selon le nombre de gabarits** (expérience E4) comme sous-produit.

En cas de retard, on réduit dans cet ordre : (1) les documents par gabarit ; (2) les gabarits de la vague 2 ; (3) un sous-type de `autre` ; (4) la sévérité des dégradations de niveau 2. **On ne réduit jamais** : les 2 gabarits de test par classe principale, le jeu stress, la séparation par gabarit.

### 2.5 Recommandation

**Plan minimal, en vagues, avec extension possible.** Le plan complet n'est pas compatible avec 9 semaines, une équipe de 3 à 5 et un prototype à livrer en parallèle ; son avantage principal (4 gabarits d'entraînement par classe au lieu de 3) est récupérable en vague 2 sans toucher au test.

**Conservé** : séparation par gabarit, entités et domaines disjoints, 2 gabarits de test indépendants par classe principale, jeu stress indépendant, validation croisée groupée, F1 macro, baseline à règles, évaluation séparée des inconnus.

**Coût** : corpus plus petit, intervalles plus larges, entraînement avec 3 gabarits par classe, couverture de `autre` réduite. Ces limites seront écrites dans le rapport.

### 2.6 Limite statistique à assumer

Le test minimal compte 20 documents par classe principale, soit **2 gabarits** : une erreur change le rappel de 5 points, et l'intervalle par « bootstrap sur les gabarits » avec 2 gabarits est **peu informatif**. On le publie avec cette réserve, et on complète par :
1. la **dispersion par gabarit** (score de chaque gabarit de test et de chaque pli de validation croisée : minimum, médiane, maximum) pour repérer un gabarit catastrophique caché par une moyenne ;
2. le jeu stress, indépendant ;
3. des conclusions prudentes : tant que les intervalles se recouvrent, on ne classe pas les modèles.

## 3. Schéma d'annotation

Trois niveaux, du plus indispensable au plus accessoire.

### 3.1 `data/annotations/manifest.csv`, une ligne par document

| Colonne | Valeurs | Rôle |
|---|---|---|
| `doc_id` | identifiant opaque (ex. `d00417`) | Nom de fichier aussi. **Jamais** de nom parlant : le modèle ne doit pas voir la classe dans le chemin. |
| `sha256` | empreinte du fichier | Intégrité, détection de doublons exacts. |
| `classe` | `facture` · `fiche_de_paie` · `contrat` · `compte_rendu_rd` · `autre` | Étiquette cible. |
| `sous_type` | ex. `devis`, `prestation`, `reunion` | Analyse fine des erreurs, composition de `autre`. |
| `provenance` | `fictif_genere` · `fictif_manuel` · `anonymise` · `public` | Obligatoire (règle du projet). |
| `gabarit_id` | ex. `fac_t05` | **Clé de groupe du découpage.** |
| `auteur_gabarit` | initiales | Hétérogénéité de style ; pas d'effet sur le découpage. |
| `pool_entites` | `A` · `B` · `C` | Pool de noms fictifs (§5.3). Un pool = un ensemble de découpage. |
| `domaine_rd` | ex. `chimie`, `logiciel`, `mecanique` (seulement `compte_rendu_rd`, `contrat` de collaboration) | Découpage par thème (§5.3). |
| `jeu` | `dev` · `test` · `stress` | Appartenance. |
| `split` | `train` · `val` · `test` · `stress` | Dérivé du gabarit, fixé par script. |
| `langue` | `fr` (`en` seulement en stress) | |
| `format_source` | `pdf_natif` · `pdf_scan` · `image` · `photo` | Le texte vient de la couche texte ou de l'OCR. |
| `niveau_degradation` | `0` propre · `1` modéré · `2` sévère | Découpes d'évaluation. |
| `degradations` | liste (`rotation:+3.2`, `flou`, `jpeg:35`, `dpi:110`, `bruit`, `coupe`…) | Reproductibilité et analyse d'échec. |
| `nb_pages` | entier | |
| `completude` | `complet` · `partiel` · `champs_manquants` | Voir 3.2. |
| `paire_trompeuse_id` | identifiant du document quasi-jumeau d'une autre classe | Évalue les confusions voisines. |
| `source_texte` | `ecrit_equipe` · `assemble_regles` · `brouillon_llm_relu` | Traçabilité du texte libre (§5.4). |
| `seed_generation` | entier | Reproduire le document à l'identique. |
| `licence` | texte, pour `public` | |
| `annotateur_1` / `annotateur_2` / `classe_2` | | Double annotation (§3.4). |
| `ocr_moteur` / `ocr_version` / `ocr_conf_moyenne` | | Un changement de moteur impose de recalculer `interim/`. |
| `notes` | texte libre | Cas litigieux. |

### 3.2 `data/annotations/verite_terrain.jsonl`, une ligne par document

Pour les documents générés, **la vérité est gratuite** puisque le générateur connaît les valeurs qu'il a écrites. On la conserve :

- `texte_reference` : texte exact tel que généré, avant dégradation. Permet de mesurer l'erreur de l'OCR **séparément** de l'erreur du classifieur : sans cela, on ne sait pas qui est responsable d'une erreur.
- `champs` : valeurs vraies des champs clés (date, montant TTC, émetteur, numéro, période…). Sert à évaluer l'extraction par règles et à tester la logique de validation.
- `defauts_conformite` : liste des défauts volontairement introduits (`date_absente`, `montant_incoherent` pour un HT + TVA ≠ TTC, `signature_absente`, `periode_absente`, `piece_expiree`). **Cette annotation n'est pas une cible du classifieur** : elle alimente le module de règles de validation et son jeu de tests. Elle ne doit pas être confondue avec la classe.

L'entrée du classifieur est le **texte lu par le pipeline** (couche texte ou OCR), pas `texte_reference`.

### 3.3 `data/annotations/splits.csv`

`doc_id, split, fold` : généré par script depuis le manifeste, déterministe et versionné. Voir §6.

### 3.4 Qualité des étiquettes

- Pour les documents générés, l'étiquette est déterministe : **un coefficient d'accord entre annotateurs n'a pas de sens** et on ne l'annonce pas.
- Le coefficient de Cohen est calculé sur ce qui est annoté par des humains : le jeu stress, les documents `fictif_manuel`, `public` et `anonymise`, annotés par deux personnes indépendamment.
- Un **contrôle visuel de 10 % du corpus généré**, tiré au hasard par classe et par niveau de dégradation, vérifie que les documents ressemblent à ce qu'ils prétendent être.
- Une relecture par un consultant Leyton de quelques documents (réalisme, et pertinence de nos pièces) est à demander : si elle est refusée, le rapport le dit.

## 4. Informations utiles aux caractéristiques (features)

Ce qui entre dans le modèle, par priorité :

| Famille | Contenu | Remarque |
|---|---|---|
| Texte (cœur) | TF-IDF de mots (1-2 grammes) et de **n-grammes de caractères** (2-5) | Les n-grammes de caractères résistent aux fautes d'OCR. |
| Structure simple | nombre de pages, longueur du texte, densité de chiffres, nombre de montants, de dates, d'ancres comme « € », « % », « Article » | Peu coûteux. À tester en ablation. |
| Qualité de lecture | confiance OCR moyenne, ratio de caractères non alphanumériques | Sert aussi au contrôle qualité en amont. |
| Mise en page (extension) | position et alignement des blocs fournis par l'OCR | Seulement si les erreurs de la baseline s'expliquent par la mise en page. |

Exclus : le nom de fichier, les métadonnées PDF (outil producteur, date de création), la taille du fichier, la résolution. Ce sont des **artefacts du générateur** qui trahiraient la classe sans rien dire du document (§8). Le pipeline d'entrée les supprime ou les normalise.

## 5. Stratégie de génération

### 5.1 Chaîne de production

```
entités fictives ──► contenu structuré ──► rendu du gabarit ──► dégradation ──► lecture (OCR / texte)
 (pools disjoints)   (champs, lignes,     (HTML/CSS → PDF,       (scan, rotation,   texte du pipeline
                      texte libre)         ou fichier manuel)     bruit, coupe…)     + confiance
                              │                                                          │
                              └──► vérité terrain (champs, texte de référence, défauts)  └──► manifeste
```

Un seul script versionné, piloté par une graine, à l'emplacement `src/datagen/` (à créer au démarrage de la génération, pas maintenant). Le même document régénéré à partir de sa graine est identique.

### 5.2 Sources de diversité des gabarits

Un gabarit est défini par un **ensemble de choix de conception**, pas par un simple changement de couleur. Les gabarits d'une même classe doivent différer sur plusieurs de ces axes :

| Axe | Variations |
|---|---|
| Structure | 1 ou 2 colonnes, en-tête en haut / en bandeau latéral / absent, pied de page légal ou non, 1 à 3 pages |
| Ordre des blocs | émetteur avant ou après destinataire, totaux en bas ou en encadré, parties du contrat en tête ou en fin |
| Tableaux | avec bordures, sans bordure, rayés, colonnes différentes (désignation, quantité, PU, TVA), ou lignes de texte libre |
| Typographie | 4 à 6 familles libres de droit, tailles et interlignages différents |
| Formules | « Facture », « Facture n° », « Note d'honoraires », « Relevé de prestations » ; « Bulletin de paie », « Fiche de salaire » ; « Contrat de… », « Convention de… » ; « Compte-rendu », « Point d'avancement », « Cahier de suivi » |
| Formats | dates (`12/03/2026`, `12 mars 2026`, `2026-03-12`), nombres (`1 234,56 €`, `1234.56 EUR`), devises |
| Éléments graphiques | logos fictifs (formes générées), tampons, filigranes, signatures manuscrites simulées |
| Exhaustivité | champs optionnels présents ou non, texte libre court ou long |
| Format du fichier | PDF natif avec couche texte, PDF d'image, JPEG/PNG, photo |

**Trois origines de gabarits**, pour éviter une unique « patte » du générateur :
1. gabarits HTML/CSS écrits par l'équipe (≈ 60 %) ;
2. gabarits repris de **modèles publics sous licence libre** (traitements Word / LibreOffice, licence notée dans `licence`) remplis avec des données fictives (≈ 25 %) ;
3. documents composés à la main dans un traitement de texte par un autre membre (≈ 15 %).

Si Leyton fournit des pièces **anonymisées** ou des maquettes, elles vont en **test uniquement** (le plus proche du réel que l'on aura), jamais en entraînement tant qu'on n'a pas décidé de les y verser pour un second modèle.

### 5.3 Entités fictives : jamais de personnes ni d'entreprises réelles

- Noms, prénoms, adresses : générateur de données françaises (type Faker `fr_FR`) complété par des listes à nous. Les noms d'entreprises sont **inventés puis recherchés une fois** pour vérifier qu'ils ne désignent pas une société existante.
- Identifiants (SIREN, TVA, IBAN) produits avec des **sommes de contrôle volontairement invalides** : ils ne peuvent pas correspondre à une entité réelle. Courriels sur un domaine réservé (`example.org`) ; téléphones dans les plages réservées à la fiction (à vérifier auprès de l'ARCEP avant usage).
- **Pools disjoints par ensemble de découpage** : l'ensemble des noms d'entreprises et de personnes est partitionné en trois pools, A (train), B (val), C (test), avant toute génération. Un nom donné n'apparaît que dans un ensemble. Sans cela, le modèle mémoriserait « Dubois Conseil → facture ».
- **Thèmes R&D** : une dizaine de domaines (chimie, logiciel, mécanique, matériaux, agronomie, énergie, électronique, santé…) répartis entre train, val et test. Un `compte_rendu_rd` de test porte sur un domaine non vu pendant l'entraînement : c'est un test de généralisation sur le vocabulaire, plus exigeant que la répartition aléatoire (limite assumée : plus dur qu'un cas réel où les domaines se recoupent).
- Les logos, tampons et signatures sont produits ou dessinés par l'équipe.

### 5.4 Texte libre : le point faible des corpus synthétiques

Les `compte_rendu_rd` et le corps des `contrat` sont des textes libres. Un assemblage de phrases à trous produit des textes très homogènes que le modèle apprend par cœur. Règles :

1. Les **blocs de texte** sont écrits par l'équipe (≥ 40 paragraphes de comptes-rendus par domaine, plusieurs clauses par type de contrat), puis **recombinés** avec variations d'ordre, de longueur et d'omission.
2. Un **brouillon assisté par un modèle de langage** est permis pour élargir les formulations (l'IA générative est autorisée comme outil, à déclarer, p.12). Il est **relu et corrigé par un membre**, déclaré dans [declaration-ia.md](declaration-ia.md) et tracé par `source_texte`. Cela ne remet pas en cause le classifieur, qui reste entraîné par nous : seul le contenu de test est généré.
3. Risque propre au brouillon assisté : un style homogène et « propre » commun à toutes les classes, ou au contraire une signature de style liée à une classe. On vérifie avec l'ablation « texte écrit par l'équipe seulement » (§7.5).
4. Le jeu stress contient du texte **écrit à la main par un membre indépendant**, sans réemploi des blocs.

### 5.5 Dégradations : recréer le monde réel

Appliquées **après** le rendu, sur le fichier final, avec un niveau tiré par document :

| Niveau | Part visée | Contenu |
|---|---|---|
| 0 | ≈ 35 % | PDF natif, couche texte exacte. |
| 1 | ≈ 40 % | Scan correct : rotation ±1-3°, bruit léger, JPEG moyen, 200 dpi. |
| 2 | ≈ 25 % | Scan difficile : rotation jusqu'à ±7°, flou, faible contraste, 100-150 dpi, ombres, plis, taches, tampon qui recouvre du texte, légère perspective type photo. |

Cas difficiles prévus en plus (§7.4), tous produits à partir d'un document existant sans en dupliquer le contenu :
- **Texte incomplet** : bas de page coupé, dernière page manquante, marge rognée, paragraphe masqué.
- **Informations manquantes** : champs clés absents (mais type reconnaissable).
- **Documents quasi-jumeaux** : paires facture / devis, CR R&D / CR non R&D avec peu de mots de différence.
- **Page quasi vide** (en-tête seul) : on vérifie que le contrôle qualité les arrête au lieu de les classer au hasard.
- **Pages parasites** : page de garde, page blanche en tête.
- **Rotation 90° ou 180°** (rare) : le pipeline doit détecter l'orientation avant lecture, sinon le texte est du bruit.

On utilise une bibliothèque de dégradation de documents (par ex. Augraphy) ou un script simple avec Pillow/OpenCV. Le choix se fait après un essai de 2 h sur trois documents.

### 5.6 Proportion de documents difficiles

Chaque ensemble (train, val, test) contient les trois niveaux de dégradation **dans les mêmes proportions**. Le test n'est pas plus facile que le train. Les cas difficiles de 5.5 représentent **≈ 15 % de chaque ensemble**, jamais plus d'un seul défaut par document pour garder l'analyse lisible, sauf dans le jeu stress.

### 5.7 Outils (sous réserve d'un essai)

Rendu : gabarits HTML/CSS avec Jinja2, convertis en PDF par un navigateur sans interface (Playwright / Chromium). Cette voie évite les dépendances système lourdes de certains moteurs de rendu sous Windows. À valider par un test d'une heure avant d'engager l'équipe. OCR : Tesseract `fra`, version et paramètres figés dans le manifeste.

## 6. Protocole Train / Validation / Test

### 6.1 Règles

```
              ┌─────────────── DEV ───────────────┐      ┌── TEST ──┐    ┌─ STRESS ─┐
              │   TRAIN          │   VALIDATION    │      │  jamais  │    │ hors     │
              │ gabarits train   │ gabarits val    │      │ vu avant │    │ générateur│
              │ pool A           │ pool B          │      │ pool C   │    │ 1 membre │
              └──────────────────┴─────────────────┘      └──────────┘    └──────────┘
                      │                                         ▲
                      └── sélection du modèle : CV groupée ─────┘ (test évalué UNE fois)
```

1. **Unité de groupe : le gabarit.** Tous les documents d'un gabarit, de n'importe quel niveau de dégradation, vivent dans le même ensemble.
2. **Pools d'entités disjoints** (A, B, C) et **domaines R&D disjoints** (§5.3).
3. **Stratification** par classe et par niveau de dégradation à l'intérieur des contraintes ci-dessus.
4. **Le découpage est fixé avant tout entraînement**, par script depuis le manifeste, avec une graine ; `splits.csv` est versionné. Il ne bouge plus.
5. **Sélection de modèle et d'hyperparamètres** : validation croisée **groupée par gabarit** (`StratifiedGroupKFold`) sur train + val, soit les **4 gabarits de développement par classe principale dans le plan minimal** (6 dans le plan complet). Un pli retient un gabarit par classe principale ; les scores de validation sont les scores hors pli. Le découpage fixe train / val sert à itérer vite ; la validation croisée sert à décider.
6. **Prétraitement appris sur le train du pli uniquement** : vocabulaire, IDF, normalisation, seuils. Aucun ajustement sur l'ensemble du corpus.
7. **Calibration et seuil de confiance** choisis sur les prédictions hors pli, **jamais sur le test**.
8. **Modèle final** : ré-entraîné sur train + val avec les hyperparamètres choisis, puis évalué **une seule fois** sur le test. Le résultat est rapporté quel qu'il soit. Pas de « je corrige un détail et je relance ».
9. **Jeu stress** : conçu par un membre qui n'a pas participé à la création des gabarits de dev, avec d'autres outils et d'autres mises en page, et dont le contenu n'est connu que de lui jusqu'à l'évaluation finale. Il n'est pas utilisé pour régler quoi que ce soit.
10. **Journal d'accès au test** : chaque évaluation du test est notée (date, personne, raison) dans `reports/`. Le dépôt est étiqueté avant la première évaluation.

### 6.2 Ce qu'on ne fait pas

Découpage aléatoire des fichiers ; dégradations du même document réparties entre ensembles ; mêmes entreprises dans deux ensembles ; réglage sur le test ; ajouter au train des documents du test après coup ; sélectionner « le meilleur modèle sur le test ».

### 6.3 Documents dérivés de test (vue de robustesse, optionnel)

Pour comparer proprement propre vs dégradé à contenu identique, chaque document du test peut être rendu aux trois niveaux. Ces versions sont rangées dans une **vue séparée** (`derived_from` rempli), non comptées dans les métriques principales (elles sont corrélées) et rapportées en courbe de robustesse.

### 6.4 Expérience de démonstration de la fuite

Pour que l'équipe, et le rapport, voient le problème que la méthode évite, on compare **une fois** : découpage aléatoire des fichiers contre découpage par gabarit, avec le même modèle. Seul l'écart entre les deux est un résultat pertinent ; il sera mesuré, pas supposé.

## 7. Protocole d'évaluation

### 7.1 Métriques demandées

Sur validation (hors pli) et sur test :

| Métrique | Définition | Usage |
|---|---|---|
| **Accuracy** | part de documents bien classés | Information, trompeuse si les classes sont inégales. |
| **Precision** (par classe) | parmi les documents classés dans C, part qui est vraiment C | **La plus critique ici** : une fausse acceptation est l'erreur coûteuse. |
| **Recall** (par classe) | parmi les vrais C, part retrouvée | Un rappel faible envoie trop de documents en revue manuelle. |
| **F1-score** (par classe) | moyenne harmonique | Résumé par classe. |
| **F1 macro** | moyenne simple des F1 | **Métrique principale de comparaison** : traite les classes à égalité. |
| **Matrice de confusion** | comptes et lignes normalisées | Montre **quelles** classes se confondent, c'est l'outil d'analyse d'erreur. |

Compléments : F1 pondéré (information), rapport par sous-type de `autre`.

### 7.2 Fiabiliser, la vraie question du sujet

Le sujet demande de « fiabiliser » les documents (p.4). Une exactitude globale ne le dit pas. On rapporte donc aussi :

- **Courbe couverture / précision** : en faisant varier le seuil de confiance, quelle part des documents est traitée sans consultant (couverture) pour quelle précision. Le seuil de production est choisi sur la validation avec une précision cible fixée avec l'encadrement (§7.7), et **le test n'est utilisé que pour mesurer** ce que ce seuil donne.
- **Taux de fausse acceptation** : part des documents de `autre` classés dans une classe principale avec une confiance au-dessus du seuil. Un devis pris pour une facture validée sans revue est le scénario à éviter.
- **Calibration** : courbe de fiabilité, score de Brier, erreur de calibration attendue. Une confiance de 0,9 doit correspondre à environ 90 % de réussite pour que le seuil ait un sens.

### 7.3 Incertitude

Test de petite taille et gabarits peu nombreux : chaque score est accompagné d'un **intervalle de confiance par bootstrap par gabarit** (on tire les gabarits avec remise, pas les documents). Les comparaisons de modèles se font sur les **mêmes documents** (comparaison appariée) ; on ne conclut à une différence que si l'intervalle de l'écart exclut zéro. Un écart inférieur à l'intervalle est écrit comme tel. Avec 2 gabarits de test par classe dans le plan minimal, l'intervalle est peu informatif : on publie en plus la **dispersion par gabarit** (§2.6).

### 7.4 Tranches d'analyse (obligatoires)

Chaque métrique est rapportée au minimum selon : niveau de dégradation ; PDF natif contre scan ; gabarit (pour repérer un gabarit « catastrophe ») ; sous-type de `autre` ; documents à champs manquants ; documents tronqués ; **sous-type inconnu (`attestation_emploi`)** ; jeu stress ; qualité de lecture (par tranches de confiance OCR) ; paires trompeuses.

Le **contrôle de qualité de lecture** (envoi en `A_REVOIR` sous un seuil de confiance OCR ou de longueur de texte) est évalué à part : on mesure combien de documents réellement illisibles sont arrêtés, et combien de documents lisibles sont arrêtés à tort.

### 7.5 Expériences à planifier (mesures, pas conclusions)

| # | Expérience | Question |
|---|---|---|
| E1 | Découpage aléatoire vs groupé (§6.4) | Quelle est l'ampleur de la fuite dans notre cas ? |
| E2 | Retirer le titre et les premières lignes du texte | Le modèle lit-il le mot « Facture » ou le contenu ? |
| E3 | Entraînement propre seulement vs avec dégradations | La dégradation à l'entraînement aide-t-elle sur les scans ? |
| E4 | Courbe d'apprentissage selon le **nombre de gabarits** | Faut-il plus de diversité ou plus de volume ? |
| E5 | Texte écrit par l'équipe seulement vs avec brouillon assisté | Le style généré est-il une signature ? |
| E6 | Effet de la qualité de lecture | L'erreur vient-elle du modèle ou de l'OCR ? (grâce à `texte_reference`) |
| E7 | Ablation des familles de features (§4) | Que valent les indices de structure ? |
| E8 | **Baseline à règles** | Voir 7.6. |

### 7.6 Pourquoi ML : la baseline à règles

Pour démontrer que la brique est « utile et pas décorative » (p.3), on compare le modèle à une **liste de règles à mots-clés** (« bulletin de paie », « net à payer », « article 1 », « ordre du jour »…) écrite en avance et figée, par un membre qui ne regarde pas le test, en 2 h maximum. Si les règles font aussi bien sur tout, y compris sur le stress et les documents dégradés, il faut le dire et recentrer la contribution du ML (calibration, revue humaine, cas ambigus). Si elles échouent sur les voisins trompeurs ou les scans, c'est la justification du ML. Dans les deux cas, c'est une mesure.

### 7.7 Critères de décision

Fixés **avant** d'avoir des résultats, avec l'encadrement :
- précision cible par classe principale à l'opération (valeur à définir avec Leyton selon le coût d'une erreur) ;
- couverture minimale souhaitée pour que l'automatisation ait un intérêt ;
- seuil de F1 macro sur le test : à fixer après mesure de la baseline pour ne pas fixer un chiffre arbitraire.

### 7.8 Documents inconnus (détection hors distribution)

#### 7.8.1 Ce que le problème est, et n'est pas

Le classifieur est « fermé » : cinq classes apprises. Un document d'un type jamais vu (`attestation_emploi`, ou un type que Leyton n'a pas prévu) sera rangé dans la classe la plus proche. **Un seuil de confiance seul ne garantit pas la détection** : les probabilités d'un modèle linéaire peuvent rester élevées loin des données d'entraînement. Une attestation d'emploi partage par exemple « employeur », « salarié », « période » avec une fiche de paie, et rien ne garantit que le modèle la juge incertaine. C'est une **hypothèse à tester**, pas un acquis. On construit donc plusieurs défenses indépendantes, on les mesure séparément, et on ne promet aucune garantie.

#### 7.8.2 Défenses en couches

| Couche | Mécanisme | Attrape | Limite connue |
|---|---|---|---|
| L1 | Classe **`autre` apprise** (rejet appris sur négatifs connus) | Types proches des sous-types de `autre` vus | Ne généralise pas aux types non vus |
| L2 | **Confiance** : 1 − probabilité maximale, calibrée | Documents ambigus entre classes | Peut rester élevée hors distribution ; un signal parmi d'autres |
| L3 | **Nouveauté dans l'espace des caractéristiques** : similarité cosinus au plus proche voisin d'entraînement de la classe prédite ; part de termes hors vocabulaire ; en option un détecteur de nouveauté (forêt d'isolement ou SVM à une classe) sur une réduction du TF-IDF | Documents éloignés de ce qu'on a vu | **Le bruit d'OCR peut rendre « nouveau » un document connu mais dégradé** : le score est contrôlé par niveau de dégradation |
| L4 | **Vérification structurelle par règles** : champs obligatoires de la classe prédite (une `facture` sans montant ni numéro ; une `fiche_de_paie` sans période ni net à payer) | Documents dont le contenu n'est pas celui du type annoncé | Dépend de l'extraction ; rejette aussi des pièces légitimes incomplètes (acceptable : revue) |
| L5 | **Humain** : tout rejet part en `A_REVOIR` avec le motif « type non reconnu » ; la correction du consultant enrichit le corpus | Ce que les couches précédentes laissent passer, *s'il est vu* | N'attrape pas un inconnu accepté en silence |

**Règle d'acceptation** : un document est accepté comme type T (parmi les 4 classes principales) seulement si la classe prédite n'est pas `autre`, si la confiance et le score de nouveauté passent leurs seuils, et si les champs obligatoires de T sont présents. Sinon il va au consultant. Seuils fixés sur la validation, jamais sur le test.

#### 7.8.3 Réglage sans tricher : « laisser un sous-type de côté »

Pour régler les seuils sans toucher aux inconnus du test, on **simule** des inconnus en développement : pour chaque sous-type S de `autre` (4 dans le plan minimal), on **réentraîne sans S**, puis on mesure, sur les gabarits de S en pli de validation, s'il est détecté comme inconnu. On obtient 4 inconnus simulés pour choisir les scores et les seuils. Le seuil de rejet est fixé pour que la part de documents **connus** des classes principales rejetés à tort ne dépasse pas une limite à fixer avec l'encadrement (charge acceptable pour le consultant). `attestation_emploi` et les types inconnus du stress ne servent **jamais** à régler.

#### 7.8.4 Évaluation séparée

Cette évaluation est **distincte** du F1 macro sur les classes connues et ne s'y mélange jamais.

- **Population « connus »** : documents de test des 4 classes principales (dégradations comprises). **Population « inconnus »** : `attestation_emploi` (test), types inconnus du stress, inconnus simulés (7.8.3).
- **Métriques** (pour chaque couche seule, puis combinées) :
  - AUROC et AUPR du score de rejet (inconnu contre connu) ;
  - **part d'inconnus acceptés** quand 95 % des documents connus sont acceptés ;
  - **taux de fausse acceptation d'un inconnu** au seuil de production ;
  - **taux de rejet à tort de connus** au même seuil : la charge pour le consultant.
- **Contrôle de la confusion avec la dégradation** : scores rapportés par niveau de dégradation, pour vérifier que le détecteur ne distingue pas « propre » de « sale » plutôt que « connu » d'« inconnu ». Les inconnus ont **la même répartition de dégradations** que les connus.
- **Cas trivial de contrôle** : 5 documents fictifs très éloignés (lettre personnelle, menu…), pour vérifier que le cas facile fonctionne ; non comptés dans les métriques.
- Intervalles de confiance publiés, **avec la réserve** que le nombre de types inconnus est très faible.

#### 7.8.5 Ce qu'on pourra affirmer, et ce qu'on ne pourra pas

| On pourra dire | On ne pourra pas dire |
|---|---|
| « Sur les types inconnus testés (1 en test, 5 en stress, 4 simulés), le système en rejette X %, au prix de Y % de documents connus envoyés en revue. » | « Le système détecte les documents inconnus. » |
| Quelles couches contribuent, lesquelles ne servent à rien. | Que cette capacité vaut pour un type quelconque. |
| Que, si un inconnu est accepté à tort, le consultant reste le filet de sécurité. | Que ce filet suffit : un inconnu accepté en silence n'est pas vu. |

## 8. Risques de biais et de fuite

| Risque | Mécanisme | Parade |
|---|---|---|
| **Mémorisation de gabarit** | Le modèle reconnaît la mise en page, pas le type de document. | Découpage par gabarit ; ≥ 2 gabarits de test par classe ; stress. |
| **Fuite d'entités** | Mêmes noms d'entreprises ou de personnes dans train et test. | Pools A/B/C disjoints. |
| **Fuite par dégradation** | Versions d'un même document dans des ensembles différents. | Groupe = gabarit ; dérivés de test rangés à part. |
| **Quasi-doublons** | Contenus presque identiques entre ensembles. | Contrôle automatique : empreintes + similarité de textes entre ensembles ; tout couple très proche est signalé et traité. |
| **Artefacts du générateur** | Métadonnées PDF, nom de fichier, taille, résolution, polices trahissent la classe. | Identifiants opaques, métadonnées normalisées, features limitées au texte. Vérifié par un test où un classifieur reçoit **seulement** ces artefacts : il doit faire au niveau du hasard. |
| **Mot-titre trivial** | « Facture » en en-tête rend la tâche triviale. | Expérience E2 ; jeu stress avec titres absents ou ambigus. |
| **Lexique du générateur** | Listes de phrases finies : le modèle apprend le lexique du script. | Blocs de texte nombreux et écrits par l'équipe ; stress rédigé à la main. |
| **Style d'un modèle de langage** | Textes assistés trop homogènes. | `source_texte`, expérience E5. |
| **Biais de conception** | Nous créons les cas difficiles : ils ressemblent à ce que nous avons imaginé. | Stress indépendant ; documents publics ; pièces anonymisées de Leyton si possibles ; limite écrite. |
| **Écart synthétique-réel** | Aucun document réel ne figure dans l'évaluation. | Rapporté comme **limite principale** : les scores mesurent la généralisation à d'autres gabarits fictifs, pas la performance sur de vrais dossiers. |
| **Fuite par prétraitement** | TF-IDF ou seuil ajusté avant découpage. | Tout dans un pipeline ajusté sur le train du pli. |
| **Réglage sur le test** | Itérations après lecture du test. | Test évalué une fois ; journal d'accès. |
| **Biais de classe** | Proportions artificielles. | F1 macro, métriques par classe, limite sur la différence avec la production. |
| **Domaines R&D** | Thèmes limités à ceux que nous imaginons. | Une dizaine de domaines, répartition disjointe, limite écrite. |
| **Effectifs faibles** | Un écart de 1-2 documents modifie les scores. | Intervalles de confiance par gabarit ; pas de classement de modèles sans écart significatif. |
| **Annotation erronée** | Erreurs dans les documents manuels. | Double annotation, relecture de 10 %. |
| **Contrôle d'OCR variable** | Moteur ou paramètres changeant en cours de route. | Version et paramètres figés dans le manifeste ; recalcul complet si changement. |

## 9. Comparaison des approches

Ce tableau est un **plan de comparaison** fondé sur les propriétés connues de ces méthodes. Aucune colonne n'indique de performance : elle sera mesurée.

| Approche | Principe | Forces | Faiblesses | Explicabilité | Probabilités | Coût |
|---|---|---|---|---|---|---|
| **P0** Classe majoritaire | Aucune apprise | Plancher de comparaison | Aucune valeur | n/a | n/a | nul |
| **Règles à mots-clés** | Expressions écrites à la main | Transparent, immédiat | Fragile aux fautes d'OCR, au vocabulaire, aux voisins | Totale | non | faible |
| **P1 TF-IDF + Régression logistique** | Modèle linéaire sur mots et caractères | Baseline robuste en petit corpus, probabilités natives, **poids lisibles** | Ignore l'ordre des mots et la structure | **Forte** : termes qui pèsent | oui, à calibrer | faible (CPU) |
| **P2a TF-IDF + SVM linéaire** | Marge maximale | Souvent proche ou meilleur que la logistique en haute dimension | Pas de probabilités natives : calibration à ajouter | Forte (poids) | non natif, calibrer | faible |
| **P2b Naive Bayes complémentaire** | Modèle probabiliste simple | Très rapide, tient bien avec peu de données | Probabilités mal calibrées | Bonne | peu fiables | très faible |
| **P2c Forêt aléatoire / XGBoost** | Arbres sur TF-IDF réduit + indices de structure | Capte des interactions et des indices non textuels | Moins adapté au texte creux ; risque de surapprentissage sur peu de gabarits | Moyenne | oui, à calibrer | moyen |
| **P3a Embeddings de phrases multilingues figés + LR** | Représentation pré-entraînée, classifieur appris par nous | Capte le sens au-delà des mots exacts ; pas de réglage lourd | Dépendance à un modèle pré-entraîné ; moins lisible | Faible | oui | moyen (CPU possible) |
| **P3b Modèle de langue affiné (type CamemBERT)** | Réglage complet d'un modèle pré-entraîné | Meilleure compréhension du contexte | Données et calcul ; **risque élevé de surapprentissage à ~300 documents** ; difficile à expliquer | Faible | oui, mal calibré | élevé (GPU conseillé) |
| **Extension** Modèle multimodal à mise en page | texte + positions | Capte la structure | Données et outillage lourds | Faible | oui | élevé |

### 9.1 Ordre d'exécution

1. P0 et règles (E8) : le plancher et le point de comparaison.
2. **P1 et P2a** : les deux modèles que vous demandez, comparés à configuration de caractéristiques identique (mots seuls, caractères seuls, les deux). **C'est le cœur de la v1.**
3. P2b et P2c : comparaison d'algorithmes pour le rapport.
4. P3a : seulement si la condition ci-dessous est remplie.
5. P3b : uniquement avec une justification forte et en connaissant le coût d'explication.

### 9.2 Quand passer à un modèle plus avancé ?

On n'ouvre P3 que si **toutes** ces conditions sont réunies :
1. P1 et P2a ont été réglés correctement (validation croisée groupée) ;
2. l'analyse d'erreurs montre des confusions qui relèvent de la **sémantique** (même sujet, mots différents) plutôt que de la qualité du corpus ou de l'OCR ;
3. le gain de F1 macro hors pli dépasse l'intervalle de confiance, **y compris sur les tranches difficiles** ;
4. le temps d'inférence par document reste acceptable en démonstration (quelques secondes) ;
5. l'équipe peut **expliquer** le modèle en soutenance (« chacun doit pouvoir expliquer tout le code », p.12).

Si elles ne le sont pas, on documente ce choix : un modèle simple, expliqué et bien évalué répond mieux au sujet qu'un modèle lourd mal compris.

### 9.3 Réglage

Petit et documenté : TF-IDF (mots 1-2 grammes, caractères 2-5, `min_df`, `sublinear_tf`), régularisation C ∈ {0,1 ; 1 ; 10 ; 100} pour P1 et P2a, poids de classe équilibrés ou non. Critère : F1 macro hors pli. La grille complète est fixée dans `src/ml/configs/` avant les essais.

## 10. Décisions principales et justification

| Décision | Justification |
|---|---|
| 5 classes dont `autre` composé de voisins trompeurs | Les 4 types du sujet ne suffisent pas en dropzone réelle ; l'`autre` « facile » ferait gonfler les scores. |
| Sous-type inconnu en test, détection en couches, réglage par « sous-type laissé de côté » | Un classifieur fermé ne rejette pas par construction ; on mesure au lieu de supposer, sans promettre de garantie (§7.8). |
| **Plan minimal** (38 gabarits générés, 348 documents + ≈ 30 de stress), livré par vagues, extension en train/val seulement | La diversité des gabarits est la contrainte qui compte ; le plan complet (54 gabarits, 656 + 40 documents) dépasse ce que 3 à 5 étudiants peuvent produire en 2 semaines à côté du prototype. Le test (2 gabarits par classe principale) et le stress ne sont pas réduits. |
| Découpage par gabarit, entités et domaines disjoints | Évite la mémorisation, principal risque d'un corpus fictif. |
| Jeu stress indépendant | Seule protection contre notre propre biais de conception. |
| Vérité terrain issue du générateur (champs, texte, défauts) | Gratuite, et indispensable pour séparer erreur d'OCR, erreur de classifieur et erreur de règle. |
| Défauts de conformité annotés mais hors cible du classifieur | La conformité relève des règles, pas du ML : on ne mélange pas les deux. |
| Français seul en v1 | Sujet en français ; l'anglais double le travail de gabarits. Sonde en stress. |
| Baseline à règles dans l'évaluation | Prouver que le ML est utile (p.3) plutôt que de l'affirmer. |
| Intervalles par bootstrap sur les gabarits | Les scores ponctuels d'un petit test sont trompeurs. |
| P1 / P2a d'abord, modèle avancé conditionnel | Cohérent avec la taille du corpus, l'exigence d'explication et le calendrier. |
| Tout résultat est mesuré ou absent | Règle du projet : aucun résultat fabriqué, aucune donnée synthétique présentée comme réelle. |

## 11. Questions à clarifier

1. Les **quatre types** du sujet sont-ils exhaustifs ? Faut-il gérer l'avoir, le relevé de TVA, la fiche de poste, un PDF contenant plusieurs documents ?
2. Quelle **précision** minimale est jugée acceptable par Leyton avant revue humaine, et quel est le coût relatif d'une fausse acceptation et d'une revue inutile ?
3. Les **documents** sont-ils français uniquement ? Quelle part de scans et de photos en pratique ?
4. Leyton peut-il fournir **quelques pièces anonymisées ou des maquettes**, utilisables au moins en test ?
5. Un consultant peut-il **relire** un échantillon de documents fictifs pour juger leur réalisme ?
6. Une pièce d'un type connu mais **incomplète** doit-elle être classée dans son type (notre hypothèse) ou rejetée comme `autre` ?
7. Accepte-t-on les documents d'**un même PDF mélangeant plusieurs types** ?
8. Quelle part de documents **connus rejetés à tort** (charge de revue du consultant) Leyton juge-t-il acceptable ? Cela fixe le seuil de rejet (§7.8.3).
9. Quel **temps réel par semaine** chaque membre peut-il consacrer au corpus ? Les estimations du §2.3 sont à confronter à cette réponse avant de s'engager.

## 12. Livrables de cette étape et suite

- Ce document, à valider par l'équipe.
- À créer **après validation** (pas avant) : `data/annotations/` (modèles de `manifest.csv`, `verite_terrain.jsonl`, `splits.csv`), `src/datagen/` (gabarits, pools d'entités, dégradations), guide d'annotation, script de contrôle de fuite, script de découpage.
- Prochaines décisions à prendre : **choix entre plan complet et plan minimal (recommandation : minimal, §2.5)**, répartition du travail de gabarits entre membres, désignation du porteur du jeu stress, essai d'une heure sur la chaîne de rendu (§5.7), accord sur le corpus minimal viable de la semaine 1.
