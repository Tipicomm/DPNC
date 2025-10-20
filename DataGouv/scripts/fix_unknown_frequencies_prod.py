"""
But :
Corriger uniquement les jeux de données en production (www.data.gouv.fr)
dont la fréquence ('frequency') est strictement 'unknown',
en la remplaçant par 'punctual'.

🧭 Règles :
 - Environnement : PROD (www.data.gouv.fr)
 - Si frequency == 'unknown' → mise à jour → 'punctual'
 - Sinon → inchangé
 - Mode simulation possible (UPDATE_MODE = False)

⚙️ Nécessite :
 - Clé API de production (PROD_DATA_GOUV_KEY)
"""

import os
import json
from datagouv import Client
import httpx
from datetime import datetime

# ───────────────────────────────
# Configuration
# ───────────────────────────────
API_KEY = os.getenv("PROD_DATA_GOUV_KEY")
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture
TARGET_FREQUENCY = "punctual"
UPDATE_MODE = True  # ⚠️ False = simulation / True = écriture réelle
BACKUP_PATH = "DataGouv/scripts/backup/backup_prod_fix_unknown_frequency.json"

# ───────────────────────────────
# Initialisation
# ───────────────────────────────
if not API_KEY:
    raise ValueError("❌ Clé API manquante : définis PROD_DATA_GOUV_KEY dans les secrets GitHub")

client = Client(environment="www", api_key=API_KEY)
print("Connexion à l'environnement PROD (www.data.gouv.fr)")
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
    "environment": "www",
    "date": datetime.now().isoformat(),
    "target_frequency": TARGET_FREQUENCY,
    "datasets": []
}

errors = []
updated_count = 0
skipped_count = 0

# ───────────────────────────────
# Boucle principale
# ───────────────────────────────
for ds in datasets:
    ds_id = getattr(ds, "id", None)
    title = getattr(ds, "title", None) or getattr(ds, "name", None)
    if not ds_id:
        continue

    full_ds = client.dataset(ds_id)
    freq = getattr(full_ds, "frequency", None)
    freq_norm = (freq or "").strip().lower()

    print(f"→ {title} ({ds_id}) — fréquence actuelle : {freq_norm or '∅'}")

    # ✅ Mise à jour uniquement si la fréquence est strictement 'unknown'
    if freq_norm == "unknown":
        backup["datasets"].append({
            "id": ds_id,
            "title": title,
            "old_frequency": freq_norm,
            "new_frequency": TARGET_FREQUENCY
        })

        if UPDATE_MODE:
            try:
                full_ds.update({"frequency": TARGET_FREQUENCY})
                print(f"   ✅ Fréquence corrigée → '{TARGET_FREQUENCY}'")
                updated_count += 1
            except httpx.HTTPStatusError as e:
                print(f"   ❌ Erreur {e.response.status_code} : {e.response.text[:120]}…")
                errors.append({"id": ds_id, "title": title, "error": str(e)})
            except Exception as e:
                print(f"   ⚠️ Erreur inattendue : {e}")
                errors.append({"id": ds_id, "title": title, "error": str(e)})
        else:
            print(f"   (Simulation) Fréquence serait mise à jour → '{TARGET_FREQUENCY}'")
            updated_count += 1
    else:
        skipped_count += 1
        print("   ⏭️ Aucune modification (fréquence différente de 'unknown').")

# ───────────────────────────────
# Sauvegarde du backup
# ───────────────────────────────
backup["count_total"] = total_datasets
backup["count_updated"] = updated_count
backup["count_skipped"] = skipped_count
backup["count_errors"] = len(errors)

with open(BACKUP_PATH, "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print(f"\n🗃️ Backup sauvegardé dans {BACKUP_PATH}")

# ───────────────────────────────
# Bilan
# ───────────────────────────────
print("\n───────────────────────────────")
print("Bilan du traitement")
print("───────────────────────────────")
print(f"Total jeux de données analysés : {total_datasets}")
print(f"Mises à jour effectuées        : {updated_count}")
print(f"Déjà conformes                 : {skipped_count}")
print(f"Erreurs rencontrées            : {len(errors)}")
print(f"Mode appliqué : {'ÉCRITURE RÉELLE' if UPDATE_MODE else 'SIMULATION'}")
print("───────────────────────────────")
