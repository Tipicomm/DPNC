"""
But :
Comparer deux sauvegardes DataGouv (production vs démo)
et produire la liste des jeux de données présents dans les deux fichiers JSON,
en se basant sur l'identifiant du dataset.

Résultat :
- Un fichier CSV "datasets_common.csv" contenant :
  id , title_www , title_demo , frequency_www , frequency_demo
- Affiche également le nombre total de jeux communs.

Convention :
X = www (prod) → référence principale
Y = demo → environnement de test / comparaison

⚙️ Exemple d’utilisation :
python DataGouv/scripts/compare_backups_datasets_prod_vs_demo.py
"""

import json
import csv
import os

# ───────────────────────────────
# 🧩 Configuration
# ───────────────────────────────
# Chemins des deux sauvegardes à comparer
BACKUP_WWW = "DataGouv/scripts/backup/backup_datasets_full_www_2025_10_20.json"
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
www_datasets = load_backup(BACKUP_WWW)
demo_datasets = load_backup(BACKUP_DEMO)

print(f"📁 WWW (prod) : {len(www_datasets)} jeux de données")
print(f"📁 Demo       : {len(demo_datasets)} jeux de données")

# ───────────────────────────────
# 🔍 Recherche des jeux communs
# ───────────────────────────────
common_ids = set(www_datasets.keys()) & set(demo_datasets.keys())
print(f"🤝 Jeux de données communs : {len(common_ids)} trouvés\n")

# ───────────────────────────────
# ✍️ Écriture du CSV
# ───────────────────────────────
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerow(["id", "title_www", "title_demo", "frequency_www", "frequency_demo"])

    for ds_id in sorted(common_ids):
        ds_www = www_datasets.get(ds_id, {})
        ds_demo = demo_datasets.get(ds_id, {})

        writer.writerow([
            ds_id,
            ds_www.get("title", ""),
            ds_demo.get("title", ""),
            ds_www.get("frequency", ""),
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
    print(f"   • title_www : {www_datasets[ds_id].get('title')}")
    print(f"   • title_demo : {demo_datasets[ds_id].get('title')}")
    print(f"   • frequency  : {www_datasets[ds_id].get('frequency')} / {demo_datasets[ds_id].get('frequency')}")
print("───────────────────────────────")
