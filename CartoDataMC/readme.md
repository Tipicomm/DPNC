# 🗺️ CartoDataMc – Cartographie des données culturelles ouvertes

**CartoDataMc** est un projet porté par le Département des politiques numériques culturelles (DPNC) du ministère de la Culture.  
Il a pour objectif de cartographier, documenter et structurer les jeux de données culturels ouverts publiés sur [data.gouv.fr](https://www.data.gouv.fr/), afin de faciliter leur gouvernance, leur réutilisation et leur valorisation.

---

## 🔧 Scripts disponibles

### Script importsDataGouv.py

Ce script automatise la génération d’une cartographie des ressources CSV publiées sur data.gouv.fr par le Ministère de la Culture.
📌 Objectif

Créer un fichier unique cartographie_ressources_datasets.csv listant les ressources CSV disponibles, enrichies avec le titre, la description et les tags de leur jeu de données parent.
📂 Étapes du traitement

    Téléchargement des ressources

        Fichier source : datasets-resources.csv

        Filtrage sur le format csv

        Colonnes extraites : id (ressource), dataset.id, dataset.title

        Résultat : ressources_culture.csv

    Téléchargement des jeux de données

        Fichier source : datasets.csv

        Colonnes extraites : id (dataset), title, description, tags

        Résultat : datasets_culture.csv

    Fusion et nettoyage

        Jointure sur id.dataset

        Nettoyage des doublons (title.dataset_x, title.dataset_y)

        Résultat final : cartographie_ressources_datasets.csv
---

### 2. `extraction_properties.py`  
Interroge l’API [`tabular.data.gouv.fr`](https://tabular.data.gouv.fr/) pour extraire dynamiquement les propriétés (colonnes) de chaque ressource CSV.

- 📥 Entrée : `cartographie_ressources_datasets.csv`
- 📤 Sortie : `Cartographie_Culture_properties.csv`

---

### 3. `analyse_semantique.py`  
Utilise l’API OpenAI pour analyser les propriétés et les regrouper par classes sémantiques (ex : date, structure, œuvre…).

- 📥 Entrée : `Cartographie_Culture_properties.csv`
- 📤 Sortie : `Cartographie_Culture_classes.csv`
- 🧠 Modèle utilisé : `gpt-4` via `openai.ChatCompletion`

---



---

## 🚀 Exemple d’enchaînement

```bash
# 1. Téléchargement et fusion des ressources
python CartoDataMc/importsDataGouv.py

# 2. Extraction des propriétés de colonnes via Swagger
python CartoDataMc/extraction_properties.py

# 3. Analyse sémantique des propriétés via OpenAI
python CartoDataMc/analyse_semantique.py
