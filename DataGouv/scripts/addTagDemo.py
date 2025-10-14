import os
from datagouv import Client

API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")
DATASET_ID = "67fe79efd6a64f5bb533e454"  # "Hello Lido" (démo)
TAG = "hellodata"

# Client authentifié sur l'environnement de démo
client = Client(environment="demo", api_key=API_KEY)

# Récupération du dataset
dataset = client.dataset(DATASET_ID)

# Ajout du tag s'il n'est pas déjà présent (exactement comme préconisé)
if TAG not in dataset.tags:
    dataset.update({"tags": dataset.tags + [TAG]})
    print(f"Tag ajouté: {TAG}")
else:
    print(f"Tag déjà présent: {TAG}")

# Contrôle simple
print("Tags finaux:", dataset.tags)
