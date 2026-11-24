# Données

Règle du cahier des charges (p.4 et p.12) : **documents fictifs ou anonymisés uniquement.** Ils sont donc versionnés ici, sauf les dérivés régénérables.

| Dossier | Contenu |
|---------|---------|
| `raw/` | Documents originaux (PDF, images), fictifs ou anonymisés. Jamais modifiés après ajout. |
| `interim/` | Texte OCR et images prétraitées (régénérable, non versionné). |
| `processed/` | Jeux train / validation / test / stress (régénérables, non versionnés). |
| `annotations/` | `manifest.csv` : un document par ligne (identifiant, classe, **provenance**, gabarit, langue, annotateur, date). |

## Règles

1. **Provenance obligatoire** : `fictif_manuel`, `fictif_genere`, `anonymise`, `public`. Un document fictif n'est jamais présenté comme réel.
2. **Anonymisation complète** avant tout ajout d'un document d'origine réelle : noms, adresses, IBAN, identifiants, numéros de sécurité sociale. En cas de doute, ne pas l'ajouter.
3. **Gabarit renseigné** pour chaque document : le découpage train/validation/test se fait par gabarit.
4. Les scripts qui génèrent des documents sont versionnés avec leur graine.
5. Un document non encore anonymisé va dans `data/private/`, ignoré par Git, et ne sort jamais de la machine.
