# -*- coding: utf-8 -*-
import pandas as pd
import requests
import yaml
import ast
import os
import csv

# 📁 Constantes
DOSSIER = "CartoDataMC"
INPUT = f"{DOSSIER}/cartographie_ressources_datasets.csv"
OUTPUT = f"{DOSSIER}/Cartographie_Culture_properties.csv"

# 📥 Chargement du fichier d’entrée avec fallback
try:
    df_csv = pd.read_csv(INPUT, sep=";", encoding="utf-8")
except Exception:
    df_csv = pd.read_csv(INPUT, sep=",", encoding="utf-8")

df_csv = df_csv.head(200)

# ✅ Vérification des colonnes nécessaires
colonnes_requises = ["id.ressource", "id.dataset", "title.dataset", "description.dataset", "tags.dataset"]
missing = [col for col in colonnes_requises if col not in df_csv.columns]
if missing:
    raise ValueError(f"Les colonnes suivantes sont manquantes dans le fichier : {missing}")

# 📦 Extraction ligne par ligne
rows = []

for _, row in df_csv.iterrows():
    resource_id = row["id.ressource"]
    dataset_id = row["id.dataset"]
    dataset_title = row.get("title.dataset", "")
    dataset_description = row.get("description.dataset", "")

    # 🔖 Extraction des tags
    tags_raw = row.get("tags.dataset", "")
    try:
        tags_list = [
            tag["name"]
            for tag in ast.literal_eval(tags_raw)
            if isinstance(tag, dict) and "name" in tag
        ]
        dataset_tags = ", ".join(tags_list)
    except Exception:
        dataset_tags = ""

    # 📡 Appel Swagger
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

# 💾 Sauvegarde du fichier final
df_properties = pd.DataFrame(rows)
df_properties.to_csv(OUTPUT, index=False, encoding="utf-8", sep=";", quoting=csv.QUOTE_MINIMAL)

print(f"✅ Fichier sauvegardé dans {OUTPUT}")
