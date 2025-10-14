import os
from datagouv import Client

# === Configuration ===
API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")
DATASET_ID = "67fe79efd6a64f5bb533e454"
TAG = "Culture"
DRY_RUN = True  # 🔒 True = affichage uniquement, False = mise à jour effective

# === Initialisation du client ===
client = Client(api_key=API_KEY)
client.base_url = "https://demo.data.gouv.fr"  # ⚠️ sans /api/1/

print(f"🧩 Connexion à {client.base_url}")
print(f"Traitement du dataset : {DATASET_ID}")

# === Récupération du dataset ===
dataset = client.dataset(DATASET_ID)
dataset_info = dataset.as_dict() if hasattr(dataset, "as_dict") else dataset.__dict__

title = getattr(dataset, "title", None) or dataset_info.get("title", "Sans titre")
current_tags = getattr(dataset, "tags", []) or dataset_info.get("tags", []) or []

print(f"Titre du dataset : {title}")
print(f"Tags actuels : {current_tags}")

# === Traitement ===
if TAG in current_tags:
    print(f"ℹ️ Le tag '{TAG}' est déjà présent, aucune modification nécessaire.")
else:
    new_tags = current_tags + [TAG]
    print(f"➕ Ajout du tag '{TAG}' → nouveaux tags : {new_tags}")

    if DRY_RUN:
        print("🧪 Mode DRY-RUN activé : aucune mise à jour envoyée.")
    else:
        dataset.update({"tags": new_tags})
        print(f"✅ Tag '{TAG}' ajouté avec succès au dataset {DATASET_ID}")

# === Vérification finale ===
updated = client.dataset(DATASET_ID)
updated_tags = getattr(updated, "tags", []) or []
print(f"Tags finaux (lecture) : {updated_tags}")
print("✔️ Fin du traitement sur le dataset de démonstration.")
