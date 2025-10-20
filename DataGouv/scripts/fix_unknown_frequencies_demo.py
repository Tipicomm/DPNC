"""
But :
Corriger les jeux de données sur DEMO (https://demo.data.gouv.fr)
dont la fréquence est strictement 'unknown', en la remplaçant par 'punctual'.

⚙️ Fonctionnement :
- Se connecte à l’organisation via la clé API (secrète)
- Parcourt tous les datasets de l’organisation
- Si la fréquence = 'unknown', met à jour en 'punctual'
- Sinon, ne modifie rien
- Enregistre un backup des fréquences initiales
"""

import os
import json
import httpx
from datagouv import Client
from datetime import datetime

# ───────────────────────────────
# Configuration
# ───────────────────────────────
API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")  # clé API DEMO
ORG_ID = "534fff91a3a7292c64a77f73"        # Ministère de la Culture
UPDATE_MODE = True                          # ⚠️ False = simulation / True = écriture réelle
BACKUP_PATH = "DataGouv/scripts/backup/backup_demo_fix_unknown_frequency.json"

# ───────────────────────────────
# Initialisation
# ───────────────────────────────
if not API_KEY:
    raise EnvironmentError("❌ Aucune clé API détectée (DEMO_DATA_GOUV_KEY manquante).")

client = Client(environment="demo", api_key=API_KEY)
print("Connexion à l'environnement DEMO (demo.data.gouv.fr)")
print(f"Organisation ciblée : {ORG_ID}")

organization = client.organization(ORG_ID)
datasets = list(organization.datasets)
total_datasets = len(datasets)

print(f"{total_datasets} jeux de données détectés pour l'organisation.\n")

# ───────────────────────────────
# Préparation du backup
# ───────────────────────────────
os.makedirs(os.path.dirname(BACKUP_PATH), exist_ok=True)
backup = {
    "organization": ORG_ID,
    "date": datetime.now().isoformat(),
    "datasets": {}
}

errors = []
fixed_count = 0
skipped_count = 0

# ───────────────────────────────
# Boucle principale
# ───────────────────────────────
for ds in datasets:
    ds_id = getattr(ds, "id", None)
    title = getattr(ds, "title", None) or getattr(ds, "name", None)
    if not ds_id:
        continue

    try
