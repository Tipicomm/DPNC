# -*- coding: utf-8 -*-
import pandas as pd
import requests
import time

# --- CONFIGURATION
OUTPUT = "CartoDataMC/cartographie_culture_properties_exemples.csv"
BASE_URL = "https://tabular-api.data.gouv.fr"
PAUSE = 0.5  # en secondes entre appels API

# --- PARTIE 1 : extraction des propriétés (identifiant + libellé)
# Supposons que tu as une fonction `get_resources()` qui renvoie la liste des resources.
# Par exemple : [{"resource_id": "...", "property_name": "...", "property_label": "..."}]
resources = get_resources()  # à adapter selon ton code existant

df = pd.DataFrame(resources)
for col in ["exemple_1", "exemple_2", "exemple_3", 
            "format_inferé", "python_type", "nb_distinct", "nb_missing_values"]:
    if col not in df.columns:
        df[col] = ""

# --- PARTIE 2 : enrichissement avec profile
grouped = df.groupby("resource_id")

for rid, group in grouped:
    try:
        resp = requests.get(f"{BASE_URL}/api/resources/{rid}/profile/")
        if resp.status_code != 200:
            print(f"❌ Échec pour {rid} (code {resp.status_code})")
            continue
        pdata = resp.json()
        cols = pdata.get("columns", {})
        profs = pdata.get("profile", {})

        for idx, row in group.iterrows():
            prop_label = row["property_label"]
            if prop_label not in cols:
                print(f"⚠️ Propriété label '{prop_label}' non trouvée pour {rid}")
                continue
            # top 3 valeurs
            tops = profs.get(prop_label, {}).get("tops", [])[:3]
            for i in range(3):
                df.at[idx, f"exemple_{i+1}"] = tops[i]["value"] if i < len(tops) else ""
            # typage et stats
            col_info = cols[prop_label]
            prof_info = profs.get(prop_label, {})
            df.at[idx, "format_inferé"] = col_info.get("format", "")
            df.at[idx, "python_type"] = col_info.get("python_type", "")
            df.at[idx, "nb_distinct"] = prof_info.get("nb_distinct", "")
            df.at[idx, "nb_missing_values"] = prof_info.get("nb_missing_values", "")

    except Exception as e:
        print(f"⚠️ Erreur sur {rid} → {e}")
    time.sleep(PAUSE)

df.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
print("✅ Enrichissement terminé :", OUTPUT)
