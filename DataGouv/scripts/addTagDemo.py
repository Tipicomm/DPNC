import os
import json
import requests
from datagouv import Client

# ───────────────────────────────
# Configuration
# ───────────────────────────────
API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")
DATASET_ID = "67fe79efd6a64f5bb533e454"  # Dataset "Hello Lido"
TAG = "culture"
SAFE_BACKUP = True  # Crée un fichier de sauvegarde avant modification
DRY_RUN = False     # True = test sans écriture
BASE_URL = "https://demo.data.gouv.fr/api/1"

# ───────────────────────────────
# Connexion au client DataGouv (environnement DEMO)
# ───────────────────────────────
client = Client(environment="demo", api_key=API_KEY)
print("🧩 Connexion à l'environnement DEMO")

# ───────────────────────────────
# Récupération du dataset via le client
# ───────────────────────────────
dataset = client.dataset(DATASET_ID)
title = getattr(dataset, "title", None) or getattr(dataset, "name", None)
tags = getattr(dataset, "tags", []) or []

print(f"🎭 Dataset : {title}")
print(f"🔖 Tags actuels : {tags}")

# ───────────────────────────────
# Sauvegarde de sécurité avant écriture
# ───────────────────────────────
if SAFE_BACKUP:
    backup_path = f"DataGouv/scripts/backup_{DATASET_ID}.json"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(dataset.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"💾 Sauvegarde de sécurité créée : {backup_path}")

# ───────────────────────────────
# Ajout du tag sans perte de données
# ───────────────────────────────
if TAG in tags:
    print(f"ℹ️ Le tag '{TAG}' est déjà présent.")
else:
    new_tags = tags + [TAG]
    print(f"➕ Ajout du tag '{TAG}' → {new_tags}")

    if DRY_RUN:
        print("🧪 DRY-RUN activé : aucune modification envoyée.")
    else:
        # 1️⃣ Récupérer le dataset complet pour ne rien perdre
        url = f"{BASE_URL}/datasets/{DATASET_ID}/"
        headers = {
            "X-API-KEY": API_KEY,
            "Accept": "application/json",
        }
        full = requests.get(url, headers=headers).json()

        # 2️⃣ Modifier uniquement les tags
        full["tags"] = new_tags

        # 3️⃣ Envoyer l’objet complet en PUT (authentifié)
        put_headers = {
            "X-API-KEY": API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = requests.put(url, headers=put_headers, data=json.dumps(full))

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
