# -*- coding: utf-8 -*-

import pandas as pd
import requests
import yaml
import ast
import csv  # ✅ nécessaire pour gérer correctement les quotes

# 📁 Chemin du fichier source
INPUT = "CartoDataMC/cartographie_ressources_datasets.csv"
OUTPUT = "CartoDataMC/Cartographie_Culture_properties.csv"

# 📥 Lecture du fichier d'entrée avec bon séparateur et quoting
df_csv = pd.read_csv(INPUT, sep=";", quoting=csv.QUOTE_ALL).head(200)

# ✅ Vérification des colonnes nécessaires
colonnes_attendues = ["id.ressource", "id.dataset", "title.dataset", "description.dataset", "tags.dataset"]
missing = [col for col in colonnes_attendues if col not in df_csv.columns]
if missing:
    raise ValueError(f"Les colonnes suivantes sont manquantes dans le fichier : {missing}")

# 📦 Stockage des résultats
rows = []

for _, row in df_csv.iterrows():
    resource_id = row["id.ressource"]
    dataset_id = row["id.dataset"]
    dataset_title = row["title.dataset"]
    dataset_description = row["description.dataset"]

    # 🏷️ Traitement des tags
    tags_raw = row["tags.dataset"]
    if isinstance(tags_raw, str):
        try:
            tags_list = [
                tag["name"]
                for tag in ast.literal_eval(tags_raw)
                if isinstance(tag, dict) and "name" in tag
            ]
            dataset_tags = ", ".join(tags_list)
        except Exception:
            dataset_tags = ""
    else:
        dataset_tags = ""

    # 📡 Récupération du schéma de la ressource via Swagger
    url = f"https://tabular-api.data.gouv.fr/api/resources/{resource_id}/swagger/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            try:
                data = yaml.safe_load(response.text)
                props = data.get("components", {}).get("schemas", {}).get("Resource", {}).get("properties", {})

                if props:
                    for prop_name, prop_info in props.items():
                        rows.append({
                            "resource_id": resource_id,
                            "dataset_id": dataset_id,
                            "dataset_title": dataset_title,
                            "description": dataset_description,
                            "tags": dataset_tags,
                            "property_name": prop_name,
                            "property_type": prop_info.get("type", "unknown")
                        })
                else:
                    rows.append({
                        "resource_id": resource_id,
                        "dataset_id": dataset_id,
                        "dataset_title": dataset_title,
                        "description": dataset_description,
                        "tags": dataset_tags,
                        "property_name": "⚠️ Aucune colonne trouvée",
                        "property_type": ""
                    })
            except yaml.YAMLError as e:
                rows.append({
                    "resource_id": resource_id,
                    "dataset_id": dataset_id,
                    "dataset_title": dataset_title,
                    "description": dataset_description,
                    "tags": dataset_tags,
                    "property_name": f"❌ Erreur YAML : {str(e)}",
                    "property_type": ""
                })
        else:
            rows.append({
                "resource_id": resource_id,
                "dataset_id": dataset_id,
                "dataset_title": dataset_title,
                "description": dataset_description,
                "tags": dataset_tags,
                "property_name": f"❌ HTTP {response.status_code}",
                "property_type": ""
            })
    except Exception as e:
        rows.append({
            "resource_id": resource_id,
            "dataset_id": dataset_id,
            "dataset_title": dataset_title,
            "description": dataset_description,
            "tags": dataset_tags,
            "property_name": f"❌ Exception : {str(e)}",
            "property_type": ""
        })

# 💾 Enregistrement des résultats
df_properties = pd.DataFrame(rows)
df_properties.to_csv(OUTPUT, index=False, quoting=csv.QUOTE_ALL, sep=";")

print(f"✅ Fichier généré : {OUTPUT}")
