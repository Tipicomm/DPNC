# -*- coding: utf-8 -*-

import pandas as pd
import openai
import os

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
OUTPUT = "CartoDataMC/cartographie_culture_semantique.csv"

# Clé API OpenAI depuis la variable d'environnement (cf. GitHub Secrets)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv(INPUT, sep=";").head(100)

# Préparation du contexte riche pour chaque propriété
rows_context = []
for _, row in df.iterrows():
    context = (
        f"dataset_title: {row.get('dataset_title','')}"
        f" | tags: {row.get('tags','')}"
        f" | property_name: {row.get('property_name','')}"
        f" | property_type: {row.get('property_type','')}"
    )
    desc = row.get('description','')
    if pd.notna(desc) and desc.strip():
        context += f" | description: {desc}"
    rows_context.append(context)

# Préparer le prompt pour OpenAI
prompt = (
    "Voici une liste de propriétés extraites de jeux de données culturels publics français, chaque ligne comprenant leur contexte (titre du jeu, tags, nom et type de propriété, description si disponible) :\n"
    + "\n".join(rows_context)
    + "\n\nÀ partir de ces informations, propose 8 à 12 grandes classes conceptuelles (types, thèmes, concepts) pour regrouper ces propriétés. "
      "Pour chaque classe, donne un intitulé explicite et liste les propriétés (par leur nom exact) que tu y regroupes.\n"
    + "Présente la réponse au format CSV avec deux colonnes : classe, property_name."
)

response = client.chat.completions.create(
    model="gpt-4-1106-preview",  # modèle gpt-4.1 (OpenAI, juin 2024+)
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
    max_tokens=1800
)

csv_result = response.choices[0].message.content

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(csv_result)

print("✅ Analyse sémantique (contextuelle, gpt-4.1) terminée et exportée dans", OUTPUT)
