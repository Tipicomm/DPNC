# -*- coding: utf-8 -*-
import pandas as pd
import requests
import time

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
OUTPUT = "CartoDataMC/cartographie_culture_properties_exemples.csv"

# Chargement du fichier
df = pd.read_csv(INPUT, sep=";")

# Création de colonnes vides pour les exemples
df["exemple_1"] = ""
df["exemple_2"] = ""
df["exemple_3"] = ""

# Groupe par resource_id pour limiter à un appel par ressource
grouped = df.groupby("resource_id")

# Fonction utilitaire : extrait jusqu’à 3 exemples de valeur pour une propriété
def extraire_exemples(lignes, prop):
    valeurs = []
    for ligne in lignes:
        val = ligne.get(prop)
        if val and val not in valeurs:
            valeurs.append(str(val))
        if len(valeurs) == 3:
            break
    return valeurs + [""] * (3 - len(valeurs))

# Boucle sur chaque resource_id
for rid, group in grouped:
    try:
        url = f"https://tabular-api.data.gouv.fr/api/resources/{rid}/data/?page=1&page_size=50"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()["data"]
            for idx, row in group.iterrows():
                prop = row["property_name"]
                exemples = extraire_exemples(data, prop)
                df.loc[idx, "exemple_1"] = exemples[0]
                df.loc[idx, "exemple_2"] = exemples[1]
                df.loc[idx, "exemple_3"] = exemples[2]
        else:
            print(f"❌ Échec pour {rid} (code {resp.status_code})")
    except Exception as e:
        print(f"⚠️ Erreur pour {rid} → {e}")
    time.sleep(0.5)  # Respecte les quotas de l’API

# Sauvegarde du fichier enrichi
df.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
print("✅ Enrichissement terminé :", OUTPUT)
