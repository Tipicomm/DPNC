# -*- coding: utf-8 -*-

import pandas as pd
import requests

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties_exemples.csv"

df = pd.read_csv(INPUT, sep=";")

# Crée les colonnes pour les exemples
for i in range(1, 4):
    df[f"exemple_{i}"] = ""

# Groupe par ressource pour éviter de sur-solliciter l'API
for resource_id, group in df.groupby("resource_id"):
    try:
        url = f"https://tabular-api.data.gouv.fr/api/resources/{resource_id}/data/?page=1&pagesize=5"
        df_data = pd.read_csv(url)
    except Exception as e:
        print(f"❌ Impossible de charger la ressource {resource_id} ({e})")
        continue

    for idx, row in group.iterrows():
        col = row["property_name"]
        if col in df_data.columns:
            exemples = df_data[col].dropna().astype(str).unique()[:3]
            for i, exemple in enumerate(exemples):
                df.at[idx, f"exemple_{i+1}"] = exemple
        else:
            # Colonnes absentes : rien à ajouter (exemples vides)
            pass

df.to_csv(OUTPUT, sep=";", index=False)
print(f"✅ Fichier enrichi avec exemples généré : {OUTPUT}")
