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

# Plage à traiter (modifiable en un seul endroit)
ROW_START, ROW_END = 1, 10

# Lecture des données sources
df = pd.read_csv(INPUT, sep=";").iloc[ROW_START:ROW_END]
axes_df = pd.read_csv(AXES_FILE, sep=";")

axes_text = "\n".join(f"- {row['Axe']} : {row['Libellé']} — {row['Définition']}" for _, row in axes_df.iterrows())

BATCH_SIZE = 10
batches = [df[i:i + BATCH_SIZE] for i in range(0, len(df), BATCH_SIZE)]
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_TEMPLATE = f"""
Contexte :
Dans le cadre de la cartographie des données du ministère de la Culture, nous cherchons à enrichir sémantiquement les propriétés extraites de jeux de données culturels publics français.

Chaque propriété est décrite par les colonnes suivantes :
- dataset_title : nom du jeu de données d’origine
- tags : mots-clés thématiques
- property_name : identifiant d’une propriété du jeu
- property_type : type de donnée (string, integer, date, bool...)
- description : description textuelle si disponible
- exemple_1 / exemple_2 / exemple_3 : exemples de valeurs réelles rencontrées

Objectif :
Pour chaque propriété analysée, produire les colonnes suivantes :
- définition : une reformulation claire et concise de la signification de la propriété
- Axe de référence : un des axes thématiques du modèle MetaMC ci-dessous
- Type référentiel : OUI si la propriété peut s'aligner sur un référentiel externe connu, NON sinon
- Référentiel alignement : nom du référentiel sémantique le plus pertinent (ex. INSEE, ISO 3166, GeoNames, RAMEAU, BNF, Europeana, schema.org...)

Voici les axes du modèle de référence MetaMC utilisables :

{axes_text}

Important :
- Ne modifie en aucun cas les noms de propriété (property_name), ni les identifiants de données.
- Ne reformule pas les champs existants.
- Présente STRICTEMENT la réponse au format CSV, avec en-têtes : definition;Axe de référence;Type référentiel;Référentiel alignement
- Respecte l’ordre des propriétés reçues.
- Si aucune information n’est possible, laisse une cellule vide sans texte de remplacement.

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
        for col in ['exemple_1', 'exemple_2', 'exemple_3']:
            val = row.get(col, '')
            if pd.notna(val) and val.strip():
                context += f" | {col}: {val}"
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

# Réintégration dans les données sources
df_source = pd.read_csv(INPUT, sep=";").iloc[ROW_START:ROW_END].reset_index(drop=True)
df_final = pd.concat([df_source, df_enrich], axis=1)
df_final.to_csv(FINAL_OUTPUT, sep=";", index=False)

print("✅ Enrichissement sémantique terminé. Fichier final disponible dans", FINAL_OUTPUT)
