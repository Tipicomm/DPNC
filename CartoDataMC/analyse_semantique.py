# -*- coding: utf-8 -*-

import pandas as pd
import openai
import os
from tqdm import tqdm

# 🗝️ Charger la clé API OpenAI depuis les variables d’environnement
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📂 Charger le fichier contenant les propriétés
df = pd.read_csv("CartoDataMC/cartographie_properties.csv").head(100)

# 🧠 Préparer les propriétés à analyser
property_descriptions = [
    f"- {row['property_name']} (type: {row['property_type']})"
    for _, row in df.iterrows()
]

prompt = f"""
Tu es un expert en modélisation de données dans le domaine culturel. 
Voici une liste de propriétés issues de jeux de données publics :

{chr(10).join(property_descriptions)}

Ta mission :
1. Regrouper ces propriétés en grandes **classes sémantiques** (ex : identifiants, dates, géolocalisation, œuvres, institutions, personnes, statistiques...).
2. Pour chaque classe, lister les noms de propriétés correspondants.
3. Être concis et structuré : réponse en Markdown avec titres pour chaque classe.

Merci.
"""

# ✨ Appel à l’API OpenAI (GPT-4-turbo ou 3.5-turbo selon ton plan)
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Tu es un assistant expert en ontologies de données culturelles."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.4,
    max_tokens=1500
)

# 💾 Sauvegarder la réponse dans un fichier Markdown
with open("CartoDataMC/semantic_grouping.md", "w", encoding="utf-8") as f:
    f.write(response["choices"][0]["message"]["content"])

print("✅ Analyse sémantique terminée. Résultat enregistré dans CartoDataMC/semantic_grouping.md")
