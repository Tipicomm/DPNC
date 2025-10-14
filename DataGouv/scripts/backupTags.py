import json
from datagouv import Client
from datetime import datetime

# ID de l'organisation
ORG_ID = "534fff91a3a7292c64a77f73"

# Initialisation du client (GET public)
client = Client()

# Structure de sauvegarde
backup = {
    "organization": ORG_ID,
    "date": datetime.now().isoformat(),
    "datasets": {}
}

organization = client.organization(ORG_ID)

for dataset in organization.datasets:
    dataset_id = getattr(dataset, "id", None)
    # certains environnements n’ont pas `.slug`, on fallback sur `.name`
    dataset_slug = getattr(dataset, "slug", getattr(dataset, "name", None))
    current_tags = getattr(dataset, "tags", []) or []

    if not dataset_id:
        print("⚠️ Dataset sans identifiant, ignoré.")
        continue

    backup["datasets"][dataset_id] = {
        "slug": dataset_slug,
        "tags": current_tags
    }

    print(f"Backup {dataset_slug or 'inconnu'} ({dataset_id}) → {current_tags}")

# Ajout du nombre total de datasets
backup["count"] = len(backup["datasets"])

# Sauvegarde du JSON dans le dépôt
output_path = "DataGouv/scripts/backup_tags.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print(f"\n--- BACKUP TERMINÉ ---")
print(f"{backup['count']} jeux de données sauvegardés dans {output_path}")
