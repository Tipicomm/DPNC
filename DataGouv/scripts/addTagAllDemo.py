import os
from datagouv import Client

# Configuration
API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture
TAG = "culture"

# Client authentifié sur la démo
client = Client(environment="demo", api_key=API_KEY)
print("Connexion à l'environnement DEMO")
print(f"Organisation ciblée : {ORG_ID}")

# Récupération de tous les jeux de données de l'organisation
organization = client.organization(ORG_ID)
datasets = list(organization.datasets)  # 👈 Conversion du générateur en liste

print(f"{len(datasets)} jeux de données détectés pour l'organisation.\n")

# Boucle sur chaque dataset
for ds in datasets:
    ds_id = getattr(ds, "id", None)
    title = getattr(ds, "title", None) or getattr(ds, "name", None)
    tags = getattr(ds, "tags", []) or []

    print(f"→ {title} ({ds_id})")
    print(f"   Tags actuels : {tags}")

    if TAG not in tags:
        new_tags = tags + [TAG]
        ds.update({"tags": new_tags})
        print(f"   ✅ Tag ajouté : {TAG}")
    else:
        print(f"   ℹ️ Tag déjà présent : {TAG}")

print("\nTraitement terminé avec succès.")
