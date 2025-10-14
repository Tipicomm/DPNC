import os
import json
import requests
from datagouv import Client

# ───────────────────────────────
# Configuration
# ───────────────────────────────
API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")
DATASET_ID = "67fe79efd6a64f5bb533e454"  # "Hello Lido"
TAG = "culture"
DRY_RUN = False
BASE_URL = "https://demo.data.gouv.fr/api/1"

# ───────────────────────────────
# Connexion via le client
# ───────────────────────────────
client = Client(environment="demo", api_key=API_KEY)
print("🧩 Connexion à l'environnement DEMO")

# Lecture du dataset via le client
dataset = client.dataset(DATASET_ID)
title = getattr(dataset, "title", None) or getattr(dataset, "name", None)
tags = getattr(dataset, "tags", []) or []

print(f"🎭 Dataset : {title}")
print(f"🔖 Tags actuels : {tags}")

# ───────────────────────────────
# Si le tag n'existe pas, on l’ajoute
# ───────────────────────────────
if TAG in tags:
    print(f"ℹ️ Le tag '{TAG}' est déjà présent.")
else:
    new_tags = tags + [TAG]
    print(f"➕ Ajout du tag '{TAG}' → {new_tags}")

    if DRY_RUN:
        print("🧪 DRY-RUN activé : aucune modification envoyée.")
    else:
        # ⚙️ Récupération du JSON complet via API REST
        url = f"{BASE_URL}/datasets/{DATASET_ID}/"
        headers = {
            "X-API-KEY": API_KEY,
            "Accept": "application/json",
        }
        dataset_json = requests.get(url, headers=headers).json()

        # 🧩 Mise à jour des tags
        dataset_json["tags"] = new_tags

        # 🚀 Envoi du PUT (remplace .update() !)
        response = requests.put(
            url,
            headers={
                "X-API-KEY": API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            data=json.dumps(dataset_json),
        )

        # ✅ Vérification
        if response.status_code in (200, 201):
            print("✅ Tag ajouté avec succès sans perte de données.")
        else:
            print(f"❌ Erreur PUT {response.status_code}: {response.text}")
            raise SystemExit(1)

# ───────────────────────────────
# Vérification finale
# ───────────────────────────────
check = requests.get(f"{BASE_URL}/datasets/{DATASET_ID}/", headers={"Accept": "application/json"})
if check.ok:
    print(f"🔎 Tags finaux : {check.json().get('tags', [])}")
else:
    print(f"⚠️ Erreur de vérification ({check.status_code})")

print("🏁 Fin du script avec succès.")
