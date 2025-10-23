"""
But :
Ajouter le tag "culture" à tous les jeux de données d'une organisation DataGouv
(via l’API officielle /api/1/datasets/{id}/).

Ce script utilise le client Python officiel `datagouv-client` pour parcourir
tous les jeux de données d’une organisation et ajouter le tag "culture"
s’il n’est pas déjà présent.

Fonctionne sur les environnements :
  - DEMO (https://demo.data.gouv.fr)
  - WWW (production, https://data.gouv.fr)

───────────────────────────────
⚙️  Fonctionnement :
───────────────────────────────
- Par défaut, le script fonctionne en **mode simulation** (`UPDATE_MODE=False`),
  donc aucune écriture réelle n’est effectuée.
- Si `UPDATE_MODE=True`, les modifications sont envoyées à l’API (clé API requise).
- Les tags existants sont **conservés et concaténés** : le script n’écrase jamais
  la liste complète des tags.
- Chaque modification est enregistrée dataset par dataset via la méthode `update()`.

───────────────────────────────
🔐  Variables d’environnement attendues :
───────────────────────────────
- `DATAGOUV_ENV` : "demo" ou "www" (défaut = demo)
- `DEMO_DATA_GOUV_KEY` : clé API pour l’environnement de test
- `DATA_GOUV_KEY` : clé API pour la production (www)

───────────────────────────────
🧩  Bonnes pratiques :
───────────────────────────────
- Tester d’abord en simulation sur DEMO avant de passer en écriture réelle.
- Sauvegarder les métadonnées avant toute mise à jour importante.
- Utiliser un utilisateur membre de l’organisation pour les accès authentifiés.
"""

import os
import httpx
from datagouv import Client

# ───────────────────────────────
# Configuration utilisateur
# ───────────────────────────────
ORG_ID = "534fff91a3a7292c64a77f73"  # Ministère de la Culture
TAG = "culture"                      # Tag à ajouter (sensible à la casse)
UPDATE_MODE = False                  # ⚠️ Simulation si False (aucune écriture)
DEFAULT_ENV = "www"                  # Environnement par défaut si non précisé

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
print(f"🔓 Mode : {'écriture réelle' if UPDATE_MODE else 'simulation (aucune écriture)'}")
print(f"🏛️ Organisation ciblée : {ORG_ID}")
print(f"🏷️ Tag à ajouter : {TAG}")
print("───────────────────────────────\n")

# ───────────────────────────────
# Initialisation du client
# ───────────────────────────────
client = Client(environment=ENVIRONMENT, api_key=API_KEY)
print(f"Connexion à l’environnement {ENVIRONMENT.upper()}...")

organization = client.organization(ORG_ID)
org_label = getattr(organization, "name", getattr(organization, "slug", organization.id))
print("───────────────────────────────")
print(f"🏛️ Organisation : {org_label}")
print(f"🔗 Page : {getattr(organization, 'page', 'Non disponible')}")
print(f"📚 Chargement des jeux de données en cours…")
print("───────────────────────────────\n")

errors = []
added = 0
already_present = 0
total = 0

# ───────────────────────────────
# Parcours des datasets
# ───────────────────────────────
datasets = list(organization.datasets)
print(f"📦 {len(datasets)} jeux de données détectés.\n")

for ds in datasets:
    total += 1
    ds_id = getattr(ds, "id", None)
    title = getattr(ds, "title", None) or getattr(ds, "name", None)

    # Charger le dataset complet (le modèle simplifié ne contient pas tous les champs)
    try:
        full_ds = client.dataset(ds_id)
        tags = getattr(full_ds, "tags", []) or []
    except Exception as e:
        print(f"⚠️ Impossible de charger le dataset complet {ds_id}: {e}")
        errors.append({"id": ds_id, "title": title, "error": str(e)})
        continue

    print(f"→ {title} ({ds_id})")
    print(f"   Tags actuels : {tags}")

    if TAG not in tags:
        new_tags = tags + [TAG]
        print(f"   [Prévu] Ajout du tag : {TAG}")

        if UPDATE_MODE:
            try:
                full_ds.update({"tags": new_tags})
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
    print("\n🧾 Détails des erreurs :")
    for e in errors:
        print(f" - {e['title']} ({e['id']}) → {e['error']}")
