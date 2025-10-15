import json
from datagouv import Client
from datetime import datetime

# ⚙️ Configuration
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture
PROPERTIES_TO_BACKUP = ["id", "title", "description", "tags", "frequency", "license"]  # Personnalisable
OUTPUT_PATH = "DataGouv/scripts/backup_datasets_properties.json"

# 🧭 Initialisation du client
client = Client()  # accès public, pas besoin d'API key pour lecture
organization = client.organization(ORG_ID)

# 🗂️ Structure du fichier de sauvegarde
backup = {
    "organization": ORG_ID,
    "date": datetime.now().isoformat(),
    "properties": PROPERTIES_TO_BACKUP,
    "datasets": {}
}

print(f"Connexion OK → Organisation : {ORG_ID}")
print(f"Propriétés sauvegardées : {', '.join(PROPERTIES_TO_BACKUP)}\n")

# 🔁 Boucle sur les jeux de données
for ds in organization.datasets:
    ds_id = getattr(ds, "id", None) or getattr(ds, "dataset_id", None)
    if not ds_id:
        print("⚠️ Dataset sans identifiant, ignoré.")
        continue

    title = getattr(ds, "title", None) or getattr(ds, "name", None)

    # ⚠️ Récupération du dataset complet (pour les propriétés absentes du résumé)
    full_ds = client.dataset(ds_id)

    # Extraction dynamique des propriétés demandées
    saved_props = {}
    for prop in PROPERTIES_TO_BACKUP:
        value = getattr(full_ds, prop, None)
        saved_props[prop] = value

    backup["datasets"][ds_id] = {
        "title": title,
        **saved_props
    }

    print(f"Backup → {title or 'inconnu'} ({ds_id})")

# 🧮 Statistiques
backup["count"] = len(backup["datasets"])

# 💾 Écriture dans le fichier
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print("\n--- BACKUP TERMINÉ ---")
print(f"{backup['count']} jeux de données sauvegardés dans {OUTPUT_PATH}")
