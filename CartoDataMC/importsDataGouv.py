# -*- coding: utf-8 -*-

import pandas as pd
import requests
import io
import csv  # nécessaire pour le quoting

# 📁 Dossier de destination
DOSSIER = "CartoDataMC"

### 1️⃣ Télécharger les ressources du ministère

url_ressources = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets-resources.csv"
response_ressources = requests.get(url_ressources)
response_ressources.encoding = "utf-8"

try:
    df_ressources = pd.read_csv(io.StringIO(response_ressources.text), sep=";")
except Exception:
    df_ressources = pd.read_csv(io.StringIO(response_ressources.text), sep=",")

df_ressources = df_ressources[df_ressources["format"].str.lower() == "csv"]

colonnes_utiles_ressources = ["id", "dataset.id", "dataset.title"]
df_ressources = df_ressources[[col for col in colonnes_utiles_ressources if col in df_ressources.columns]]

df_ressources = df_ressources.rename(columns={
    "id": "id.ressource",
    "dataset.id": "id.dataset",
    "dataset.title": "title.dataset"
})

df_ressources.to_csv(
    f"{DOSSIER}/ressources_culture.csv",
    index=False,
    sep=";",
    quoting=csv.QUOTE_ALL
)
print("✅ ressources_culture.csv sauvegardé")


### 2️⃣ Télécharger les jeux de données du ministère

url_datasets = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets.csv"
response_datasets = requests.get(url_datasets)
response_datasets.encoding = "utf-8"

try:
    df_datasets = pd.read_csv(io.StringIO(response_datasets.text), sep=";")
except Exception:
    df_datasets = pd.read_csv(io.StringIO(response_datasets.text), sep=",")

colonnes_utiles_datasets = ["id", "title", "description", "tags"]
df_datasets = df_datasets[[col for col in colonnes_utiles_datasets if col in df_datasets.columns]]

df_datasets = df_datasets.rename(columns={
    "id": "id.dataset",
    "title": "title.dataset",
    "description": "description.dataset",
    "tags": "tags.dataset"
})

df_datasets.to_csv(
    f"{DOSSIER}/datasets_culture.csv",
    index=False,
    sep=";",
    quoting=csv.QUOTE_ALL
)
print("✅ datasets_culture.csv sauvegardé")


### 3️⃣ Fusionner les deux

df_jointure = pd.merge(df_ressources, df_datasets, on="id.dataset", how="left")

print(f"🔍 Colonnes fusionnées : {df_jointure.columns.tolist()}")
print(f"🔢 Nombre total de lignes : {len(df_jointure)}")

df_jointure.to_csv(
    f"{DOSSIER}/cartographie_ressources_datasets.csv",
    index=False,
    sep=";",
    quoting=csv.QUOTE_ALL
)
print("✅ cartographie_ressources_datasets.csv généré avec succès")
