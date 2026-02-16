# -*- coding: utf-8 -*-
import requests
import pandas as pd
import csv
import os

# =======================
# Paramètres
# =======================
TAG = "deps-doc"
API_BASE = "https://www.data.gouv.fr/api/1/datasets/"
PAGE_SIZE = 100  # 100 est généralement un bon compromis

# =======================
# 1. Récupération de tous les datasets portant le tag (avec pagination)
# =======================
datasets = []
page = 1

while True:
    params = {
        "tag": TAG,
        "page": page,
        "page_size": PAGE_SIZE,
    }
    resp = requests.get(API_BASE, params=params, timeout=60)
    resp.raise_for_status()
    payload = resp.json()

    for ds in payload.get("data", []):
        org = ds.get("organization") or {}
        datasets.append({
            "dataset_id": ds.get("id", ""),
            "dataset_slug": ds.get("slug", ""),
            "title": ds.get("title", ""),
            "description": ds.get("description", ""),
            "tags": ";".join([str(t) for t in (ds.get("tags") or [])]),
            "organization_id": org.get("id", ""),
            "organization_name": org.get("name", ""),
            "created_at": ds.get("created_at", ""),
            "last_modified": ds.get("last_modified", ""),
            "resources_count": len(ds.get("resources") or []),
            "page_url": ds.get("page", ""),   # URL publique du dataset
            "uri": ds.get("uri", ""),         # URI API (souvent présente)
        })

    # Si next_page est null/vide => fini
    if not payload.get("next_page"):
        break

    page += 1

# =======================
# 2. Export CSV
# =======================
df = pd.DataFrame(datasets)

os.makedirs("UsineSchema", exist_ok=True)
output_file = f"UsineSchema/datasets_tag_{TAG}.csv"
df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL, quotechar='"', encoding="utf-8")

print(f"✅ {len(df)} jeux de données récupérés. Fichier généré : {output_file}")
