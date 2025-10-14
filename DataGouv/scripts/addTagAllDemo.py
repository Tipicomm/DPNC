import os
from datagouv import Client

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture (démo)
TAG = "hellodata"

# ------------------------------------------------------------
# Connexion au client Data.gouv (environnement démo)
# ------------------------------------------------------------
client = Client(environment="demo", api_key=API_KEY)
print("Connexion à l'environnement DEMO")
print(f"Organisation ciblée : {ORG_ID}")

# ------------------------------------------------------------
# Récupération de l'organisation et de ses jeux de données
# ------------------------------------------------------------
organization = client.organization(ORG_ID)
datasets = organization.datasets
print(f"{len(datasets)} jeux de données détectés pour l'organisation.")

# ------------------------------------------------------------
# Parcours de tous les jeux de données
# ------------------------------------------------------------
for dataset in datasets:
    title = getattr(dataset, "title", None) or getattr(dataset, "name", None)
    tags = getattr(dataset, "tags", []) or []

    print(f"\n---")
    print(f"Titre : {title}")
    print(f"Tags actuels : {tags}")

    if TAG not in tags:
        print(f"Ajout du tag '{TAG}'...")
        try:
            dataset.update({"tags": tags + [TAG]})
            print(f"Tag ajouté avec succès au dataset '{title}'.")
        except Exception as e:
            print(f"Erreur lors de la mise à jour du dataset '{title}': {e}")
    else:
        print(f"Le tag '{TAG}' est déjà présent dans '{title}'.")

# ------------------------------------------------------------
# Fin du traitement
# ------------------------------------------------------------
print("\nMise à jour terminée pour l'ensemble des jeux de données.")
