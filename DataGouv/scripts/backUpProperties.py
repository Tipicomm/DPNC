import os
import json
from datagouv import Client
from datetime import datetime

# ───────────────────────────────
# Configuration
# ───────────────────────────────
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture
PROPERTIES_TO_BACKUP = [
    "id",
    "title",
    "description",
    "tags",
    "frequency",
    "license"
]  # Personnalisable
OUTPUT_PATH = "DataGouv/scripts/backup_datasets_properties.json"

# ───────────────────────────────
# Initialisation du client
# ───────────────────────────────
print("Connexion à l’API DataGouv (accès public)...")
client = Client()  # accès public, pas besoin d'API key pour lecture
organization = client.organization(ORG_ID)

# ───────────────────────────────
# Structure du fichier de sauvegarde
# ───────────────────────────────
backup = {
    "organization": ORG_ID,
    "date": datetime.now().isoformat(),
    "properties": PROPERTIES_TO_BACKUP,
    "datasets": {}
}

print(f"Connexion réussie. Organisation : {ORG_ID}")
print(f"Propriétés sauvegardées : {', '.join(PROPERTIES_TO_BACKUP)}\n")

# ───────────────────────────────
# Boucle sur les jeux de données
# ───────────────────────────────
for ds in organization.datasets:
    ds_id = getattr(ds, "id", None) or getattr(ds, "dataset_id", None)
    if not ds_id:
        print("Avertissement : dataset sans identifiant, ignoré.")
        continue

    title = getattr(ds, "title", None) or getattr(ds, "name", None)

    # Récupération complète du dataset pour les propriétés manquantes
    try:
        full_ds = client.dataset(ds_id)
    except Exception as e:
        print(f"Erreur lors de la récupération du dataset {ds_id}: {e}")
        continue

    saved_props = {}
    for prop in PROPERTIES_TO_BACKUP:
        saved_props[prop] = getattr(full_ds, prop, None)

    backup["datasets"][ds_id] = {
        "title": title,
        **saved_props
    }

    print(f"Sauvegarde du dataset : {title or 'inconnu'} ({ds_id})")

# ───────────────────────────────
# Écriture du fichier de sauvegarde
# ───────────────────────────────
backup["count"] = len(backup["datasets"])

# Crée le dossier si nécessaire
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

try:
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(backup, f, indent=2, ensure_ascii=False)

    if os.path.exists(OUTPUT_PATH):
        print(f"\nFichier de sauvegarde créé avec succès : {OUTPUT_PATH}")
    else:
        raise FileNotFoundError(f"Le fichier {OUTPUT_PATH} n’a pas été trouvé après écriture.")
except Exception as e:
    print(f"Erreur lors de l’écriture du fichier : {e}")
    raise

# ───────────────────────────────
# Bilan final
# ───────────────────────────────
print("\n--- SAUVEGARDE TERMINÉE ---")
print(f"{backup['count']} jeux de données sauvegardés dans {OUTPUT_PATH}")
