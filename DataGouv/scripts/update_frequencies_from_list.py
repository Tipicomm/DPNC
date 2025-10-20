"""
But :
Mettre à jour la fréquence ("frequency") des jeux de données listés dans datasets_to_fix.csv,
en remplaçant uniquement la valeur "unknown" par "punctual".

Entrée :
- Fichier CSV généré par list_unknown_frequencies.py :
  DataGouv/scripts/backup/datasets_to_fix.csv

Sortie :
- Fichier JSON de backup : DataGouv/scripts/backup/backup_update_frequencies.json
  Contient le détail des mises à jour effectuées et les éventuelles erreurs.

⚙️ Exemple d’utilisation :
DATAGOUV_ENV=demo python DataGouv/scripts/update_frequencies_from_list.py
ou
DATAGOUV_ENV=prod DATAGOUV_API_KEY=<ta_cle_api> python DataGouv/scripts/update_frequencies_from_list.py
"""

import os
import csv
import json
import httpx
from datagouv import Client
from datetime import datetime

# ───────────────────────────────
# ⚙️ Configuration
# ───────────────────────────────
INPUT_CSV = "DataGouv/scripts/backup/datasets_to_fix.csv"
BACKUP_PATH = "DataGouv/scripts/backup/backup_update_frequencies.json"

NEW_FREQUENCY = "punctual"  # valeur appliquée
UPDATE_MODE = True           # False = simulation
ENVIRONMENT = os.getenv("DATAGOUV_ENV", "demo").lower()

# Clé API selon environnement
if ENVIRONMENT == "prod":
    API_KEY = os.getenv("DATAGOUV_API_KEY")
else:
    API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")

if not API_KEY:
    raise EnvironmentError("❌ Aucune clé API détectée. Vérifie tes secrets GitHub.")

# ───────────────────────────────
# 🔌 Connexion au client
# ───────────────────────────────
print("───────────────────────────────")
print(f"🌍 Environnement : {ENVIRONMENT.upper()}")
print(f"🔑 Clé API détectée : {'✅ Oui' if API_KEY else '❌ Non'}")
print("───────────────────────────────")

client = Client(environment=ENVIRONMENT, api_key=API_KEY)

# ───────────────────────────────
# 📂 Lecture du CSV
# ───────────────────────────────
if not os.path.exists(INPUT_CSV):
    raise FileNotFoundError(f"❌ Fichier CSV introuvable : {INPUT_CSV}")

datasets_to_fix = []
with open(INPUT_CSV, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get("id"):
            datasets_to_fix.append(row)

print(f"📋 {len(datasets_to_fix)} datasets à mettre à jour (source : {INPUT_CSV})\n")

# ───────────────────────────────
# 🧾 Backup initial
# ───────────────────────────────
os.makedirs(os.path.dirname(BACKUP_PATH), exist_ok=True)
backup = {
    "environment": ENVIRONMENT,
    "date": datetime.utcnow().isoformat(),
    "new_frequency": NEW_FREQUENCY,
    "update_mode": "REAL" if UPDATE_MODE else "SIMULATION",
    "datasets": [],
    "errors": []
}

# ───────────────────────────────
# 🔁 Boucle principale
# ───────────────────────────────
for ds in datasets_to_fix:
    ds_id = ds["id"]
    title = ds["title"]

    print(f"→ {title} ({ds_id})")

    try:
        dataset = client.dataset(ds_id)
        current_freq = getattr(dataset, "frequency", None)

        print(f"   Fréquence actuelle : {current_freq or '∅'}")

        if UPDATE_MODE:
            dataset.update({"frequency": NEW_FREQUENCY})
            print(f"   ✅ Fréquence mise à jour → '{NEW_FREQUENCY}'")
        else:
            print(f"   (Simulation) Fréquence serait mise à jour → '{NEW_FREQUENCY}'")

        backup["datasets"].append({
            "id": ds_id,
            "title": title,
            "old_frequency": current_freq,
            "new_frequency": NEW_FREQUENCY,
            "status": "updated" if UPDATE_MODE else "simulated"
        })

    except httpx.HTTPStatusError as e:
        print(f"   ❌ Erreur HTTP {e.response.status_code} : {e.response.text[:120]}…")
        backup["errors"].append({"id": ds_id, "title": title, "error": str(e)})
    except Exception as e:
        print(f"   ⚠️ Erreur inattendue : {e}")
        backup["errors"].append({"id": ds_id, "title": title, "error": str(e)})

print("\n───────────────────────────────")
print("💾 Sauvegarde du rapport de mise à jour...")
with open(BACKUP_PATH, "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print(f"✅ Rapport créé : {BACKUP_PATH}")
print(f"📊 Datasets mis à jour : {len(backup['datasets'])}")
print(f"⚠️ Erreurs détectées : {len(backup['errors'])}")
print("───────────────────────────────")
