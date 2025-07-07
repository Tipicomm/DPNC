# -*- coding: utf-8 -*-
import pandas as pd
import os
from pathlib import Path
import glob
import requests
from time import sleep

INPUT = "CartoDataMC/cartographie_culture_properties_exemples.csv"
AXES_FILE = "CartoDataMC/ModeleMetaMC_UTF8.csv"
OUTPUT_DIR = Path("CartoDataMC/semantique_batches_v2")
FINAL_OUTPUT = "CartoDataMC/cartographie_culture_semantique_v2.csv"

ROW_START, ROW_END = 0, 100  # à adapter selon tes besoins
BATCH_SIZE = 20

# Chargement des données
df_full = pd.read_csv(INPUT, sep=";")
for col in ['exemple_1', 'exemple_2', 'exemple_3']:
    if col not in df_full.columns:
        df_full[col] = ""

df = df_full.iloc[ROW_START:ROW_END].copy()
axes_df = pd.read_csv(AXES_FILE, sep=";")

axes_text = "\n".join(
    f"- {row['Axe']} : {row['Libellé']} — {row['Définition']}"
    for _, row in axes_df.iterrows()
)

# Prompt système
SYSTEM_PROMPT = f"""
Contexte :
Dans le cadre de la cartographie des données du ministère de la Culture, nous cherchons à enrichir sémantiquement les propriétés extraites de jeux de données culturels publics français.

Chaque propriété est décrite par :
- dataset_title : titre du jeu de données source
- tags : mots-clés
- property_name : nom exact de la propriété
- property_type : type de donnée
- description : description éventuelle
- valeurs_exemple : exemples rencontrés

Objectif :
Pour chaque propriété, produire les colonnes suivantes dans un tableau CSV :
- définition : reformulation claire et concise du sens de la propriété
- Axe de référence : choisir parmi les axes MetaMC ci-dessous
- Type référentiel : OUI si la propriété correspond à une nomenclature, NON sinon
- Référentiel alignement : indiquer un alignement reconnu (schema.org, INSEE, etc.) si pertinent

Critères d’analyse :
L'attribution de l'axe MetaMC doit reposer sur une analyse sémantique complète, tenant compte de :
- la signification du nom de la propriété (property_name)
- sa description éventuelle (description)
- les exemples de valeurs (valeurs_exemple)
- le type de donnée (property_type)
- le contexte du jeu de données (dataset_title, tags)

Ne te limite pas au nom : interprète le sens réel de la propriété à partir de tous ces éléments pour choisir l’axe le plus pertinent.

Axes MetaMC :
{axes_text}

Important :
- Ne modifie pas les identifiants
- Ne génère que le tableau CSV avec les colonnes : definition;Axe de référence;Type référentiel;Référentiel alignement
"""

# Fonction d'appel à Mistral local
def interroger_mistral(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        return response.json()["response"]
    except Exception as e:
        print(f"❌ Erreur Mistral : {e}")
        return ""

# Traitement par batch
rows = [df[i:i+BATCH_SIZE] for i in range(0, len(df), BATCH_SIZE)]
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for idx, batch in enumerate(rows):
    output_file = OUTPUT_DIR / f"batch_{idx + 1}.csv"
    if output_file.exists():
        print(f"🟡 Batch {idx + 1} déjà traité.")
        continue

    user_context = []
    for _, row in batch.iterrows():
        context = f"dataset_title: {row['dataset_title']} | tags: {row['tags']} | property_name: {row['property_name']} | property_type: {row['property_type']}"
        if pd.notna(row['description']) and row['description'].strip():
            context += f" | description: {row['description'].strip()}"
        exemples = [e for e in [row.get('exemple_1', ''), row.get('exemple_2', ''), row.get('exemple_3', '')] if pd.notna(e) and e.strip()]
        if exemples:
            context += f" | valeurs_exemple: [{', '.join(exemples[:2])}]"
        user_context.append(context)

    prompt_complet = SYSTEM_PROMPT + "\n" + "\n".join(user_context)

    try:
        print(f"🔄 Traitement batch {idx + 1}")
        texte = interroger_mistral(prompt_complet)
        csv_cleaned = "\n".join(line for line in texte.splitlines() if ";" in line)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(csv_cleaned)

        print(f"✅ Batch {idx + 1} traité avec succès.")
        sleep(2)

    except Exception as e:
        print(f"❌ Erreur batch {idx + 1} : {e}")

# Fusion finale
all_files = glob.glob(str(OUTPUT_DIR / "batch_*.csv"))
df_enrich = pd.concat([pd.read_csv(f, sep=";") for f in all_files if Path(f).stat().st_size > 0], ignore_index=True)
df_enrich.reset_index(drop=True, inplace=True)

columns_to_keep = ['resource_id', 'dataset_id', 'property_name', 'description', 'tags', 'property_type', 'exemple_1', 'exemple_2', 'exemple_3']
df_source = df_full.iloc[ROW_START:ROW_END][columns_to_keep].reset_index(drop=True)
df_final = pd.concat([df_source, df_enrich], axis=1)
df_final.to_csv(FINAL_OUTPUT, sep=";", index=False)

print("✅ Script terminé. Résultat :", FINAL_OUTPUT)
