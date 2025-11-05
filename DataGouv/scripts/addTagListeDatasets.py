"""
But :
Ajouter le tag "deps-doc" uniquement à une liste spécifique de jeux de données
sur data.gouv.fr (ou demo.data.gouv.fr).

───────────────────────────────
⚙️  Fonctionnement :
───────────────────────────────
- Parcourt uniquement la liste d’identifiants fournie dans DATASET_IDS.
- Pour chaque dataset, ajoute le tag "DEPS" s’il n’est pas déjà présent.
- Mode simulation par défaut (aucune écriture).
- En mode écriture (UPDATE_MODE=True), met à jour réellement les jeux de données.

───────────────────────────────
🔐  Variables d’environnement :
───────────────────────────────
- DATAGOUV_ENV : "demo" ou "www" (défaut = demo)
- UPDATE_MODE : "True" (écriture) ou "False" (simulation)
- DEMO_DATA_GOUV_KEY : clé API pour demo
- DATAGOUV_API_KEY : clé API pour prod
"""

import os
import httpx
from datagouv import Client

# ───────────────────────────────
# Configuration
# ───────────────────────────────
TAG = "deps-doc"
DEFAULT_ENV = "demo"

# Liste fournie (datasets à traiter uniquement)
DATASET_IDS = [
    "67f7424b137aad8bcb9ac731",
    "6545c1e0bcab951e5a4090dd",
    "651e3557c5f0fe7fee6e33b0",
    "64ae255bbc600d7a3468ee64",
    "635a02568c0544dea690f691",
    "635a0255ae37fbcc1290f692",
    "635a0255905f648a9e90f68e",
    "635a02558c0544dea690f690",
    "635a0254f931c40e6390f690",
    "635a0252f931c40e6390f68f",
    "635a0251ae37fbcc1290f691",
    "635a0251dc41dc073190f690",
    "635a0251dc41dc073190f68f",
    "635a0251e708959bd890f68e",
    "6358b1077649e63c98487174",
    "6358b1057280fb6a2a90f68e",
    "6350c887ecad6abcaa90f690",
    "6350c887d95d644f9c487174",
    "6350c887210de3789f90f68e",
    "6350c887cec32b14bc90f68e",
    "6350c886dbe7e0f35f90f68e",
    "6350c885ecad6abcaa90f68f",
    "6340f607b1c7e116b5eacfa4",
    "6340f606d04658a4a4eacfa4",
    "6340f606a6550b8bf4eacfa4",
    "6340f6052cbb8188ebeacfa4",
    "633bafd4a3f5260a3ceacfa6",
    "633669cd02685f4c8beacfa5",
    "633518ec6b559831b7eacfa4",
    "633518ecb5deca30cdeacfa4",
    "633518ec7d88ad6fb4eacfa4",
    "62cf95993d99f22480f49334",
    "61777ddaa9101d073e5506cd",
    "5af120e7b595087cfabcde82",
    "5af120e5a3a7295e54c41a13",
]

# ───────────────────────────────
# Lecture des variables d’environnement
# ───────────────────────────────
ENVIRONMENT = os.getenv("DATAGOUV_ENV", DEFAULT_ENV).lower()
UPDATE_MODE = os.getenv("UPDATE_MODE", "False").lower() == "true"

API_KEYS = {
    "demo": os.getenv("DEMO_DATA_GOUV_KEY"),
    "www": os.getenv("DATAGOUV_API_KEY"),
}
API_KEY = API_KEYS.get(ENVIRONMENT)

if ENVIRONMENT not in ("demo", "www", "prod"):
    raise ValueError(f"Environnement inconnu : {ENVIRONMENT}")

if not API_KEY and UPDATE_MODE:
    raise EnvironmentError(
        f"Aucune clé API détectée pour l'environnement '{ENVIRONMENT}'."
    )

print("───────────────────────────────")
print(f"🟢 Environnement : {ENVIRONMENT.upper()}")
print(f"🔓 Mode : {'ÉCRITURE RÉELLE' if UPDATE_MODE else 'SIMULATION (aucune écriture)'}")
print(f"🏷️ Tag à ajouter : {TAG}")
print(f"📋 Nombre de datasets ciblés : {len(DATASET_IDS)}")
print("───────────────────────────────\n")

# ───────────────────────────────
# Initialisation du client
# ───────────────────────────────
client = Client(environment=ENVIRONMENT, api_key=API_KEY)

errors = []
added = 0
already_present = 0
total = 0

# ───────────────────────────────
# Parcours de la liste d’identifiants
# ───────────────────────────────
for ds_id in DATASET_IDS:
    total += 1
    try:
        full_ds = client.dataset(ds_id)
        title = getattr(full_ds, "title", ds_id)
        tags = getattr(full_ds, "tags", []) or []

        print(f"→ {title} ({ds_id})")
        print(f"   Tags actuels : {tags}")

        if TAG not in tags:
            new_tags = tags + [TAG]
            print(f"   [Prévu] Ajout du tag : {TAG}")
            print(f"   [Liste Prévue] Tags après ajout : {new_tags}")

            if UPDATE_MODE:
                try:
                    full_ds.update({"tags": new_tags})
                    print(f"   ✅ Tag ajouté avec succès")
                    added += 1
                except httpx.HTTPStatusError as e:
                    print(f"   ❌ Erreur {e.response.status_code} : {e.response.text[:120]}…")
                    errors.append({"id": ds_id, "title": title, "error": str(e)})
                except Exception as e:
                    print(f"   ⚠️ Erreur inattendue : {e}")
                    errors.append({"id": ds_id, "title": title, "error": str(e)})
        else:
            print(f"   ℹ️ Tag déjà présent : {TAG}")
            already_present += 1

    except Exception as e:
        print(f"⚠️ Impossible de charger le dataset {ds_id}: {e}")
        errors.append({"id": ds_id, "error": str(e)})

print("\n───────────────────────────────")
print(f"✅ Traitement terminé ({ENVIRONMENT.upper()})")
print(f"📊 Jeux de données traités : {total}")
print(f"🏷️ Tags ajoutés : {added}")
print(f"ℹ️ Déjà présents : {already_present}")
print(f"❌ Erreurs : {len(errors)}")
print("───────────────────────────────")

if errors:
    print("\n🧾 Détails des erreurs :")
    for e in errors:
        print(f" - {e.get('title', 'Sans titre')} ({e['id']}) → {e['error']}")
