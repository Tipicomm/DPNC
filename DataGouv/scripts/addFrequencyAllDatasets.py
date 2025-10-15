import os
from datagouv import Client
import httpx

API_KEY = os.getenv("DEMO_DATA_GOUV_KEY")
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture
DEFAULT_FREQUENCY = "punctual"

client = Client(environment="demo", api_key=API_KEY)
print("Connexion à l'environnement DEMO")
print(f"Organisation ciblée : {ORG_ID}")

organization = client.organization(ORG_ID)
datasets = list(organization.datasets)
total_datasets = len(datasets)
print(f"{total_datasets} jeux de données détectés pour l'organisation.\n")

errors = []
fixed_count = 0
already_ok_count = 0

for ds in datasets:
    ds_id = getattr(ds, "id", None)
    title = getattr(ds, "title", None) or getattr(ds, "name", None)

    # ⚠️ On recharge le dataset complet
    full_ds = client.dataset(ds_id)
    frequency = getattr(full_ds, "frequency", None)

    print(f"→ {title} ({ds_id})")
    print(f"   Fréquence actuelle : {frequency}")

    if frequency in (None, "unknown", "", "null"):
        try:
            full_ds.update({"frequency": DEFAULT_FREQUENCY})
            print(f"   ✅ Fréquence corrigée → '{DEFAULT_FREQUENCY}'")
            fixed_count += 1
        except httpx.HTTPStatusError as e:
            print(f"   ❌ Erreur {e.response.status_code} : {e.response.text[:120]}…")
            errors.append({"id": ds_id, "title": title, "error": str(e)})
        except Exception as e:
            print(f"   ⚠️ Erreur inattendue : {e}")
            errors.append({"id": ds_id, "title": title, "error": str(e)})
    else:
        print("   ℹ️ Fréquence déjà conforme.")
        already_ok_count += 1

print("\n───────────────────────────────")
print("Bilan du traitement")
print("───────────────────────────────")
print(f"Total jeux de données analysés : {total_datasets}")
print(f"✅ Fréquences corrigées        : {fixed_count}")
print(f"ℹ️  Fréquences déjà conformes  : {already_ok_count}")
print(f"❌ Erreurs rencontrées         : {len(errors)}")
