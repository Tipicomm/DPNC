# 🗺️ CartoDataMc – Cartographie des données culturelles ouvertes

**CartoDataMc** est un projet porté par le Département des politiques numériques culturelles (DPNC) du ministère de la Culture.  
Il a pour objectif de cartographier, documenter et structurer les jeux de données culturels ouverts publiés sur [data.gouv.fr](https://www.data.gouv.fr/), afin de faciliter leur gouvernance, leur réutilisation et leur valorisation.



## 🔧 Scripts disponibles

###  1. Script importsDataGouv.py

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

Structure et propriétés du fichier cartographie_ressources_datasets.csv :
- id.ressource
- id.dataset
- title.dataset
- description.dataset
- tags.dataset


### 2. Script `extraction_colonnes_tabular.py`

Ce script extrait les **propriétés (colonnes)** de chaque ressource CSV publiée sur data.gouv.fr par le Ministère de la Culture, à l’aide de l’API [Tabular](https://tabular-api.data.gouv.fr). Il complète automatiquement les métadonnées issues des jeux de données en les enrichissant avec des statistiques descriptives.

#### 📌 Objectif
Préparer un fichier consolidé pour l’analyse sémantique des propriétés, en vue d’alignements avec des vocabulaires standardisés.

#### ⚙️ Fonctionnement
Pour chaque ressource CSV :
- Récupère le profil tabulaire via l’API `https://tabular-api.data.gouv.fr/api/resources/<id.ressource>/profile/`
- Extrait les colonnes et leurs métadonnées typologiques et statistiques
- Génère une ligne par **colonne détectée**

#### 📥 Fichier d’entrée
**Nom** : `cartographie_ressources_datasets.csv`  
**Format** : CSV (UTF-8, quotes forcées)
#### 🧾 Fichier de sortie
**Nom** : `cartographie_ressources_datasets_proprietes.csv`  
**Format** : CSV (UTF-8, quotes forcées)

#### 📑 Structure du fichier de sortie

| Colonne               | Description                                         |
|-----------------------|-----------------------------------------------------|
| `id.ressource`        | Identifiant de la ressource (fichier CSV)          |
| `id.dataset`          | Identifiant du jeu de données parent               |
| `title.dataset`       | Titre du jeu de données                            |
| `description.dataset` | Description du jeu de données                      |
| `tags.dataset`        | Mots-clés associés                                 |
| `column_name`         | Nom de la colonne extraite du fichier              |
| `column_datatype`     | Type détecté (ex. : `string`, `float`, `year`)     |
| `python_type`         | Type Python estimé (`string`, `float`, etc.)       |
| `score`               | Score de confiance du typage                       |
| `nb_distinct`         | Nombre de valeurs distinctes                       |
| `nb_missing_values`   | Nombre de valeurs manquantes                       |
| `top_1`               | Valeur la plus fréquente                           |
| `top_2`               | 2e valeur la plus fréquente                        |
| `top_3`               | 3e valeur la plus fréquente                        |

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
