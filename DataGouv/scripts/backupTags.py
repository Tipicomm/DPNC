import json
from datagouv import Client
from datetime import datetime

ORG_ID = "534fff91a3a7292c64a77f73"
client = Client()  # accès public, pas de token

backup = {
    "organization": ORG_ID,
    "date": datetime.now().isoformat(),
    "datasets": {}
}

organization = client.organization(ORG_ID)

for ds in organization.datasets:
    # id robuste (certaines versions exposent id/dataset_id)
    ds_id = getattr(ds, "id", None) or getattr(ds, "dataset_id", None)
    if not ds_id:
        print("⚠️ Dataset sans identifiant, ignoré.")
        continue

    # lisible et fiable : title (fallback sur name)
    title = getattr(ds, "title", None) or getattr(ds, "name", None)

    # conforme à la préconisation du dev
    tags = getattr(ds, "tags", []) or []

    backup["datasets"][ds_id] = {
        "title": title,
        "tags": tags,
    }

    print(f"Backup {title or 'inconnu'} ({ds_id}) → {tags}")

# ajoute le nombre total
backup["count"] = len(backup["datasets"])

# écrit dans le repo
output_path = "DataGouv/scripts/backup_tags.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)

print(f"\n--- BACKUP TERMINÉ ---")
print(f"{backup['count']} jeux de données sauvegardés dans {output_path}")
