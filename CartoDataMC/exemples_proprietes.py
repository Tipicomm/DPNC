# -*- coding: utf-8 -*-
import pandas as pd
import requests
import time
import unicodedata

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties_exemples.csv"

df = pd.read_csv(INPUT, sep=";")

# Ajout des colonnes enrichies si absentes
for col in ["exemple_1", "exemple_2", "exemple_3", "format_inferé", "python_type", "nb_distinct", "nb_missing_values"]:
    if col not in df.columns:
        df[col] = ""

grouped = df.groupby("resource_id")

def normalize(s):
    if not isinstance(s, str):
        return ""
    return unicodedata.normalize('NFKD', s.strip().lower()).encode('ascii', 'ignore').decode()

for rid, group in grouped:
    try:
        profile_url = f"https://tabular-api.data.gouv.fr/api/resources/{rid}/profile/"
        resp = requests.get(profile_url)
        if resp.status_code != 200:
            print(f"❌ Échec pour {rid} (code {resp.status_code})")
            continue

        profile_data = resp.json()
        colonnes = profile_data.get("columns", {})
        profils = profile_data.get("profile", {})

        normalized_keys = {normalize(k): k for k in colonnes.keys()}

        for idx, row in group.iterrows():
            prop = str(row["property_name"])
            norm_prop = normalize(prop)

            if norm_prop not in normalized_keys:
                print(f"⚠️ Propriété '{prop}' non trouvée (normalisée : '{norm_prop}') dans le profil de {rid}")
                continue

            col_name = normalized_keys[norm_prop]
            col_info = colonnes[col_name]
            prof_info = profils.get(col_name, {})

            # Exemples de valeurs
            top_vals = prof_info.get("tops", [])[:3]
            for i in range(3):
                df.at[idx, f"exemple_{i+1}"] = top_vals[i].get("value", "") if i < len(top_vals) else ""

            # Autres informations
            df.at[idx, "format_inferé"] = col_info.get("format", "")
            df.at[idx, "python_type"] = col_info.get("python_type", "")
            df.at[idx, "nb_distinct"] = prof_info.get("nb_distinct", "")
            df.at[idx, "nb_missing_values"] = prof_info.get("nb_missing_values", "")

    except Exception as e:
        print(f"⚠️ Erreur pour {rid} → {e}")
    time.sleep(0.5)

df.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
print("✅ Fichier enrichi avec typage et statistiques :", OUTPUT)
