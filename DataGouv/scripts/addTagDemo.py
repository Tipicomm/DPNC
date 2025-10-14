import os
from datagouv import Client

# === Configuration ===
API_KEY = os.environ["DATAGOUV_API_KEY"]
BASE_URL = "https://demo.data.gouv.fr"
DATASET_ID = "68c3019f59e15e4d36e65f9b"
TAG = "Culture"

# === Initialisation du client ===
client = Client(api_key=API_KEY, base_url=BASE_URL)

print(f"🧩 Connexion à {BASE_URL}")
print(f"Traitement du dataset : {DATASET_ID}")

# === Récupération complète du dataset ===
dataset = client.dataset(DATASET_ID)
dataset_info = dataset.as_dict() if hasattr(dataset, "as_dict") else dataset.__dict__

# Récupération des tags actuels (préconisation dev)
current_tags = getattr(dataset, "tags", []) or dataset_info.get("tags", []) or []

print(f"Tags actuels : {current_tags}")

# Ajout du tag s’il n’existe pas déjà
if TAG not in current_tags:
    new_tags = current_tags + [TAG]
    print(f"Ajout du tag '{TAG}'…")
    dataset.update({"tags": new_tags})
    print(f"✅ Tag '{TAG}' ajouté avec succès au dataset {DATASET_ID}")
else:
    print(f"ℹ️ Le tag '{TAG}' est déjà présent, aucune modification effectuée.")

# Vérification finale après mise à jour
updated = client.dataset(DATASET_ID)
updated_tags = getattr(updated, "tags", []) or []
print(f"Tags finaux : {updated_tags}")
print("✔️ Fin du traitement sur le dataset de démonstration.")
