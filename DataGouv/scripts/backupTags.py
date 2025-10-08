import os
import json
from datagouv import Client

API_KEY = os.environ["DATAGOUV_API_KEY"]
ORG_ID = "534fff91a3a7292c64a77f73"

client = Client(api_key=API_KEY)
organization = client.organization(ORG_ID)

backup = {}

for dataset in organization.datasets:
    dataset_id = dataset["id"]
    dataset_slug = dataset["slug"]
    current_tags = dataset.get("tags", []) or []
    backup[dataset_id] = current_tags
    print(f"Backup {dataset_slug} ({dataset_id}) → {current_tags}")

with open("backup_tags.json", "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print("\n--- BACKUP TERMINÉ ---")
print(f"{len(backup)} datasets sauvegardés dans backup_tags.json")
