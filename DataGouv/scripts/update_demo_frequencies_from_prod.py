"""
But :
Synchroniser les fréquences ('frequency') des jeux de données entre la production (www)
et l’environnement de démonstration (demo).

🧭 Règles :
 - Si frequency_prod ≠ frequency_demo → mise à jour sur DEMO
 - Si frequency_prod est 'unknown', '', ou None → ignoré
 - Sauvegarde des modifications appliquées
 - Peut être exécuté en mode simulation (UPDATE_MODE = False)

⚙️ Nécessite :
 - Deux sauvegardes locales : backup_datasets_full_www_*.json & backup_datasets_full_demo_*.json
 - Une clé API valide pour DEMO (DEMO_DATA_GOUV_KEY)
"""

import os
import json
from datagouv import Client
import httpx
from datetime import datetime

# ───────────────────────────────
# Configuration
# ───────────────────────────────
API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture
UPDATE_MODE = True  # ⚠️ False = simulation / True = écriture réelle
BACKUP_PATH = "DataGouv/scripts/backup/backup_demo_frequency_updates.json"

# Sauvegardes locales
BACKUP_WWW = "DataGouv/scripts/backup/backup_datasets_full_www_2025_10_20.json"
BACKUP_DEMO = "DataGouv/scripts/backup/backup_datasets_full_demo_2025_10_20.json"

# ───────────────────────────────
# Chargement des fichiers
# ───────────────────────────────
def load_datasets(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("datasets", {})
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {path}: {e}")
        return {}

print("───────────────────────────────")
print("📦 Chargement des sauvegardes...")
www_datasets = load_datasets(BACKUP_WWW)
demo_datasets = load_datasets(BACKUP_DEMO)

print(f"📁 WWW (prod) : {len(www_datasets)} jeux de données")
print(f"📁 DEMO       : {len(demo_datasets)} jeux de données")

# ───────────────────────────────
# Initialisation du client
# ───────────────────────────────
if not API_KEY:
    raise ValueError("❌ Clé API manquante : définis DEMO_DATA_GOUV_KEY dans les secrets GitHub")

client = Client(environment="demo", api_key=API_KEY)
organization = client.organization(ORG_ID)
print(f"Connexion à DEMO — Organisation : {ORG_ID}\n")

# ───────────────────────────────
# Comparaison et détection des cas à corriger
# ───────────────────────────────
common_ids = set(www_datasets.keys()) & set(demo_datasets.keys())
to_fix = []

for ds_id in common_ids:
    freq_www = (www_datasets[ds_id].get("frequency") or "").strip().lower()
    freq_demo = (demo_datasets[ds_id].get("frequency") or "").strip().lower()

    if not freq_www or freq_www in ("unknown", "null"):
        continue  # on ignore les cas où la fréquence prod n’est pas définie

    if freq_www != freq_demo:
        title = demo_datasets[ds_id].get("title") or www_datasets[ds_id].get("title")
        to_fix.append((ds_id, title, freq_demo, freq_www))

print(f"🔍 {len(to_fix)} datasets à mettre à jour sur DEMO (toutes fréquences sauf 'unknown')\n")

# ───────────────────────────────
# Préparation du backup
# ───────────────────────────────
os.makedirs(os.path.dirname(BACKUP_PATH), exist_ok=True)
backup = {
    "organization": ORG_ID,
    "date": datetime.now().isoformat(),
    "total_to_update": len(to_fix),
    "datasets": []
}

errors = []
updated_count = 0

# ───────────────────────────────
# Boucle principale de mise à jour
# ───────────────────────────────
for ds_id, title, freq_demo, freq_www in to_fix:
    print(f"→ {title} ({ds_id})")
    print(f"   DEMO : {freq_demo or '∅'} → PROD : {freq_www}")

    backup["datasets"].append({
        "id": ds_id,
        "title": title,
        "old_frequency": freq_demo,
        "new_frequency": freq_www
    })

    if UPDATE_MODE:
        try:
            ds = client.dataset(ds_id)
            ds.update({"frequency": freq_www})
            print(f"   ✅ Fréquence mise à jour sur DEMO → {freq_www}")
            updated_count += 1
        except httpx.HTTPStatusError as e:
            print(f"   ❌ Erreur {e.response.status_code} : {e.response.text[:120]}…")
            errors.append({"id": ds_id, "title": title, "error": str(e)})
        except Exception as e:
            print(f"   ⚠️ Erreur inattendue : {e}")
            errors.append({"id": ds_id, "title": title, "error": str(e)})
    else:
        print("   (Simulation) Aucune écriture réelle effectuée.")
        updated_count += 1

# ───────────────────────────────
# Sauvegarde du backup
# ───────────────────────────────
backup["updated_count"] = updated_count
backup["error_count"] = len(errors)

with open(BACKUP_PATH, "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print(f"\n🗃️ Backup sauvegardé dans {BACKUP_PATH}")

# ───────────────────────────────
# Bilan
# ───────────────────────────────
print("\n───────────────────────────────")
print("Bilan du traitement")
print("───────────────────────────────")
print(f"Total datasets analysés   : {len(common_ids)}")
print(f"Total à corriger          : {len(to_fix)}")
print(f"Mises à jour effectuées   : {updated_count}")
print(f"Erreurs rencontrées       : {len(errors)}")
print(f"Mode appliqué : {'ÉCRITURE RÉELLE' if UPDATE_MODE else 'SIMULATION'}")
print("───────────────────────────────")
