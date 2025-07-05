# -*- coding: utf-8 -*-
import pandas as pd
import requests
import yaml
import ast
import os

INPUT = "CartoDataMC/cartographie_ressources_datasets.csv"
OUTPUT = "CartoDataMC/Cartographie_Culture_properties.csv"

df_csv = pd.read_csv(INPUT, sep=";").head(200)

# Vérification des colonnes
colonnes_requises = ["id.ressource", "id.dataset", "title.dataset", "description.dataset", "tags.dataset"]
missing = [col for col in colonnes_requises if col not in df_csv.columns]
if missing:
    raise ValueError(f"Les colonnes suivantes sont manquantes dans le fichier : {missing}")

rows = []
for _, row in df_csv.iterrows():
    res_id = row["id.ressource"]
    ds_id = row["id.dataset"]
    title = row["title.dataset"]
    desc = row["description.dataset"]
    tags_raw = row["tags.dataset"]

    try:
        tags_list = [t["name"] for t in ast.literal_eval(tags_raw) if isinstance(t, dict) and "name" in t]
        tags = ", ".join(tags_list)
    except Exception:
        tags = ""

    url = f"https://tabular-api.data.gouv.fr/api/resources/{res_id}/swagger/"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = yaml.safe_load(r.text)
            props = data.get("components", {}).get("schemas", {}).get("Resource", {}).get("properties", {})
            if props:
                for name, meta in props.items():
                    rows.append({
                        "resource_id": res_id,
                        "dataset_id": ds_id,
                        "dataset_title": title,
                        "description": desc,
                        "tags": tags,
                        "property_name": name,
                        "property_type": meta.get("type", "unknown")
                    })
            else:
                rows.append({
                    "resource_id": res_id,
                    "dataset_id": ds_id,
                    "dataset_title": title,
                    "description": desc,
                    "tags": tags,
                    "property_name": "⚠️ Aucune colonne trouvée",
                    "property_type": ""
                })
        else:
            rows.append({
                "resource_id": res_id,
                "dataset_id": ds_id,
                "dataset_title": title,
                "description": desc,
                "tags": tags,
                "property_name": f"❌ HTTP {r.status_code}",
                "property_type": ""
            })
    except Exception as e:
        rows.append({
            "resource_id": res_id,
            "dataset_id": ds_id,
            "dataset_title": title,
            "description": desc,
            "tags": tags,
            "property_name": f"❌ Exception : {str(e)}",
            "property_type": ""
        })

# Sauvegarde
df_props = pd.DataFrame(rows)
df_props.to_csv(OUTPUT, index=False)
print(f"✅ Fichier sauvegardé : {OUTPUT}")
