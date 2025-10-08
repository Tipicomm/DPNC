import json
from datetime import datetime
from datagouv import Client

ORG_ID = "534fff91a3a7292c64a77f73"

# Client sans API key (lecture publique)
client = Client()

organization = client.organization(ORG_ID)

backup = {
    "organization": ORG_ID,
    "date": datetime.now().isoformat(),
    "datasets": {}
}

for dataset in organization.datasets:
    # Récupération sûre des champs
    dataset_id = getattr(dataset, "id", None) or dataset.__dict__.get("id")
    dataset_slug = getattr(dataset, "slug", None) or dataset.__dict__.get("slug")
    current_tags = getattr(dataset, "tags", None) or dataset.__dict__.get("tags", [])

    backup["datasets"][dataset_id] = {
        "slug": dataset_slug,
        "tags": current_tags
    }
    print(f"Backup {dataset_slug} ({dataset_id}) → {current_tags}")

# Ajouter compteur
backup["count"] = len(backup["datasets"])

# Sauvegarde JSON dans ton repo
with open("DataGouv/scripts/backup_tags.json", "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print("\n--- BACKUP TERMINÉ ---")
print(f"{backup['count']} datasets sauvegardés dans DataGouv/scripts/backup_tags.json")
