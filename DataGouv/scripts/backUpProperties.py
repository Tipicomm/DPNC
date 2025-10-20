import os
import json
from datagouv import Client
from datetime import datetime

# ───────────────────────────────
# Configuration de base
# ───────────────────────────────
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture
PROPERTIES_TO_BACKUP = [
    "id",
    "title",
    "description",
    "tags",
    "frequency",
    "license"
]
OUTPUT_PATH = "DataGouv/scripts/backup_datasets_properties.json"

# ───────────────────────────────
# Contexte d’environnement
# ───────────────────────────────
# On conserve le contexte (utile pour logs et traçabilité)
ENVIRONMENT = os.getenv("DATAGOUV_ENV", "demo")  # demo par défaut

print("───────────────────────────────")
print(f"🟢 Environnement : {ENVIRONMENT.upper()} (lecture seule)")
print("🔓 Mode : public (aucune clé API requise)")
print(f"🏛️ Organisation ciblée : {ORG_ID}")
print("───────────────────────────────\n")

# ───────────────────────────────
# Initialisation du client
# ───────────────────────────────
print(f"Connexion à l’environnement {ENVIRONMENT.upper()} (accès public)...")
client = Client(environment=ENVIRONMENT)  # Lecture seule sans clé
organization = client.organization(ORG_ID)

# ───────────────────────────────
# Structure du fichier de sauvegarde
# ───────────────────────────────
backup = {
    "organization": ORG_ID,
    "environment": ENVIRONMENT,
    "date": datetime.now().isoformat(),
    "properties": PROPERTIES_TO_BACKUP,
    "datasets": {}
}

print(f"Propriétés sauvegardées : {', '.join(PROPERTIES_TO_BACKUP)}\n")

# ───────────────────────────────
# Boucle sur les jeux de données
# ───────────────────────────────
for ds in organization.datasets:
    ds_id = getattr(ds, "id", None) or getattr(ds, "dataset_id", None)
    if not ds_id:
        print("⚠️  Avertissement : dataset sans identifiant, ignoré.")
        continue

    title = getattr(ds, "title", None) or getattr(ds, "name", None)

    try:
        full_ds = client.dataset(ds_id)
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du dataset {ds_id}: {e}")
        continue

    saved_props = {prop: getattr(full_ds, prop, None) for prop in PROPERTIES_TO_BACKUP}

    backup["datasets"][ds_id] = {
        "title": title,
        **saved_props
    }

    print(f"💾 Sauvegarde du dataset : {title or 'inconnu'} ({ds_id})")

# ───────────────────────────────
# Écriture du fichier de sauvegarde
# ───────────────────────────────
backup["count"] = len(backup["datasets"])

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

try:
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(backup, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Fichier de sauvegarde créé avec succès : {OUTPUT_PATH}")
except Exception as e:
    print(f"❌ Erreur lors de l’écriture du fichier : {e}")
    raise

# ───────────────────────────────
# Bilan final
# ───────────────────────────────
print("\n───────────── BILAN FINAL ─────────────")
print(f"📦 {backup['count']} jeux de données sauvegardés.")
print(f"🏛️ Organisation : {ORG_ID}")
print(f"🌍 Environnement : {ENVIRONMENT}")
print(f"📁 Fichier : {OUTPUT_PATH}")
print("────────────────────────────────────────")
