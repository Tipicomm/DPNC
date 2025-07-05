# -*- coding: utf-8 -*-
import pandas as pd
import requests
import io

### 1️⃣ Télécharger les ressources (datasets-resources.csv)

url_ressources = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets-resources.csv"
response_ressources = requests.get(url_ressources)
response_ressources.encoding = "utf-8"

# Lecture du CSV en mémoire
try:
    df_ressources = pd.read_csv(io.StringIO(response_ressources.text), sep=";")
except Exception:
    df_ressources = pd.read_csv(io.StringIO(response_ressources.text), sep=",")

df_ressources.columns = df_ressources.columns.str.strip()
df_ressources = df_ressources[df_ressources["format"].str.lower() == "csv"]

# Sélectionner les colonnes utiles
df_ressources = df_ressources[["id", "dataset.id", "dataset.title"]].copy()
df_ressources.rename(columns={
    "id": "id.ressource",
    "dataset.id": "id.dataset",
    "dataset.title": "title.dataset"
}, inplace=True)
df_ressources["id.dataset"] = df_ressources["id.dataset"].astype(str)
df_ressources.to_csv("ressources_culture.csv", index=False)
print("✅ ressources_culture.csv sauvegardé")


### 2️⃣ Télécharger les jeux de données (datasets.csv)

url_datasets = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets.csv"
response_datasets = requests.get(url_datasets)
response_datasets.encoding = "utf-8"

try:
    df_datasets = pd.read_csv(io.StringIO(response_datasets.text), sep=";")
except Exception:
    df_datasets = pd.read_csv(io.StringIO(response_datasets.text), sep=",")

df_datasets.columns = df_datasets.columns.str.strip()
df_datasets = df_datasets[["id", "title", "description", "tags"]].copy()
df_datasets.rename(columns={
    "id": "id.dataset",
    "title": "title.dataset",
    "description": "description.dataset",
    "tags": "tags.dataset"
}, inplace=True)
df_datasets["id.dataset"] = df_datasets["id.dataset"].astype(str)
df_datasets.to_csv("datasets_culture.csv", index=False)
print("✅ datasets_culture.csv sauvegardé")


### 3️⃣ Fusion des deux fichiers

df_jointure = pd.merge(df_ressources, df_datasets, on="id.dataset", how="left")

# Nettoyage des doublons de colonnes
if "title.dataset_x" in df_jointure.columns and "title.dataset_y" in df_jointure.columns:
    df_jointure.drop(columns=["title.dataset_x"], inplace=True)
    df_jointure.rename(columns={"title.dataset_y": "title.dataset"}, inplace=True)

# ✅ Export final
df_jointure.to_csv("cartographie_ressources_datasets.csv", index=False, sep=";")
print("✅ cartographie_ressources_datasets.csv généré avec succès")
