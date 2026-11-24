# Evaluation du modele ML — Baseline P1

**Algorithme** : TF-IDF (word) + Keywords metier + RandomForest
**Version** : 2.0.0
**Date** : 2026-11-24T16:00:37.481772+00:00
**Temps d'entrainement** : 0.15s

## Corpus
- Train : 80 documents
- Validation : 80 documents
- Test : 80 documents

## Validation
- **Accuracy** : 1.0000
- **F1 macro** : 1.0000
- **F1 weighted** : 1.0000

### Matrice de confusion
```
                 factur  fiche_  contra  compte   autre
        facture      10       0       0       0       0
  fiche_de_paie       0      10       0       0       0
        contrat       0       0      10       0       0
compte_rendu_rd       0       0       0      10       0
          autre       0       0       0       0      40
```

### Rapport par classe
```
                 precision    recall  f1-score   support

        facture     1.0000    1.0000    1.0000        10
  fiche_de_paie     1.0000    1.0000    1.0000        10
        contrat     1.0000    1.0000    1.0000        10
compte_rendu_rd     1.0000    1.0000    1.0000        10
          autre     1.0000    1.0000    1.0000        40

       accuracy                         1.0000        80
      macro avg     1.0000    1.0000    1.0000        80
   weighted avg     1.0000    1.0000    1.0000        80

```

## Test
- **Accuracy** : 0.9875
- **F1 macro** : 0.9870
- **F1 weighted** : 0.9872

### Matrice de confusion
```
                 factur  fiche_  contra  compte   autre
        facture       9       0       0       0       1
  fiche_de_paie       0      10       0       0       0
        contrat       0       0      10       0       0
compte_rendu_rd       0       0       0      10       0
          autre       0       0       0       0      40
```

### Rapport par classe
```
                 precision    recall  f1-score   support

        facture     1.0000    0.9000    0.9474        10
  fiche_de_paie     1.0000    1.0000    1.0000        10
        contrat     1.0000    1.0000    1.0000        10
compte_rendu_rd     1.0000    1.0000    1.0000        10
          autre     0.9756    1.0000    0.9877        40

       accuracy                         0.9875        80
      macro avg     0.9951    0.9800    0.9870        80
   weighted avg     0.9878    0.9875    0.9872        80

```
