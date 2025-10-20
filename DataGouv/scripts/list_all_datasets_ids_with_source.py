"""
But :
Lister tous les identifiants (id) de datasets présents dans deux sauvegardes DataGouv
(production et démo), indiquer leur provenance (www, demo ou les deux),
et générer un fichier CSV dédoublonné.

Résultat :
- Un fichier CSV `datasets_ids_all.csv` contenant :
  id , source
  (où source ∈ {"www", "demo", "both"})
- Affiche également les statistiques de répartition.
"""

import json
import csv
import os

# ───────────────────────────────
# 🧩 Configuration
# ───────────────────────────────
# ⚠️ Utilise bien les fichiers existants dans ton dépôt
BACKUP_WWW = "DataGouv/scripts/backup/backup_datasets_full_www_2025_10_20.json"
BACKUP_DEMO = "DataGouv/scripts/backup/backup_datasets_full_demo_2025_10_20.json"
OUTPUT_CSV = "DataGouv/scripts/backup/datasets_ids_all.csv"

# ───────────────────────────────
# 📂 Fonction de chargement
# ───────────────────────────────
def load_backup_ids(path):
    """Charge les IDs de datasets depuis un fichier JSON"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("datasets", {}).keys())
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {path}: {e}")
        return set()

# ───────────────────────────────
# 🔄 Fusion et provenance
# ───────────────────────────────
print("───────────────────────────────")
print("📦 Extraction des IDs de datasets...")
www_ids = load_backup_ids(BACKUP_WWW)
demo_ids = load_backup_ids(BACKUP_DEMO)

print(f"📁 WWW (prod) : {len(www_ids)} IDs")
print(f"📁 Demo       : {len(demo_ids)} IDs")

all_ids = sorted(www_ids | demo_ids)
print(f"🧩 Total unique : {len(all_ids)} IDs distincts trouvés\n")

# ───────────────────────────────
# 📊 Calcul des provenances
# ───────────────────────────────
rows = []
for ds_id in all_ids:
    if ds_id in www_ids and ds_id in demo_ids:
        source = "both"
    elif ds_id in www_ids:
        source = "www"
    else:
        source = "demo"
    rows.append((ds_id, source))

# Statistiques simples
count_both = sum(1 for _, s in rows if s == "both")
count_www = sum(1 for _, s in rows if s == "www")
count_demo = sum(1 for _, s in rows if s == "demo")

# ───────────────────────────────
# ✍️ Écriture du CSV final
# ───────────────────────────────
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerow(["id", "source"])
    writer.writerows(rows)

# ───────────────────────────────
# 🧾 Résumé
# ───────────────────────────────
print("───────────────────────────────")
print(f"✅ Fichier généré : {OUTPUT_CSV}")
print(f"📊 Nombre total d’IDs uniques : {len(all_ids)}")
print(f"   • Présents dans les deux  : {count_both}")
print(f"   • Uniquement sur WWW      : {count_www}")
print(f"   • Uniquement sur DEMO     : {count_demo}")
print("───────────────────────────────")
