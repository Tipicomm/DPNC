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
DEFAULT_FREQUENCY = "punctual"
UPDATE_MODE = True  # ⚠️ False = simulation / True = écriture réelle
BACKUP_PATH = "DataGouv/scripts/backup_frequencies.json"

# ───────────────────────────────
# Initialisation
# ───────────────────────────────
client = Client(environment="demo", api_key=API_KEY)
print("Connexion à l'environnement DEMO")
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
already_ok_count = 0

# ───────────────────────────────
# Boucle principale
# ───────────────────────────────
for ds in datasets:
    ds_id = getattr(ds, "id", None)
    title = getattr(ds, "title", None) or getattr(ds, "name", None)
    if not ds_id:
        continue

    # recharge complet
    full_ds = client.dataset(ds_id)
    frequency = getattr(full_ds, "frequency", None)

    backup["datasets"][ds_id] = {
        "title": title,
        "frequency": frequency
    }

    print(f"→ {title} ({ds_id})")
    print(f"   Fréquence actuelle : {frequency}")

    if frequency in (None, "unknown", "", "null"):
        if UPDATE_MODE:
            try:
                full_ds.update({"frequency": DEFAULT_FREQUENCY})
                print(f"   ✅ Fréquence corrigée → '{DEFAULT_FREQUENCY}'")
                fixed_count += 1
            except httpx.HTTPStatusError as e:
                print(f"   ❌ Erreur {e.response.status_code} : {e.response.text[:120]}…")
                errors.append({"id": ds_id, "title": title, "error": str(e)})
            except Exception as e:
                print(f"   ⚠️ Erreur inattendue : {e}")
                errors.append({"id": ds_id, "title": title, "error": str(e)})
        else:
            print(f"   (Simulation) Fréquence serait mise à jour → '{DEFAULT_FREQUENCY}'")
            fixed_count += 1
    else:
        print("   Fréquence déjà conforme.")
        already_ok_count += 1

# ───────────────────────────────
# Sauvegarde des fréquences
# ───────────────────────────────
backup["count"] = len(backup["datasets"])
with open(BACKUP_PATH, "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print(f"\nBackup sauvegardé dans {BACKUP_PATH}")

# ───────────────────────────────
# Bilan
# ───────────────────────────────
print("\n───────────────────────────────")
print("Bilan du traitement")
print("───────────────────────────────")
print(f"Total jeux de données analysés : {total_datasets}")
print(f"Fréquences à corriger          : {fixed_count}")
print(f"Fréquences déjà conformes      : {already_ok_count}")
print(f"Erreurs rencontrées            : {len(errors)}")
print(f"Mode appliqué : {'ÉCRITURE RÉELLE' if UPDATE_MODE else 'SIMULATION'}")
