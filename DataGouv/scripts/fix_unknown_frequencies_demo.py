"""
But :
Corriger les jeux de données sur DEMO (https://demo.data.gouv.fr)
dont la fréquence est strictement 'unknown', en la remplaçant par 'punctual'.

⚙️ Fonctionnement :
- Se connecte à l’organisation via la clé API
- Parcourt tous les datasets
- Si frequency == "unknown", met à jour uniquement ce champ
- Vérifie ensuite que rien d’autre n’a changé
- Sauvegarde un backup complet

⚠️ Nécessite la clé API dans le secret GitHub : DEMO_DATA_GOUV_KEY
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
# Fonctions utilitaires
# ───────────────────────────────
VOLATILE_KEYS = {
    "last_modified", "last_update", "internal", "metrics", "quality",
}

def diff_keys(before: dict, after: dict) -> set[str]:
    """Retourne les clés modifiées hors champs volatils."""
    keys = set(before.keys()) | set(after.keys())
    changed = set()
    for k in keys:
        if k in VOLATILE_KEYS:
            continue
        if before.get(k) != after.get(k):
            changed.add(k)
    return changed

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

    try:
        full_ds = client.dataset(ds_id)
        full_ds.refresh()
        freq = getattr(full_ds, "frequency", None)
        freq = (freq or "").strip().lower()

        backup["datasets"][ds_id] = {
            "title": title,
            "frequency": freq
        }

        print(f"→ {title} ({ds_id}) — fréquence actuelle : {freq or '∅'}")

        if freq == "unknown":
            if UPDATE_MODE:
                try:
                    # 1️⃣ Snapshot avant
                    before = client._client.session.get(full_ds.uri).json()

                    # 2️⃣ Update minimal
                    print("   Payload envoyé :", {"frequency": "punctual"})
                    full_ds.update({"frequency": "punctual"})

                    # 3️⃣ Snapshot après
                    after = client._client.session.get(full_ds.uri).json()

                    # 4️⃣ Vérification des différences
                    allowed_changes = {"frequency"} | VOLATILE_KEYS
                    changed = diff_keys(before, after)
                    unexpected = changed - allowed_changes

                    if unexpected:
                        print(f"   ⚠️ Attention : changements inattendus détectés : {sorted(unexpected)}")
                    else:
                        print("   ✅ Vérifié : seule la fréquence (et champs volatils) a changé.")

                    fixed_count += 1

                except httpx.HTTPStatusError as e:
                    print(f"   ❌ Erreur HTTP {e.response.status_code} : {e.response.text[:120]}…")
                    errors.append({"id": ds_id, "title": title, "error": str(e)})

                except Exception as e:
                    print(f"   ⚠️ Erreur inattendue : {e}")
                    errors.append({"id": ds_id, "title": title, "error": str(e)})

            else:
                print("   (Simulation) Fréquence serait mise à jour → 'punctual'")
                fixed_count += 1

        else:
            print("   ⏭️ Aucune modification (fréquence différente de 'unknown').")
            skipped_count += 1

    except Exception as e:
        print(f"❌ Erreur lors du traitement du dataset {ds_id}: {e}")
        errors.append({"id": ds_id, "title": title, "error": str(e)})

# ───────────────────────────────
# Sauvegarde
# ───────────────────────────────
backup["count"] = len(backup["datasets"])
with open(BACKUP_PATH, "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print(f"\n💾 Backup sauvegardé dans {BACKUP_PATH}")

# ───────────────────────────────
# Bilan
# ───────────────────────────────
print("\n───────────────────────────────")
print("Bilan du traitement des fréquences 'unknown' (DEMO)")
print("───────────────────────────────")
print(f"📊 Total jeux de données analysés : {total_datasets}")
print(f"🛠️  Fréquences corrigées          : {fixed_count}")
print(f"⏭️  Fréquences ignorées           : {skipped_count}")
print(f"⚠️  Erreurs rencontrées            : {len(errors)}")
print(f"🧩 Mode appliqué : {'ÉCRITURE RÉELLE' if UPDATE_MODE else 'SIMULATION'}")
print("───────────────────────────────")
