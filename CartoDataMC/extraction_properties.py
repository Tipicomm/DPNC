# -*- coding: utf-8 -*-
import pandas as pd
import requests
import time

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties_exemples.csv"

df = pd.read_csv(INPUT, sep=";")

# Vérifie la présence des colonnes nécessaires
if "resource_id" not in df.columns or "property_label" not in df.columns:
    raise ValueError("Les colonnes 'resource_id' et 'property_label' sont requises.")

# Ajoute les colonnes vides si elles n'existent pas
colonnes_enrichies = ["exemple_1", "exemple_2", "exemple_3", "format_inferé", "python_type", "nb_distinct", "nb_missing_values"]
for col in colonnes_enrichies:
    if col not in df.columns:
        df[col] = ""

# Regroupement par ressource pour limiter les appels
grouped = df.groupby("resource_id")

for rid, group in grouped:
    try:
        url = f"https://tabular-api.data.gouv.fr/api/resources/{rid}/profile/"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"❌ Échec pour {rid} (code {resp.status_code})")
            continue

        profile = resp.json().get("profile", {})
        colonnes = profile.get("columns", {})
        statistiques = profile.get("profile", {})

        for idx, row in group.iterrows():
            prop_label = row["property_label"]
            if prop_label not in colonnes:
                print(f"⚠️ '{prop_label}' absent de {rid}")
                continue

            df.at[idx, "format_inferé"] = colonnes[prop_label].get("format", "")
            df.at[idx, "python_type"] = colonnes[prop_label].get("python_type", "")
            stats = statistiques.get(prop_label, {})
            df.at[idx, "nb_distinct"] = stats.get("nb_distinct", "")
            df.at[idx, "nb_missing_values"] = stats.get("nb_missing_values", "")

            # Exemples de valeurs
            tops = stats.get("tops", [])
            for i in range(3):
                if i < len(tops):
                    df.at[idx, f"exemple_{i+1}"] = tops[i].get("value", "")
                else:
                    df.at[idx, f"exemple_{i+1}"] = ""

    except Exception as e:
        print(f"⚠️ Erreur pour {rid} → {e}")
    time.sleep(0.5)

# Sauvegarde
df.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
print("✅ Fichier enrichi généré :", OUTPUT)
