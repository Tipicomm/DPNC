"""
But :
Comparer deux sauvegardes DataGouv (production vs démo)
et produire la liste des jeux de données présents dans les deux fichiers JSON,
en se basant sur l'identifiant du dataset.

Résultat :
- Un fichier CSV "datasets_common.csv" contenant :
  id ; title_prod ; title_demo ; frequency_prod ; frequency_demo
- Affiche également le nombre total de jeux communs.

Convention :
X = prod / www → référence principale
Y = demo → environnement de test / comparaison

⚙️ Exemple d’utilisation :
python DataGouv/scripts/compare_backups.py
"""

import json
import csv
import os

# ───────────────────────────────
# 🧩 Configuration
# ───────────────────────────────
# Chemins des deux sauvegardes à comparer
BACKUP_PROD = "DataGouv/scripts/backup/backup_datasets_full_prod_2025_10_20.json"
BACKUP_DEMO = "DataGouv/scripts/backup/backup_datasets_full_demo_2025_10_20.json"

# Fichier de sortie
OUTPUT_CSV = "DataGouv/scripts/backup/datasets_common.csv"

# ───────────────────────────────
# 📂 Chargement des fichiers
# ───────────────────────────────
def load_backup(path):
    """Charge un fichier JSON et renvoie le dictionnaire des datasets"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("datasets", {})
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {path}: {e}")
        return {}

print("───────────────────────────────")
print("📦 Chargement des sauvegardes...")
prod_datasets = load_backup(BACKUP_PROD)
demo_datasets = load_backup(BACKUP_DEMO)

print(f"📁 Prod : {len(prod_datasets)} jeux de données")
print(f"📁 Demo : {len(demo_datasets)} jeux de données")

# ───────────────────────────────
# 🔍 Recherche des jeux communs
# ───────────────────────────────
common_ids = set(prod_datasets.keys()) & set(demo_datasets.keys())
print(f"🤝 Jeux de données communs : {len(common_ids)} trouvés\n")

# ───────────────────────────────
# ✍️ Écriture du CSV
# ───────────────────────────────
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=";")
    writer.writerow(["id", "title_prod", "title_demo", "frequency_prod", "frequency_demo"])

    for ds_id in sorted(common_ids):
        ds_prod = prod_datasets.get(ds_id, {})
        ds_demo = demo_datasets.get(ds_id, {})

        writer.writerow([
            ds_id,
            ds_prod.get("title", ""),
            ds_demo.get("title", ""),
            ds_prod.get("frequency", ""),
            ds_demo.get("frequency", "")
        ])

print("───────────────────────────────")
print(f"✅ Fichier généré : {OUTPUT_CSV}")
print(f"📊 Nombre de jeux communs : {len(common_ids)}")
print("───────────────────────────────")

# ───────────────────────────────
# 🔍 Exemple d’aperçu console
# ───────────────────────────────
print("🔍 Exemples de jeux communs :")
for ds_id in list(sorted(common_ids))[:5]:
    print(f" - {ds_id}")
    print(f"   • title_prod : {prod_datasets[ds_id].get('title')}")
    print(f"   • title_demo : {demo_datasets[ds_id].get('title')}")
    print(f"   • frequency  : {prod_datasets[ds_id].get('frequency')} / {demo_datasets[ds_id].get('frequency')}")
print("───────────────────────────────")
