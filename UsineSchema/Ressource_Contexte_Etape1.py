# -*- coding: utf-8 -*-
import requests
import pandas as pd
import csv
import os

# Paramètres
DATASET_ID = "6842b8e772325215e9dbf196"
RESOURCE_ID = "ad59533c-1c18-4eb4-a079-7e061ec5dbcd"

# 1. Récupération des métadonnées du dataset
url_dataset = f"https://demo.data.gouv.fr/api/1/datasets/{DATASET_ID}/"
resp_ds = requests.get(url_dataset)
dataset = resp_ds.json()
title_dataset = dataset.get("title", "")
description_dataset = dataset.get("description", "")
tags_dataset = dataset.get("tags", [])

# 2. Récupération du profil tabulaire de la ressource
url_profile = f"https://tabular-api.preprod.data.gouv.fr/api/resources/{RESOURCE_ID}/profile/"
resp_profile = requests.get(url_profile)
profile = resp_profile.json().get("profile", {})

header = profile.get("header", [])
columns = profile.get("columns", {})
stats = profile.get("profile", {})

# 3. Extraction colonnes et stats
lignes = []
for nom_col in header:
    col_meta = columns.get(nom_col, {})
    col_stats = stats.get(nom_col, {})
    tops = col_stats.get("tops", [])

    ligne = {
        "id.dataset": DATASET_ID,
        "id.ressource": RESOURCE_ID,
        "title.dataset": title_dataset,
        "description.dataset": description_dataset,
        "tags.dataset": ";".join(tags_dataset),
        "column_name": nom_col,
        "column_datatype": col_meta.get("format", ""),
        "python_type": col_meta.get("python_type", ""),
        "score": col_meta.get("score", ""),
        "nb_distinct": col_stats.get("nb_distinct", ""),
        "nb_missing_values": col_stats.get("nb_missing_values", ""),
        "top_1": tops[0]["value"] if len(tops) > 0 else "",
        "top_2": tops[1]["value"] if len(tops) > 1 else "",
        "top_3": tops[2]["value"] if len(tops) > 2 else "",
        # Champ prévu pour enrichir la définition métier plus tard
        "definition": ""
    }
    lignes.append(ligne)

df_props = pd.DataFrame(lignes)

# 4. Export CSV
# 👉 S'assurer que le dossier existe
os.makedirs("UsineSchema", exist_ok=True)

output_file = f"UsineSchema/schema_{DATASET_ID}_{RESOURCE_ID}.csv"
df_props.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL, quotechar='"', encoding="utf-8")

print(f"✅ Fichier généré : {output_file}")
