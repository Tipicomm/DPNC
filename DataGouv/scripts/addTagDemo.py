import os
from datagouv import Client

API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")
DATASET_ID = "67fe79efd6a64f5bb533e454"  # ID du dataset "Hello Lido"
TAG = "culture"
DRY_RUN = False  # Passe à False pour appliquer vraiment la modification

# Connexion à l'environnement de démo
client = Client(environment="demo", api_key=API_KEY)

print("🧩 Connexion à l'environnement DEMO")
print(f"Traitement du dataset : {DATASET_ID}")

# Récupération du dataset
dataset = client.dataset(DATASET_ID)
title = getattr(dataset, "title", None) or getattr(dataset, "name", None)
tags = getattr(dataset, "tags", []) or []

print(f"Titre : {title}")
print(f"Tags actuels : {tags}")

# Ajout du tag s’il n’est pas déjà présent
if TAG not in tags:
    new_tags = tags + [TAG]
    print(f"➕ Ajout du tag '{TAG}' → {new_tags}")

    if not DRY_RUN:
        dataset.update({"tags": new_tags})
        print("✅ Tag ajouté avec succès (environnement DEMO).")
    else:
        print("🧪 DRY-RUN activé : aucune modification envoyée.")
else:
    print(f"ℹ️ Le tag '{TAG}' est déjà présent.")
