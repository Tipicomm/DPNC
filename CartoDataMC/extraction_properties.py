# CartoDataMC/extraction_properties.py

import pandas as pd
import requests
import time

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties_exemples.csv"

df = pd.read_csv(INPUT, sep=";")

# Vérification des colonnes obligatoires
for col in ["resource_id", "property_name", "property_label"]:
    if col not in df.columns:
        raise ValueError("Les colonnes 'resource_id', 'property_name' et 'property_label' sont requises.")

# Ajout des colonnes enrichies si absentes
for col in ["exemple_1", "exemple_2", "exemple_3", "format_inferé", "python_type", "nb_distinct", "nb_missing_values"]:
    if col not in df.columns:
        df[col] = ""

# Groupement par ressource pour limiter les appels API
grouped = df.groupby("resource_id")

for rid, group in grouped:
    try:
        url = f"https://tabular-api.data.gouv.fr/api/resources/{rid}/profile/"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"❌ Erreur pour {rid} (code {resp.status_code})")
            continue
        profile = resp.json()
        columns_info = profile.get("columns", {})
        profiles_info = profile.get("profile", {})

        for idx, row in group.iterrows():
            label = str(row["property_label"])
            if label not in columns_info:
                print(f"⚠️ '{label}' non trouvé dans le profil de {rid}")
                continue

            col_info = columns_info[label]
            prof_info = profiles_info.get(label, {})

            # Exemples de valeurs
            tops = prof_info.get("tops", [])[:3]
            for i in range(3):
                df.at[idx, f"exemple_{i+1}"] = tops[i].get("value", "") if i < len(tops) else ""

            # Autres métadonnées
            df.at[idx, "format_inferé"] = col_info.get("format", "")
            df.at[idx, "python_type"] = col_info.get("python_type", "")
            df.at[idx, "nb_distinct"] = prof_info.get("nb_distinct", "")
            df.at[idx, "nb_missing_values"] = prof_info.get("nb_missing_values", "")

    except Exception as e:
        print(f"⚠️ Exception pour {rid} : {e}")
    time.sleep(0.4)  # éviter de surcharger l’API

# Export final
df.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
print("✅ Fichier enrichi :", OUTPUT)
