"""
But : Sauvegarder le JSON complet de tous les jeux de données d'une organisation DataGouv (API /api/1/datasets/{id}/).

Ce script interroge directement l’API REST publique (aucune clé API requise)
et sauvegarde le contenu complet de chaque dataset dans un fichier JSON global.

Remarque importante :
Le client officiel `datagouv-client` n’expose qu’une partie des champs (voir `Dataset._attributes`).
Certaines propriétés du JSON complet (ex. frequency, license, private, quality, etc.)
ne sont pas disponibles via le client Python, d’où l’usage direct de l’API REST.
"""

import os
import json
import requests
from datagouv import Client
from datetime import datetime

# ───────────────────────────────
# Configuration
# ───────────────────────────────
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture

# Environnement (demo, www, dev)
ENVIRONMENT = os.getenv("DATAGOUV_ENV", "demo").lower()

BASE_URL = {
    "www": "https://www.data.gouv.fr",
    "demo": "https://demo.data.gouv.fr",
    "dev": "https://dev.data.gouv.fr"
}.get(ENVIRONMENT, "https://demo.data.gouv.fr")

# Nom dynamique du fichier
DATE_STR = datetime.utcnow().strftime("%Y_%m_%d")
OUTPUT_DIR = "DataGouv/scripts/backup"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"backup_datasets_full_{ENVIRONMENT}_{DATE_STR}.json")

print("───────────────────────────────")
print(f"🟢 Environnement : {ENVIRONMENT.upper()}")
print("🔓 Mode : public (aucune clé API requise)")
print(f"🏛️ Organisation ciblée : {ORG_ID}")
print(f"📁 Fichier de sortie prévu : {OUTPUT_PATH}")
print("───────────────────────────────\n")

# ───────────────────────────────
# Initialisation du client
# ───────────────────────────────
print(f"Connexion à l’environnement {ENVIRONMENT.upper()} (accès public)...")
client = Client(environment=ENVIRONMENT)
organization = client.organization(ORG_ID)

# ───────────────────────────────
# Préparation du fichier de sauvegarde
# ───────────────────────────────
backup = {
    "organization": ORG_ID,
    "environment": ENVIRONMENT,
    "date": datetime.utcnow().isoformat(),
    "datasets": {}
}

session = requests.Session()

# ───────────────────────────────
# Boucle principale
# ───────────────────────────────
for ds in organization.datasets:
    ds_id = getattr(ds, "id", None) or getattr(ds, "dataset_id", None)
    if not ds_id:
        print("⚠️  Dataset sans identifiant, ignoré.")
        continue

    try:
        url = f"{BASE_URL}/api/1/datasets/{ds_id}/"
        response = session.get(url, timeout=10)
        response.raise_for_status()
        metadata = response.json()
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du dataset {ds_id}: {e}")
        continue

    backup["datasets"][ds_id] = metadata
    print(f"💾 Sauvegarde complète du dataset : {metadata.get('title', 'inconnu')} ({ds_id})")

# ───────────────────────────────
# Écriture du fichier
# ───────────────────────────────
backup["count"] = len(backup["datasets"])

try:
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(backup, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Sauvegarde complète créée : {OUTPUT_PATH}")
except Exception as e:
    print(f"❌ Erreur lors de l’écriture du fichier : {e}")
    raise

# ───────────────────────────────
# Bilan
# ───────────────────────────────
print("\n───────────── BILAN FINAL ─────────────")
print(f"📦 {backup['count']} jeux de données sauvegardés.")
print(f"🏛️ Organisation : {ORG_ID}")
print(f"🌍 Environnement : {ENVIRONMENT}")
print(f"📁 Fichier : {OUTPUT_PATH}")
print("────────────────────────────────────────")
