# -*- coding: utf-8 -*-
import pandas as pd
import requests
import time

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties_exemples.csv"

df = pd.read_csv(INPUT, sep=";")

# Vérification des colonnes requises
required_columns = ["resource_id", "property_name"]
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"La colonne '{col}' est requise dans le fichier d'entrée.")

# Ajouter la colonne 'property_label' si absente
if "property_label" not in df.columns:
    print("Ajout automatique de la colonne 'property_label' à partir de 'property_name'")
    df["property_label"] = df["property_name"]

# Ajout des colonnes enrichies si absentes
for col in ["exemple_1", "exemple_2", "exemple_3", "format_inferé", "python_type", "nb_distinct", "nb_missing_values"]:
    if col not in df.columns:
        df[col] = ""

grouped = df.groupby("resource_id")

for rid, group in grouped:
    try:
        profile_url = f"https://tabular-api.data.gouv.fr/api/resources/{rid}/profile/"
        resp = requests.get(profile_url)
        if resp.status_code != 200:
            print(f"❌ Échec pour {rid} (code {resp.status_code})")
            continue

        profile_data = resp.json()
        columns_data = profile_data.get("columns", {})
        profile_stats = profile_data.get("profile", {})

        for idx, row in group.iterrows():
            label = str(row["property_label"])
            if label not in columns_data:
                print(f"⚠️ Libellé '{label}' non trouvé dans le profil de {rid}")
                continue

            col_info = columns_data[label]
            prof_info = profile_stats.get(label, {})

            # Exemples de valeurs
            top_vals = prof_info.get("tops", [])[:3]
            for i in range(3):
                df.at[idx, f"exemple_{i+1}"] = top_vals[i]["value"] if i < len(top_vals) else ""

            # Autres métadonnées
            df.at[idx, "format_inferé"] = col_info.get("format", "")
            df.at[idx, "python_type"] = col_info.get("python_type", "")
            df.at[idx, "nb_distinct"] = prof_info.get("nb_distinct", "")
            df.at[idx, "nb_missing_values"] = prof_info.get("nb_missing_values", "")

    except Exception as e:
        print(f"⚠️ Erreur pour {rid} → {e}")
    time.sleep(0.5)

df.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
print("✅ Fichier enrichi avec typage et statistiques :", OUTPUT)
