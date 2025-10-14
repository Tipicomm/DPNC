import os
from datagouv import Client
import httpx

# Configuration
API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture
TAG = "culture"

# Initialisation du client
client = Client(environment="demo", api_key=API_KEY)
print("Connexion à l'environnement DEMO")
print(f"Organisation ciblée : {ORG_ID}")

# Récupération des jeux de données
organization = client.organization(ORG_ID)
datasets = list(organization.datasets)
print(f"{len(datasets)} jeux de données détectés pour l'organisation.\n")

errors = []

# Traitement de chaque dataset
for ds in datasets:
    ds_id = getattr(ds, "id", None)
    title = getattr(ds, "title", None) or getattr(ds, "name", None)
    tags = getattr(ds, "tags", []) or []

    print(f"→ {title} ({ds_id})")
    print(f"   Tags actuels : {tags}")

    if TAG not in tags:
        new_tags = tags + [TAG]
        try:
            ds.update({"tags": new_tags})
            print(f"   ✅ Tag ajouté : {TAG}")
        except httpx.HTTPStatusError as e:
            print(f"   ❌ Erreur {e.response.status_code} : {e.response.text[:120]}…")
            errors.append({"id": ds_id, "title": title, "error": str(e)})
        except Exception as e:
            print(f"   ⚠️ Erreur inattendue : {e}")
            errors.append({"id": ds_id, "title": title, "error": str(e)})
    else:
        print(f"   ℹ️ Tag déjà présent : {TAG}")

print("\nTraitement terminé avec succès.")

if errors:
    print(f"\n{len(errors)} erreurs détectées :")
    for e in errors:
        print(f" - {e['title']} ({e['id']}) → {e['error']}")
