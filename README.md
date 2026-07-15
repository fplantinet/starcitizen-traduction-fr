# Traduction FR enrichie pour Star Citizen

Un `global.ini` prêt à l'emploi : la traduction française communautaire
([Dymerz/StarCitizen-Localization](https://github.com/Dymerz/StarCitizen-Localization)),
enrichie d'améliorations communautaires **greffées sur le texte français** :

- **préfixes de classification des composants** (taille/classe/type, ex.
  « C3A Rayon Tracteur SureGrip S3 ») issus de
  [BeltaKoda/ScCompLangPackRemix](https://github.com/BeltaKoda/ScCompLangPackRemix) ;
- **informations de récompenses de missions** (réputation, paiements) issues d'
  [ExoAE/ScCompLangPack](https://github.com/ExoAE/ScCompLangPack), qui inclut
  [StarStrings](https://github.com/MrKraken/StarStrings).

Quand une amélioration ne peut pas être greffée proprement sur le texte
français, le français est conservé tel quel — **le français gagne toujours**.

## Téléchargement

➡️ **<https://raw.githubusercontent.com/fplantinet/starcitizen-traduction-fr/main/dist/global.ini>**

Le fichier est régénéré automatiquement chaque nuit à partir des dernières
versions de la traduction et des packs (workflow GitHub Actions
`build-fr-pack`) : re-téléchargez-le après un patch du jeu ou quand vous
voulez les dernières nouveautés.

## Installation

1. Placer le fichier téléchargé dans :
   `<dossier du jeu>\StarCitizen\LIVE\data\Localization\french_(france)\global.ini`
   (créer les dossiers s'ils n'existent pas).
2. Créer ou éditer `<dossier du jeu>\StarCitizen\LIVE\user.cfg` et y ajouter :
   ```
   g_language = french_(france)
   ```
3. Relancer le jeu.

## Composer votre propre variante

Pour un mélange différent (traduction FR pure, autres packs, choix par
catégorie), utilisez l'outil [StarMeld](https://beltakoda.github.io/StarMeld/)
et son upload de pack personnalisé — ce `global.ini` y est utilisable tel quel.

## Développement

Générateur en Python (bibliothèque standard uniquement, Python ≥ 3.9) :

```
python3 scripts/test_build_fr_enriched.py   # tests unitaires
python3 scripts/build_fr_enriched.py        # régénère dist/global.ini
```

Le générateur télécharge les sources (stock du jeu, traduction FR, packs
d'amélioration), fusionne clé par clé et greffe les ajouts des packs
(préfixes/suffixes autour du texte d'origine) sur la valeur française.

## Crédits et licence

- Traduction française :
  [Dymerz/StarCitizen-Localization](https://github.com/Dymerz/StarCitizen-Localization)
  et ses contributeurs.
- Améliorations d'origine :
  [BeltaKoda](https://github.com/BeltaKoda/ScCompLangPackRemix),
  [ExoAE](https://github.com/ExoAE/ScCompLangPack),
  [MrKraken](https://github.com/MrKraken/StarStrings).
- Outil de fusion recommandé : [StarMeld](https://github.com/beltakoda/StarMeld)
  (BeltaKoda).

Générateur sous licence MIT ([LICENSE](LICENSE)). Ce projet n'est pas affilié à
Cloud Imperium Games. Star Citizen® est une marque de Cloud Imperium Rights LLC.
