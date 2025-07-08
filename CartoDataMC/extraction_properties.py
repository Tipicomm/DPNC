# -*- coding: utf-8 -*-
import pandas as pd
import os

# 📥 Entrée : fichier de jointure datasets + ressources
FICHIER_CSV = "CartoDataMC/cartographie_ressources_datasets.csv"

# 📤 Sortie : propriétés extraites
FICHIER_SORTIE = "CartoDataMC/cartographie_culture_properties.csv"

# 🧪 Nombre de lignes à lire dans chaque fichier pour échantillon
NB_LIGNES = 200

# 📁 Création du dossier si nécessaire
os.makedirs("CartoDataMC", exist_ok=True)

# 🔁 Lecture du fichier principal
df = pd.read_csv(FICHIER_CSV, sep=",", quotechar='"', encoding="utf-8")

# 📄 Préparation d’un tableau pour collecter les propriétés
liste_props = []

# 🔍 Parcours des ressources CSV
for i, row in df.iterrows():
    if not row["id.ressource"]:
        continue
    ressource_id = row["id.ressource"]
    dataset_id = row["id.dataset"]
    titre = row["title.dataset"]

    try:
        url = f"https://tabular-api.data.gouv.fr/api/resources/{ressource_id}/rows/?format=csv&page=1&page_size={NB_LIGNES}"
        temp_df = pd.read_csv(url, sep=None, engine="python", nrows=NB_LIGNES)

        for col in temp_df.columns:
            liste_props.append({
                "resource_id": ressource_id,
                "dataset_id": dataset_id,
                "property_label": col,
                "property_name": col.lower().strip().replace(" ", "_"),
                "title": titre
            })

    except Exception as e:
        print(f"❌ Échec lecture {ressource_id} → {e}")

# 📦 Sauvegarde des propriétés
df_props = pd.DataFrame(liste_props)
df_props = df_props.drop_duplicates()
df_props.to_csv(FICHIER_SORTIE, sep=";", index=False, encoding="utf-8")
print(f"✅ Propriétés extraites et sauvegardées dans : {FICHIER_SORTIE}")
