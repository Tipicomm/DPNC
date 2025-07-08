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

# Phase 3 – Alignement sémantique

## 🎯 Objectif
Enrichir les propriétés extraites de jeux de données culturels français avec des métadonnées sémantiques : description, classification thématique, typage référentiel, et tentative d’alignement avec des vocabulaires standards comme `schema.org` ou les nomenclatures de l’INSEE.

## 🗂️ Fichiers

- **Entrée principale :**  
  `CartoDataMC/cartographie_ressources_datasets_proprietes.csv`  
  → Propriétés extraites automatiquement des métadonnées de jeux de données culturels.

- **Modèle d’axes de référence :**  
  `CartoDataMC/ModeleMetaMC_UTF8.csv`  
  → Décrit les axes thématiques du référentiel MetaMC (axe, libellé, définition).

- **Sortie intermédiaire par lot :**  
  `CartoDataMC/semantique_batches/batch_*.csv`

- **Sortie finale :**  
  `CartoDataMC/cartographie_culture_semantique.csv`  
  → Fusion des données sources et de l’enrichissement sémantique.

## ⚙️ Workflow automatisé (`MetaMc_analyse_semantique.py`)

1. **Chargement des fichiers sources**
   - Lecture des propriétés (`cartographie_ressources_datasets_proprietes.csv`)
   - Lecture du référentiel d’axes thématiques (`ModeleMetaMC_UTF8.csv`)

2. **Génération de prompts structurés**
   - Pour chaque lot de 10 propriétés, construction d’un contexte détaillé (titre, description, type, exemples…)
   - Injection des axes MetaMC comme référence dans le prompt

3. **Appel à l’API OpenAI (GPT-4o)**
   - Génère un tableau avec :
     - `definition`
     - `Axe de référence`
     - `Type référentiel`
     - `Référentiel alignement`

4. **Fusion des enrichissements**
   - Assemblage des résultats en sortie (`cartographie_culture_semantique.csv`)
   - Export au format CSV avec encodage UTF-8 et guillemets normalisés

## 📉 Limites actuelles

- Les colonnes `Référentiel alignement` et `Type référentiel` contiennent des résultats partiels ou peu précis.
- L’alignement automatique est sensible aux biais de formulation, aux noms ambigus ou mal typés.
- Le script se limite à un nombre restreint de lignes (`ROW_END = 10` par défaut).
