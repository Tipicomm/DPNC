# -*- coding: utf-8 -*-
import pandas as pd
import requests
import time

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties_exemples.csv"

df = pd.read_csv(INPUT, sep=";")

# Colonnes à créer si absentes
for col in ["exemple_1", "exemple_2", "exemple_3", "format_inferé", "python_type", "nb_distinct", "nb_missing_values"]:
    if col not in df.columns:
        df[col] = ""

grouped = df.groupby("resource_id")

for rid, group in grouped:
    try:
        profile_url = f"https://tabular-api.data.gouv.fr/api/resources/{rid}/profile/"
        resp = requests.get(profile_url)
        if resp.status_code == 200:
            profile_data = resp.json()
            colonnes = profile_data.get("columns", {})
            profils = profile_data.get("profile", {})

            for idx, row in group.iterrows():
                prop = row["property_name"]
                col_info = colonnes.get(prop, {})
                prof_info = profils.get(prop, {})

                top_vals = prof_info.get("tops", [])[:3]
                for i, val in enumerate(top_vals):
                    df.loc[idx, f"exemple_{i+1}"] = val["value"]

                df.loc[idx, "format_inferé"] = col_info.get("format", "")
                df.loc[idx, "python_type"] = col_info.get("python_type", "")
                df.loc[idx, "nb_distinct"] = prof_info.get("nb_distinct", "")
                df.loc[idx, "nb_missing_values"] = prof_info.get("nb_missing_values", "")
        else:
            print(f"❌ Échec pour {rid} (code {resp.status_code})")
    except Exception as e:
        print(f"⚠️ Erreur pour {rid} → {e}")
    time.sleep(0.5)

df.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
print("✅ Fichier enrichi avec typage et statistiques :", OUTPUT)
