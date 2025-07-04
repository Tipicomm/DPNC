import pandas as pd
import requests

# URL de la ressource
url = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets-resources.csv"
fichier_telecharge = "datasets-resources.csv"

# Télécharger le fichier et l’enregistrer localement
response = requests.get(url)
with open(fichier_telecharge, "wb") as f:
    f.write(response.content)

print("📥 Fichier téléchargé et enregistré localement sous 'datasets-resources.csv'.")

# Lire le CSV
df = pd.read_csv(fichier_telecharge, sep=";")

# Filtrer uniquement les ressources CSV (insensible à la casse)
df_csv = df[df["format"].str.lower() == "csv"]

# Ne conserver que les colonnes souhaitées
colonnes_souhaitees = ["dataset.id", "dataset.title", "id"]
df_csv = df_csv[colonnes_souhaitees]

# Enregistrer dans un nouveau fichier
df_csv.to_csv("data/ressources_csv_culture.csv", index=False)

print("✅ Fichier 'ressources_csv_culture.csv' généré avec succès (colonnes filtrées).")
