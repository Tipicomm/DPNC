# -*- coding: utf-8 -*-
import pandas as pd
import requests
import csv

INPUT = "CartoDataMC/cartographie_ressources_datasets.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties.csv"

df = pd.read_csv(INPUT, sep=";", quoting=csv.QUOTE_ALL)

colonnes = [
    "dataset_id",
    "resource_id",
    "dataset_title",
    "tags",
    "property_name",
    "property_label",
    "property_type",
]

rows = []
for idx, row in df.iterrows():
    rid = row["id.ressource"]
    did = row["id.dataset"]
    titre = row.get("title.dataset_y", row.get("title.dataset_x", ""))
    tags = row.get("tags.dataset", "")
    
    url_profile = f"https://tabular-api.data.gouv.fr/api/resources/{rid}/profile/"
    try:
        r = requests.get(url_profile)
        if r.status_code != 200:
            print(f"❌ {rid} → HTTP {r.status_code}")
            continue
        data = r.json()["profile"]
        colonnes_data = data.get("columns_labels", data.get("columns", {}))

        for prop in data["header"]:
            if prop not in colonnes_data:
                print(f"⚠️ {prop} absent de {rid}")
                continue

            prop_info = colonnes_data[prop]
            rows.append({
                "dataset_id": did,
                "resource_id": rid,
                "dataset_title": titre,
                "tags": tags,
                "property_name": prop,
                "property_label": prop,
                "property_type": prop_info.get("python_type", ""),
            })

    except Exception as e:
        print(f"⚠️ Erreur {rid} → {e}")

df_props = pd.DataFrame(rows, columns=colonnes)
df_props.to_csv(OUTPUT, sep=";", index=False)
print("✅ Fichier généré :", OUTPUT)
