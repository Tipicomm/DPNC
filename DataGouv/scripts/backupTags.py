import os
import json
from datagouv import Client
from datetime import datetime

ORG_ID = "534fff91a3a7292c64a77f73"

# Pas besoin de token pour GET
client = Client()

organization = client.organization(ORG_ID)

backup = {
    "organization": ORG_ID,
    "date": datetime.now().isoformat(),
    "datasets": {}
}

for dataset in organization.datasets:
    dataset_id = dataset.id
    dataset_slug = dataset.slug
    current_tags = getattr(dataset, "tags", []) or []
    backup["datasets"][dataset_id] = {
        "slug": dataset_slug,
        "tags": current_tags
    }
    print(f"Backup {dataset_slug} ({dataset_id}) → {current_tags}")

# Sauvegarde JSON
backup_file = "DataGouv/scripts/backup_tags.json"
with open(backup_file, "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

count = len(backup["datasets"])
print(f"\n--- BACKUP TERMINÉ ---")
print(f"{count} datasets sauvegardés dans {backup_file}")

# Écrit aussi le nombre dans un fichier texte pour GitHub Actions
with open("datasets_count.txt", "w") as f:
    f.write(str(count))
