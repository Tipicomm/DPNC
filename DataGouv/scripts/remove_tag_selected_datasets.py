"""
But :
Supprimer le tag "DEPS" d’une liste spécifique de jeux de données
sur DataGouv (via l’API officielle /api/1/datasets/{id}/).

───────────────────────────────
⚙️  Fonctionnement :
───────────────────────────────
- Le script parcourt uniquement une liste d’identifiants (DATASET_IDS).
- Pour chaque dataset, il supprime le tag "DEPS" s’il est présent.
- Par défaut, fonctionne en **mode simulation** (`UPDATE_MODE=False`).
- En mode écriture (`UPDATE_MODE=True`), les modifications sont envoyées à l’API.
- Les autres tags sont **préservés** : seule la suppression du tag ciblé est effectuée.

───────────────────────────────
🔐  Variables d’environnement :
───────────────────────────────
- DATAGOUV_ENV : "demo" ou "www" (défaut = demo)
- UPDATE_MODE : "True" (écriture réelle) ou "False" (simulation)
- DEMO_DATA_GOUV_KEY : clé API pour demo
- DATAGOUV_API_KEY : clé API pour prod

───────────────────────────────
🧩 Bonnes pratiques :
───────────────────────────────
- Toujours tester en `demo` et `UPDATE_MODE=False` avant écriture.
- Sauvegarder les métadonnées (backup) avant modification.
- Ne jamais exécuter sur `www` sans validation de la liste.
"""

import os
import httpx
from datagouv import Client

# ───────────────────────────────
# Configuration
# ───────────────────────────────
TAG_TO_REMOVE = "deps"
DEFAULT_ENV = "demo"

# Liste des datasets ciblés
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
        f"Aucune clé API détectée pour '{ENVIRONMENT}'.\n"
        f"⚠️ Vérifie la variable {'DEMO_DATA_GOUV_KEY' if ENVIRONMENT == 'demo' else 'DATAGOUV_API_KEY'}."
    )

print("───────────────────────────────")
print(f"🟢 Environnement : {ENVIRONMENT.upper()}")
print(f"🔓 Mode : {'ÉCRITURE RÉELLE' if UPDATE_MODE else 'SIMULATION'}")
print(f"🏷️ Tag à supprimer : {TAG_TO_REMOVE}")
print(f"📋 Nombre de datasets ciblés : {len(DATASET_IDS)}")
print("───────────────────────────────\n")

# ───────────────────────────────
# Initialisation du client
# ───────────────────────────────
client = Client(environment=ENVIRONMENT, api_key=API_KEY)
errors = []
removed = 0
not_present = 0
total = 0

# ───────────────────────────────
# Parcours de la liste des jeux de données
# ───────────────────────────────
for ds_id in DATASET_IDS:
    total += 1
    try:
        full_ds = client.dataset(ds_id)
        title = getattr(full_ds, "title", ds_id)
        tags = getattr(full_ds, "tags", []) or []

        print(f"→ {title} ({ds_id})")
        print(f"   Tags actuels : {tags}")

        if TAG_TO_REMOVE in tags:
            new_tags = [t for t in tags if t != TAG_TO_REMOVE]
            print(f"   [Prévu] Suppression du tag : {TAG_TO_REMOVE}")
            print(f"   [Liste Prévue] Tags après suppression : {new_tags}")

            if UPDATE_MODE:
                try:
                    full_ds.update({"tags": new_tags})
                    print(f"   ✅ Tag supprimé avec succès")
                    removed += 1
                except httpx.HTTPStatusError as e:
                    print(f"   ❌ Erreur {e.response.status_code} : {e.response.text[:120]}…")
                    errors.append({"id": ds_id, "title": title, "error": str(e)})
                except Exception as e:
                    print(f"   ⚠️ Erreur inattendue : {e}")
                    errors.append({"id": ds_id, "title": title, "error": str(e)})
        else:
            print(f"   ℹ️ Tag non présent : {TAG_TO_REMOVE}")
            not_present += 1

    except Exception as e:
        print(f"⚠️ Impossible de charger le dataset {ds_id}: {e}")
        errors.append({"id": ds_id, "error": str(e)})

# ───────────────────────────────
# Rapport final
# ───────────────────────────────
print("\n───────────────────────────────")
print(f"✅ Traitement terminé ({ENVIRONMENT.upper()})")
print(f"📊 Jeux de données traités : {total}")
print(f"🗑️ Tags supprimés : {removed}")
print(f"ℹ️ Non concernés (tag absent) : {not_present}")
print(f"❌ Erreurs : {len(errors)}")
print("───────────────────────────────")

if errors:
    print("\n🧾 Détails des erreurs :")
    for e in errors:
        print(f" - {e.get('title', 'Sans titre')} ({e['id']}) → {e['error']}")
