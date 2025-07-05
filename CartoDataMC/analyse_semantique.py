# -*- coding: utf-8 -*-

import pandas as pd
import openai
import os

# Assure-toi d’avoir défini OPENAI_API_KEY dans les secrets ou les variables d’environnement GitHub Actions
openai.api_key = os.getenv("OPENAI_API_KEY")

INPUT = "CartoDataMC/cartographie_culture_properties.csv"
OUTPUT = "CartoDataMC/cartographie_culture_semantique.csv"

df = pd.read_csv(INPUT, sep=";").head(100)

# Pour l’exemple, on ne traite que les noms de propriété
property_names = df["property_name"].dropna().unique().tolist()

# Préparer la requête (prompt) pour l’API OpenAI
prompt = (
    "Voici une liste de noms de propriétés issues de jeux de données culturels publics français :\n"
    + "\n".join(property_names)
    + "\n\nPropose 8 à 12 grandes classes (types/concepts) pour regrouper ces propriétés, avec un intitulé pour chaque classe, et liste les propriétés associées à chaque classe.\n"
    + "Présente la réponse au format CSV avec deux colonnes : classe, property_name."
)

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
    max_tokens=1500
)

# Extraire le texte CSV de la réponse
csv_result = response["choices"][0]["message"]["content"]

# Sauvegarder tel quel (pour contrôle)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(csv_result)

print("✅ Analyse sémantique terminée et exportée dans", OUTPUT)
