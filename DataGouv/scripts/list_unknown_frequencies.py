"""
But :
Lister tous les jeux de données de production ayant une fréquence "unknown"
à partir du backup complet DataGouv.

Entrée :
- Fichier JSON (backup complet) : backup_datasets_full_www_YYYY_MM_DD.json

Sortie :
- Fichier CSV : datasets_to_fix.csv
  Contenant : id, title, old_frequency

⚙️ Exemple d’utilisation :
python DataGouv/scripts/list_unknown_frequencies.py

Ce script ne modifie rien. Il prépare la base pour le script 2
(update_frequencies_from_list.py) qui fera les mises à jour réelles.
"""

import os
import json
import csv
from datetime import datetime

# ───────────────────────────────
# ⚙️ Configuration
# ───────────────────────────────
BACKUP_PROD_PATH = "DataGouv/scripts/backup/backup_datasets_full_www_2025_10_20.json"
OUTPUT_CSV_PATH = "DataGouv/scripts/backup/datasets_to_fix.csv"

# ───────────────────────────────
# 📦 Chargement du fichier JSON
# ───────────────────────────────
if not os.path.exists(BACKUP_PROD_PATH):
    raise FileNotFoundError(f"❌ Fichier introuvable : {BACKUP_PROD_PATH}")

print(f"📦 Chargement du backup de production : {BACKUP_PROD_PATH}")
with open(BACKUP_PROD_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

datasets = data.get("datasets", {})
print(f"🔍 {len(datasets)} jeux de données trouvés dans le backup.\n")

# ───────────────────────────────
# 🧩 Filtrage des "unknown"
# ───────────────────────────────
to_fix = []
for ds_id, ds in datasets.items():
    freq = (ds.get("frequency") or "").strip().lower()
    if freq == "unknown":
        to_fix.append({
            "id": ds_id,
            "title": ds.get("title", ""),
            "old_frequency": freq
        })

print(f"🧮 {len(to_fix)} jeux de données avec frequency='unknown' détectés.\n")

# ───────────────────────────────
# ✍️ Écriture du fichier CSV
# ───────────────────────────────
os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)

with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["id", "title", "old_frequency"])
    for row in to_fix:
        writer.writerow([row["id"], row["title"], row["old_frequency"]])

# ───────────────────────────────
# 📊 Bilan
# ───────────────────────────────
print("───────────────────────────────")
print(f"✅ Liste exportée vers : {OUTPUT_CSV_PATH}")
print(f"📊 Nombre total à corriger : {len(to_fix)}")
print("───────────────────────────────")

# Aperçu rapide
for row in to_fix[:10]:
    print(f" - {row['title']} ({row['id']}) → {row['old_frequency']}")
if len(to_fix) > 10:
    print(f"   ... et {len(to_fix) - 10} autres jeux de données.")
print("───────────────────────────────")
