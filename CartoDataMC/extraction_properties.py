# -*- coding: utf-8 -*-
import pandas as pd
from collections import Counter

INPUT = "CartoDataMC/cartographie_ressources_datasets.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties.csv"

df = pd.read_csv(INPUT, sep=";")

# Correction du nom de colonne fusionné
if "title.dataset_x" in df.columns and "title.dataset_y" in df.columns:
    df["title.dataset"] = df["title.dataset_x"]
elif "title.dataset_x" in df.columns:
    df.rename(columns={"title.dataset_x": "title.dataset"}, inplace=True)
elif "title.dataset_y" in df.columns:
    df.rename(columns={"title.dataset_y": "title.dataset"}, inplace=True)

# Préparation d’une structure pour stocker les propriétés
records = []

for (rid, dataset_id), group in df.groupby(["resource_id", "dataset_id"]):
    # Liste des en-têtes (properties)
    try:
        headers = eval(group.iloc[0]["headers"])  # format ["col1", "col2", ...]
        for col in headers:
            records.append({
                "property_name": col,
                "resource_id": rid,
                "dataset_id": dataset_id,
                "title.dataset": group.iloc[0].get("title.dataset", ""),
                "title.resource": group.iloc[0].get("title.resource", "")
            })
    except Exception as e:
        print(f"Erreur parsing headers pour {rid} : {e}")

# Création du DataFrame de sortie
out_df = pd.DataFrame(records)

# Sauvegarde
out_df.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
print("✅ Fichier des propriétés extrait :", OUTPUT)
