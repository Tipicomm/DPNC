# -*- coding: utf-8 -*-
import pandas as pd
import csv
from pathlib import Path

DOSSIER = "CartoDataMC"
FICHIER_ENTREE = f"{DOSSIER}/cartographie_ressources_datasets.csv"
FICHIER_SORTIE = f"{DOSSIER}/cartographie_culture_properties.csv"

# Chargement avec séparateur virgule
df = pd.read_csv(FICHIER_ENTREE, sep=",", encoding="utf-8")

# Colonnes attendues
assert "id.ressource" in df.columns
assert "id.dataset" in df.columns
assert "title.dataset" in df.columns

# Liste pour les résultats
proprietes = []

# Boucle sur chaque ressource
for _, row in df.iterrows():
    resource_id = row["id.ressource"]
    dataset_id = row["id.dataset"]
    dataset_title = row["title.dataset"]

    try:
        url = f"https://tabular-api.data.gouv.fr/api/resources/{resource_id}/profile/"
        profil = pd.read_json(url)

        if "columns" not in profil["profile"]:
            continue

        for prop, metadata in profil["profile"]["columns"].items():
            propriete = {
                "resource_id": resource_id,
                "dataset_id": dataset_id,
                "dataset_title": dataset_title,
                "property_name": prop,
                "property_label": prop,  # on conserve la même pour l’instant
                "property_type": metadata.get("python_type", ""),
                "property_format": metadata.get("format", ""),
            }
            proprietes.append(propriete)

    except Exception as e:
        print(f"⚠️ Erreur pour {resource_id} : {e}")

# Export
df_props = pd.DataFrame(proprietes)
df_props.to_csv(FICHIER_SORTIE, sep=";", index=False, encoding="utf-8")
print(f"✅ Propriétés extraites et enregistrées dans : {FICHIER_SORTIE}")
