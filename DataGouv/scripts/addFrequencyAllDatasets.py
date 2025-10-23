"""
But :
Ajouter le tag "Culture" à tous les jeux de données d'une organisation DataGouv (via l’API /api/1/datasets/{id}/).

Ce script utilise le client officiel `datagouv-client` pour parcourir tous les jeux de données
d’une organisation et ajouter le tag "Culture" si celui-ci n’est pas déjà présent.

Le script fonctionne à la fois sur les environnements :
  - DEMO  → https://demo.data.gouv.fr
  - WWW (production) → https://www.data.gouv.fr

Remarques importantes :
- Le mode par défaut est la SIMULATION : aucune écriture n’est faite tant que `UPDATE_MODE` reste à False.
- Le script concatène les tags existants avant mise à jour, il n’écrase donc jamais les tags déjà présents.
- Une clé API est requise uniquement si `UPDATE_MODE=True` (écriture réelle).
- Les variables d’environnement attendues sont :
    - `DATAGOUV_ENV` = "demo" ou "www"
    - `DEMO_DATA_GOUV_KEY` pour l’environnement de test
    - `DATA_GOUV_KEY` pour la production

Bonnes pratiques :
- Toujours tester d’abord en mode simulation sur DEMO avant d’activer l’écriture.
- Sauvegarder les métadonnées avant toute mise à jour importante.
"""

import os
import httpx
from datagouv import Client

# ───────────────────────────────
# Configuration utilisateur
# ───────────────────────────────
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture
TAG = "Culture"                      # Tag à ajouter (sensible à la casse)
UPDATE_MODE = False                  # ⚠️ Simulation si False (aucune écriture)
DEFAULT_ENV = "demo"                 # Environnement par défaut si non précisé

# ───────────────────────────────
# Environnement et clé API
# ───────────────────────────────
ENVIRONMENT = os.getenv("DATAGOUV_ENV", DEFAULT_ENV).lower()

API_KEYS = {
    "demo": os.getenv("DEMO_DATA_GOUV_KEY"),
    "www": os.getenv("DATA_GOUV_KEY"),  # ✅ Clé API production
    "prod": os.getenv("DATA_GOUV_KEY"),
}

API_KEY = API_KEYS.get(ENVIRONMENT)

if ENVIRONMENT not in ("demo", "www", "prod"):
    raise ValueError(f"Environnement inconnu : {ENVIRONMENT}")

if not API_KEY and UPDATE_MODE:
    raise EnvironmentError(
        f"Aucune clé API détectée pour l'environnement '{ENVIRONMENT}'.\n"
        f"⚠️ Vérifie que la variable "
        f"{'DEMO_DATA_GOUV_KEY' if ENVIRONMENT == 'demo' else 'DATA_GOUV_KEY'} "
        f"est bien définie."
    )

print("───────────────────────────────")
print(f"🟢 Environnement : {ENVIRONMENT.upper()}")
print(f"🔓 Mode : {'écriture' if UPDATE_MODE else 'simulation (aucune écriture)'}")
print(f"🏛️ Organisation ciblée : {ORG_ID}")
print(f"🏷️ Tag à ajouter : {TAG}")
print("───────────────────────────────\n")

# ───────────────────────────────
# Initialisation du client
# ───────────────────────────────
client = Client(environment=ENVIRONMENT, api_key=API_KEY)
print(f"Connexion à l’environnement {ENVIRONMENT.upper()}...")

organization = client.organization(ORG_ID)
print(f"Organisation : {organization.title}\n")

errors = []
added = 0
already_present = 0
total = 0

# ───────────────────────────────
# Parcours des datasets
# ───────────────────────────────
for ds in organization.datasets:
    total += 1
    ds_id = getattr(ds, "id", None)
    title = getattr(ds, "title", None) or getattr(ds, "name", None)
    tags = getattr(ds, "tags", []) or []

    print(f"→ {title} ({ds_id})")
    print(f"   Tags actuels : {tags}")

    if TAG not in tags:
        new_tags = tags + [TAG]
        print(f"   [Prévu] Ajout du tag : {TAG}")

        if UPDATE_MODE:
            try:
                ds.update({"tags": new_tags})
                print(f"   ✅ Tag ajouté : {TAG}")
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

print("\n───────────────────────────────")
print(f"✅ Traitement terminé ({ENVIRONMENT.upper()})")
print(f"📊 Jeux de données traités : {total}")
print(f"🏷️ Tags ajoutés : {added}")
print(f"ℹ️ Déjà présents : {already_present}")
print(f"❌ Erreurs : {len(errors)}")
print("───────────────────────────────")

if errors:
    for e in errors:
        print(f" - {e['title']} ({e['id']}) → {e['error']}")
