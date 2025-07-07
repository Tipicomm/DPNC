# -*- coding: utf-8 -*-

import pandas as pd
import os
from pathlib import Path
import glob

try:
    import openai
except ImportError:
    raise ImportError("Le module 'openai' est manquant. Installez-le via 'pip install openai'")

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
AXES_FILE = "CartoDataMC/ModeleMetaMC_UTF8.csv"
OUTPUT_DIR = Path("CartoDataMC/semantique_batches")
FINAL_OUTPUT = "CartoDataMC/cartographie_culture_semantique.csv"

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ROW_START, ROW_END = 0, 4

df_full = pd.read_csv(INPUT, sep=";")
available_columns = df_full.columns.tolist()

for col in ['exemple_1', 'exemple_2', 'exemple_3']:
    if col not in df_full.columns:
        df_full[col] = ""

df = df_full.iloc[ROW_START:ROW_END].copy()
axes_df = pd.read_csv(AXES_FILE, sep=";")

axes_text = "\n".join(f"- {row['Axe']} : {row['Libellé']} — {row['Définition']}" for _, row in axes_df.iterrows())

BATCH_SIZE = 10
batches = [df[i:i + BATCH_SIZE] for i in range(0, len(df), BATCH_SIZE)]
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_TEMPLATE = f"""
Contexte :
Dans le cadre de la cartographie des données du ministère de la Culture, nous cherchons à enrichir sémantiquement les propriétés extraites de jeux de données culturels publics français.

Chaque propriété est décrite par :
- dataset_title : titre du jeu de données source
- tags : mots-clés fournis
- property_name : nom exact de la propriété
- property_type : type de donnée (ex : string, integer, boolean...)
- description : description éventuelle fournie
- valeurs_exemple : exemples de valeurs rencontrées dans le jeu de données (format libre)

Objectif :
Pour chaque propriété analysée, produire les colonnes suivantes :
- définition : une reformulation claire et concise du sens de la propriété, en s’appuyant sur les exemples si utiles
- Axe de référence : l’un des axes MetaMC ci-dessous
- Type référentiel : OUI si la propriété désigne une liste de valeurs fermées, un code ou une nomenclature normalisée (ex : statut, type, catégorie), NON sinon
- Référentiel alignement : uniquement si reconnu dans schema.org ou les nomenclatures de l’INSEE (code commune, département, région, etc.). Laisser vide sinon.

Voici les axes du modèle de référence MetaMC :

{axes_text}

Important :
- Ne modifie jamais les noms ou identifiants d’origine
- N’invente pas de référentiels si aucun ne s’impose clairement
- Présente uniquement le tableau CSV avec les 4 colonnes suivantes : definition;Axe de référence;Type référentiel;Référentiel alignement
- Une ligne par propriété analysée, dans le même ordre qu’en entrée

Voici les propriétés à enrichir :

{{contexte}}
"""

for idx, batch in enumerate(batches):
    output_file = OUTPUT_DIR / f"batch_{idx + 1}.csv"
    if output_file.exists():
        print(f"🟡 Batch {idx + 1} déjà traité, on saute.")
        continue

    rows_context = []
    for _, row in batch.iterrows():
        context = (
            f"dataset_title: {row.get('dataset_title', '')}"
            f" | tags: {row.get('tags', '')}"
            f" | property_name: {row.get('property_name', '')}"
            f" | property_type: {row.get('property_type', '')}"
        )
        desc = row.get('description', '')
        if pd.notna(desc) and desc.strip():
            context += f" | description: {desc}"
        exemples = [row.get(col, '') for col in ['exemple_1', 'exemple_2', 'exemple_3'] if pd.notna(row.get(col, '')) and row.get(col, '').strip()]
        if exemples:
            context += f" | valeurs_exemple: [{', '.join(exemples)}]"
        rows_context.append(context)

    full_prompt = PROMPT_TEMPLATE.replace("{contexte}", "\n".join(rows_context))

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.2,
            max_tokens=1800
        )
        csv_result = response.choices[0].message.content
        csv_cleaned = "\n".join(line for line in csv_result.splitlines() if ";" in line)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(csv_cleaned)

    except Exception as e:
        print(f"❌ Erreur lors du traitement du batch {idx + 1} : {e}")
        continue

all_files = glob.glob(str(OUTPUT_DIR / "batch_*.csv"))
df_enrich = pd.concat([pd.read_csv(f, sep=";") for f in all_files if Path(f).stat().st_size > 0], ignore_index=True)
df_enrich.reset_index(drop=True, inplace=True)

columns_to_keep = ['resource_id', 'dataset_id', 'property_name', 'description', 'tags', 'property_type', 'exemple_1', 'exemple_2', 'exemple_3']
df_source = df_full.iloc[ROW_START:ROW_END][columns_to_keep].reset_index(drop=True)
df_final = pd.concat([df_source, df_enrich], axis=1)
df_final.to_csv(FINAL_OUTPUT, sep=";", index=False)

print("✅ Enrichissement sémantique terminé. Fichier final disponible dans", FINAL_OUTPUT)
