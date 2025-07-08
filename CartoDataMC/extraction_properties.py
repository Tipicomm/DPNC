# -*- coding: utf-8 -*-
import pandas as pd
import requests
import os
import time

INPUT = "CartoDataMC/cartographie_ressources_datasets.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties.csv"

if not os.path.exists(INPUT):
    raise FileNotFoundError(f"Fichier introuvable : {INPUT}")

df = pd.read_csv(INPUT, sep=";")
properties = []

for idx, row in df.iterrows():
    resource_id = row.get("resource_id", "").strip()
    dataset_id = row.get("dataset_id", "").strip()
    titre = row.get("title.dataset", "") or row.get("title", "")

    if not resource_id or pd.isna(resource_id):
        continue

    try:
        profile_url = f"https://tabular-api.data.gouv.fr/api/resources/{resource_id}/profile/"
        resp = requests.get(profile_url)
        if resp.status_code != 200:
            print(f"❌ Échec pour {resource_id} (code {resp.status_code})")
            continue

        profile = resp.json().get("profile", {})
        colonnes = profile.get("columns", {})

        for prop in colonnes:
            properties.append({
                "dataset_id": dataset_id,
                "resource_id": resource_id,
                "title": titre,
                "property_name": prop,
                "property_label": prop  # utile si on veut distinguer le nom public
            })

    except Exception as e:
        print(f"⚠️ Erreur pour {resource_id} → {e}")
    time.sleep(0.5)

pd.DataFrame(properties).to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
print("✅ Fichier exporté :", OUTPUT)
