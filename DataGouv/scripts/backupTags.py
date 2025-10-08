import json
from datagouv import Client
from datetime import datetime

# Organisation du ministère
ORG_ID = "534fff91a3a7292c64a77f73"

# Client en lecture seule (pas besoin de token)
client = Client()

organization = client.organization(ORG_ID)

backup = {
    "organization": ORG_ID,
    "date": datetime.now().isoformat(),
    "datasets": {}
}

for dataset in organization.datasets:
    dataset_id = getattr(dataset, "id", None)
    dataset_slug = getattr(dataset, "slug", None)
    current_tags = getattr(dataset, "tags", []) or []
    backup["datasets"][dataset_id] = {
        "slug": dataset_slug,
        "tags": current_tags
    }
    print(f"Backup {dataset_slug} ({dataset_id}) → {current_tags}")

with open("backup_tags.json", "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print("\n--- BACKUP TERMINÉ ---")
print(f"{len(backup['datasets'])} jeux sauvegardés dans backup_tags.json")
