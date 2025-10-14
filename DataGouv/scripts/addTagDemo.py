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

# Récupération du dataset avec le client (lecture)
dataset = client.dataset(DATASET_ID)
title = getattr(dataset, "title", None) or getattr(dataset, "name", None)
tags = getattr(dataset, "tags", []) or []

print(f"🎭 Dataset : {title}")
print(f"🔖 Tags actuels : {tags}")

# ───────────────────────────────
# Préparation des nouveaux tags
# ───────────────────────────────
if TAG in tags:
    print(f"ℹ️ Le tag '{TAG}' est déjà présent.")
else:
    new_tags = tags + [TAG]
    print(f"➕ Ajout du tag '{TAG}' → {new_tags}")

    if DRY_RUN:
        print("🧪 DRY-RUN activé : aucune modification envoyée.")
    else:
        # On recharge le dataset complet (JSON brut)
        url = f"{BASE_URL}/datasets/{DATASET_ID}/"
        headers = {
            "X-API-KEY": API_KEY,
            "Accept": "application/json",
        }
        full_dataset = requests.get(url, headers=headers).json()

        # On met à jour les tags dans le JSON complet
        full_dataset["tags"] = new_tags

        # PUT avec authentification (et sans perdre les autres champs)
        put_headers = {
            "X-API-KEY": API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        print("🚀 Envoi de la mise à jour...")
        response = requests.put(url, headers=put_headers, data=json.dumps(full_dataset))

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
