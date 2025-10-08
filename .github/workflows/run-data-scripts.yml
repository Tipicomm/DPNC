import os
import json
from datagouv import Client

ORG_ID = "534fff91a3a7292c64a77f73"
client = Client()

backup = {
    "organization": ORG_ID,
    "datasets": {}
}

for dataset in client.organization(ORG_ID).datasets:
    dataset_id = getattr(dataset, "id", None)
    dataset_slug = getattr(dataset, "slug", None)
    current_tags = getattr(dataset, "tags", []) or []
    backup["datasets"][dataset_id] = {
        "slug": dataset_slug,
        "tags": current_tags
    }
    print(f"Backup {dataset_slug} ({dataset_id}) → {current_tags}")

# chemin explicite vers ton repo GitHub
output_path = "DataGouv/scripts/backup_tags.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print(f"\n--- BACKUP TERMINÉ ---\nFichier sauvegardé : {output_path}")
