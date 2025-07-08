# -*- coding: utf-8 -*-
import pandas as pd
import requests
import io
import csv

DOSSIER = "CartoDataMC"

# 1. Télécharger les ressources
url_ressources = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets-resources.csv"
r = requests.get(url_ressources)
r.encoding = "utf-8"
try:
    df_ress = pd.read_csv(io.StringIO(r.text), sep=";")
except:
    df_ress = pd.read_csv(io.StringIO(r.text), sep=",")
df_ress = df_ress[df_ress["format"].str.lower() == "csv"]
df_ress = df_ress[["id", "dataset.id", "dataset.title"]].rename(columns={
    "id": "id.ressource",
    "dataset.id": "id.dataset",
    "dataset.title": "title.dataset"
})

# 2. Télécharger les jeux de données
url_datasets = "https://www.data.gouv.fr/api/1/organizations/ministere-de-la-culture-et-de-la-communication/datasets.csv"
r2 = requests.get(url_datasets)
r2.encoding = "utf-8"
try:
    df_ds = pd.read_csv(io.StringIO(r2.text), sep=";")
except:
    df_ds = pd.read_csv(io.StringIO(r2.text), sep=",")
df_ds = df_ds[["id", "title", "description", "tags"]].rename(columns={
    "id": "id.dataset",
    "title": "title.dataset",
    "description": "description.dataset",
    "tags": "tags.dataset"
})

# 3. Jointure
df_joint = pd.merge(df_ress, df_ds, on="id.dataset", how="left")
if "title.dataset_x" in df_joint and "title.dataset_y" in df_joint:
    df_joint = df_joint.drop(columns=["title.dataset_y"]).rename(columns={"title.dataset_x": "title.dataset"})

# 4. Récupération du profil tabulaire enrichi
lignes = []
for _, row in df_joint.iterrows():
    rid = row["id.ressource"]
    api = f"https://tabular-api.data.gouv.fr/api/resources/{rid}/profile/"
    try:
        resp = requests.get(api)
        if resp.status_code != 200:
            continue
        profile = resp.json().get("profile", {})
        colonnes = profile.get("columns", {})
        statistiques = profile.get("profile", {})
        for nom_col in profile.get("header", []):
            col_meta = colonnes.get(nom_col, {})
            stats = statistiques.get(nom_col, {})
            tops = stats.get("tops", [])
            ligne = {
                "id.ressource": rid,
                "id.dataset": row["id.dataset"],
                "title.dataset": row["title.dataset"],
                "description.dataset": row["description.dataset"],
                "tags.dataset": row["tags.dataset"],
                "column_name": nom_col,
                "column_datatype": col_meta.get("format", ""),
                "python_type": col_meta.get("python_type", ""),
                "score": col_meta.get("score", ""),
                "nb_distinct": stats.get("nb_distinct", ""),
                "nb_missing_values": stats.get("nb_missing_values", ""),
                "top_1": tops[0]["value"] if len(tops) > 0 else "",
                "top_2": tops[1]["value"] if len(tops) > 1 else "",
                "top_3": tops[2]["value"] if len(tops) > 2 else "",
            }
            lignes.append(ligne)
    except Exception as e:
        print(f"⚠️ Erreur pour {rid} : {e}")
        continue

df_props = pd.DataFrame(lignes)

# 5. Export enrichi
df_props.to_csv(
    f"{DOSSIER}/cartographie_ressources_datasets_proprietes.csv",
    index=False,
    quoting=csv.QUOTE_ALL,
    quotechar='"',
    encoding="utf-8"
)
print("✅ cartographie_ressources_datasets_proprietes.csv enrichi généré")
