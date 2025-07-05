# -*- coding: utf-8 -*-

import pandas as pd
import requests
import yaml
import ast
import os
import csv

# 📁 Chemins
INPUT = "CartoDataMC/cartographie_ressources_datasets.csv"
OUTPUT = "CartoDataMC/Cartographie_Culture_properties.csv"

# 📥 Fonction robuste de lecture du CSV
def robust_read_csv(path):
    try:
        return pd.read_csv(path, sep=";", encoding="utf-8")
    except Exception as e1:
        print("Échec avec le séparateur ';' :", e1)
        try:
            return pd.read_csv(path, sep=",", encoding="utf-8")
        except Exception as e2:
            print("Échec avec le séparateur ',' :", e2)
            raise ValueError(f"Echec de lecture du CSV {path} :\n- {e1}\n- {e2}")

df_csv = robust_read_csv(INPUT).head(200)

# 🔧 Normalisation dynamique des colonnes
if "title.dataset" not in df_csv.columns:
    if "title.dataset_y" in df_csv.columns:
        df_csv["title.dataset"] = df_csv["title.dataset_y"]
    elif "title.dataset_x" in df_csv.columns:
        df_csv["title.dataset"] = df_csv["title.dataset_x"]

# Vérifier que toutes les colonnes essentielles sont présentes
colonnes_requises = ["id.ressource", "id.dataset", "title.dataset", "description.dataset", "tags.dataset"]
missing = [col for col in colonnes_requises if col not in df_csv.columns]
if missing:
    raise ValueError(f"Les colonnes suivantes sont manquantes dans le fichier : {missing}")

# 📦 Extraire les propriétés
rows = []

for _, row in df_csv.iterrows():
    resource_id = row["id.ressource"]
    dataset_id = row["id.dataset"]
    dataset_title = row.get("title.dataset", "")
    dataset_description = row.get("description.dataset", "")
    
    # Nettoyage des tags
    tags_raw = row.get("tags.dataset", "")
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

    # Appel Swagger
    url = f"https://tabular-api.data.gouv.fr/api/resources/{resource_id}/swagger/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
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

# 💾 Export final
df_properties = pd.DataFrame(rows)
df_properties.to_csv(OUTPUT, index=False, quoting=csv.QUOTE_ALL, sep=";")
print("✅ Fichier d’extraction des propriétés généré :", OUTPUT)
