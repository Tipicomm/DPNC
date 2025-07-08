# -*- coding: utf-8 -*-
import pandas as pd
import requests
import csv
import os

INPUT = "CartoDataMC/cartographie_ressources_datasets.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties.csv"

# Tentative de lecture avec différents séparateurs
separators = [";", ",", "\t"]
for sep in separators:
    try:
        df = pd.read_csv(INPUT, sep=sep, quotechar='"', encoding="utf-8", dtype=str)
        if df.shape[1] > 1:
            break
    except Exception:
        continue
else:
    print("❌ Impossible de lire le fichier avec les séparateurs classiques (; , tabulation).")
    exit(1)

# Vérification et renommage des colonnes
if "title.dataset" not in df.columns:
    if "title.dataset_x" in df.columns:
        df = df.rename(columns={"title.dataset_x": "title.dataset"})
    elif "title" in df.columns:
        df = df.rename(columns={"title": "title.dataset"})
    else:
        raise ValueError("⚠️ Colonne 'title.dataset' introuvable.")

if "id.ressource" not in df.columns:
    raise ValueError("⚠️ Colonne 'id.ressource' introuvable.")

# Filtrage des ressources
df = df.dropna(subset=["id.ressource", "title.dataset"])
df = df.drop_duplicates(subset=["id.ressource", "title.dataset"])

# Extraction des propriétés
liste_props = []

for _, row in df.iterrows():
    rid = row["id.ressource"]
    titre = row["title.dataset"]

    url = f"https://tabular-api.data.gouv.fr/api/resources/{rid}/profile/"
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print(f"❌ Profil non disponible pour {rid} ({r.status_code})")
            continue

        profile = r.json()
        colonnes = profile.get("columns", {})

        for nom_col, infos in colonnes.items():
            liste_props.append({
                "resource_id": rid,
                "property_label": nom_col,
                "property_name": nom_col.lower().replace(" ", "_"),
                "python_type": infos.get("python_type", ""),
                "format_inferé": infos.get("format", ""),
                "dataset_title": titre
            })

    except Exception as e:
        print(f"⚠️ Erreur pour la ressource {rid} → {e}")
        continue

# Sauvegarde du résultat
df_props = pd.DataFrame(liste_props)
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
df_props.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
print(f"✅ Fichier des propriétés généré : {OUTPUT}")
