# -*- coding: utf-8 -*-

import pandas as pd
import openai
import os
import re

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
OUTPUT = "CartoDataMC/cartographie_culture_semantique.csv"

# Clé API OpenAI depuis la variable d'environnement (cf. GitHub Secrets)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv(INPUT, sep=";").head(20)

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

# Préparer le prompt pour OpenAI, avec consigne stricte de format
prompt = (
    "Voici une liste de propriétés extraites de jeux de données culturels publics français, chaque ligne comprenant leur contexte (titre du jeu, tags, nom et type de propriété, description si disponible) :\n"
    + "\n".join(rows_context)
    + "\n\nÀ partir de ces informations, propose 8 à 12 grandes classes conceptuelles (types, thèmes, concepts) pour regrouper ces propriétés. "
      "Pour chaque classe, donne un intitulé explicite et liste les propriétés (par leur nom exact) que tu y regroupes.\n"
    + "Présente STRICTEMENT la réponse au format CSV avec deux colonnes intitulées classe et property_name, séparateur point-virgule (« ; »), sans aucune ligne vide, phrase, commentaire ou texte hors tableau avant ou après."
)

response = client.chat.completions.create(
    model="gpt-4o",   # <= modèle universel, moderne, accessible
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
    max_tokens=1800
)

csv_result = response.choices[0].message.content

# Nettoyage : ne garder que les lignes contenant le séparateur ';'
lines = csv_result.splitlines()
csv_cleaned = "\n".join(line for line in lines if ";" in line)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(csv_cleaned)

print("✅ Analyse sémantique (gpt-4o) terminée, résultat nettoyé, exporté dans", OUTPUT)
