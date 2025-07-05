import pandas as pd
import requests
import io  # requis pour la lecture en mémoire

### 🔹 1. Ressources du ministère (datasets-resources.csv)
url_ressources = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets-resources.csv"
response_ressources = requests.get(url_ressources)
response_ressources.encoding = "utf-8"

try:
    df_ressources = pd.read_csv(io.StringIO(response_ressources.text), sep=";")
except Exception:
    df_ressources = pd.read_csv(io.StringIO(response_ressources.text), sep=",")

# Filtrer les ressources CSV
df_ressources = df_ressources[df_ressources["format"].str.lower() == "csv"]

# Conserver les colonnes d’intérêt
colonnes_ressources = ["dataset.id", "dataset.title", "id"]
df_ressources = df_ressources[[col for col in colonnes_ressources if col in df_ressources.columns]]

# Enregistrer le fichier final (dans le dossier courant)
df_ressources.to_csv("ressources_culture.csv", index=False)
print("✅ Fichier 'ressources_culture.csv' généré avec succès.")


### 🔹 2. Jeux de données (datasets.csv)
url_datasets = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets.csv"
response_datasets = requests.get(url_datasets)
response_datasets.encoding = "utf-8"

try:
    df_datasets = pd.read_csv(io.StringIO(response_datasets.text), sep=";")
except Exception:
    df_datasets = pd.read_csv(io.StringIO(response_datasets.text), sep=",")

# Conserver uniquement certaines colonnes
colonnes_datasets = ["id", "title", "description", "tag"]
df_datasets = df_datasets[[col for col in colonnes_datasets if col in df_datasets.columns]]

# Enregistrer le fichier final (dans le dossier courant)
df_datasets.to_csv("datasets_culture.csv", index=False)
print("✅ Fichier 'datasets_culture.csv' généré avec succès.")
