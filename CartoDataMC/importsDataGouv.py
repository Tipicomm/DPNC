# -*- coding: utf-8 -*-

import pandas as pd
import requests
import io  # pour lire les CSV directement en mémoire

### 1️⃣ Télécharger les ressources du ministère (datasets-resources.csv)

url_ressources = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets-resources.csv"
response_ressources = requests.get(url_ressources)
response_ressources.encoding = "utf-8"

try:
    df_ressources = pd.read_csv(io.StringIO(response_ressources.text), sep=";")
except Exception:
    df_ressources = pd.read_csv(io.StringIO(response_ressources.text), sep=",")

# Filtrer uniquement les ressources CSV
df_ressources = df_ressources[df_ressources["format"].str.lower() == "csv"]

# Ne conserver que les colonnes utiles
colonnes_utiles_ressources = ["id", "dataset.id", "dataset.title"]
df_ressources = df_ressources[[col for col in colonnes_utiles_ressources if col in df_ressources.columns]]

# ✅ Renommer les colonnes pour normalisation
df_ressources = df_ressources.rename(columns={
    "id": "id.ressource",
    "dataset.id": "id.dataset",
    "dataset.title": "title.dataset"
})

# 💾 Enregistrer dans le dossier CartoDataMC
df_ressources.to_csv("CartoDataMC/ressources_culture.csv", index=False)
print("✅ ressources_culture.csv sauvegardé")


### 2️⃣ Télécharger les jeux de données (datasets.csv)

url_datasets = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets.csv"
response_datasets = requests.get(url_datasets)
response_datasets.encoding = "utf-8"

try:
    df_datasets = pd.read_csv(io.StringIO(response_datasets.text), sep=";")
except Exception:
    df_datasets = pd.read_csv(io.StringIO(response_datasets.text), sep=",")

# Colonnes utiles
colonnes_utiles_datasets = ["id", "title", "description", "tags"]
df_datasets = df_datasets[[col for col in colonnes_utiles_datasets if col in df_datasets.columns]]

# ✅ Renommer les colonnes pour correspondre à la structure du fichier ressources
df_datasets = df_datasets.rename(columns={
    "id": "id.dataset",
    "title": "title.dataset",
    "description": "description.dataset",
    "tags": "tags.dataset"
})

# 💾 Enregistrer dans le dossier CartoDataMC
df_datasets.to_csv("CartoDataMC/datasets_culture.csv", index=False)
print("✅ datasets_culture.csv sauvegardé")


### 3️⃣ Fusionner les deux fichiers

df_jointure = pd.merge(
    df_ressources,
    df_datasets,
    on="id.dataset",
    how="left"
)

# 💾 Enregistrer la cartographie finale
df_jointure.to_csv("CartoDataMC/cartographie_ressources_datasets.csv", index=False, sep=";")

print("✅ cartographie_ressources_datasets.csv généré avec succès dans CartoDataMC/")
