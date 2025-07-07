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

# Lecture des données sources (plage 60 à 140 pour test ciblé)
df = pd.read_csv(INPUT, sep=";").iloc[1:10]
axes_df = pd.read_csv(AXES_FILE, sep=";")

axes_text = "\n".join(f"- {row['Axe']} : {row['Libellé']} — {row['Définition']}" for _, row in axes_df.iterrows())

BATCH_SIZE = 10
batches = [df[i:i + BATCH_SIZE] for i in range(0, len(df), BATCH_SIZE)]
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_TEMPLATE = f"""
Contexte :
Dans le cadre de la cartographie des données du ministère de la Culture, nous cherchons à catégoriser les propriétés issues de jeux de données culturels selon des axes sémantiques de référence.

Les données sources sont décrites à travers les colonnes suivantes :
- dataset_title
- tags
- property_name
- property_type
- description
- exemple_1
- exemple_2
- exemple_3

Objectif :
Analyser par lot un ensemble de propriétés afin d’identifier leur signification sémantique, et les aligner avec le métamodèle MetaMC, qui comporte 10 axes thématiques principaux décrits ci-dessous :

{axes_text}

Consignes :
Pour chaque propriété analysée, produis une ligne dans un tableau CSV respectant les colonnes suivantes :
- resource_id : identifiant unique de la propriété, sous la forme “{{dataset_id}}_{{property_name}}”
- dataset_id : identifiant du jeu de données source
- property_name : nom exact de la propriété
- définition : une reformulation claire et concise de la signification de la propriété (à partir du contexte fourni)
- Axe de référence : un des axes du modèle MetaMC (ex. « AX02 - Œuvre ou bien culturel »)
- Type référentiel : OUI si la propriété peut s’aligner sur un référentiel externe ou un standard, NON sinon
- Référentiel alignement : nom du référentiel ou standard associé (ex. schema.org, DCAT, Europeana, Joconde…)

Important :
- Présente strictement la réponse au format CSV, séparateur point-virgule (« ;»), sans texte avant ou après.
- Ne laisse aucune ligne vide.
- Si l’information est incertaine, propose une hypothèse plausible justifiée par le contexte.
- Utilise uniquement les axes du modèle MetaMC comme regroupement de référence.

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
df_final = pd.concat([pd.read_csv(f, sep=";") for f in all_files if Path(f).stat().st_size > 0], ignore_index=True)
df_final.drop_duplicates(inplace=True)
df_final.to_csv(FINAL_OUTPUT, sep=";", index=False)

print("✅ Traitement par lot terminé. Fichier final disponible dans", FINAL_OUTPUT)
