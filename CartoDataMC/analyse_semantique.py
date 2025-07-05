# -*- coding: utf-8 -*-

import os
import pandas as pd
import openai
from tqdm import tqdm

# 📁 Dossier des données
DOSSIER = "CartoDataMC"
FICHIER_ENTREE = f"{DOSSIER}/Cartographie_Culture_properties.csv"
FICHIER_SORTIE = f"{DOSSIER}/Cartographie_Culture_clusters.csv"

# 🔑 Récupération de la clé API (à définir dans GitHub Secrets : OPENAI_API_KEY)
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📥 Charger les données
df = pd.read_csv(FICHIER_ENTREE).head(100)  # Analyse sur les 100 premières lignes

# 🧠 Requête GPT pour chaque propriété
descriptions = []

for _, row in tqdm(df.iterrows(), total=len(df), desc="🔍 Analyse sémantique"):
    context = f"""
    La propriété suivante est issue d’un jeu de données culturels publics :
    
    - Nom de la propriété : {row['property_name']}
    - Type : {row['property_type']}
    - Titre du jeu de données : {row.get('dataset_title', '')}
    - Description : {row.get('description', '')}
    - Tags : {row.get('tags', '')}
    
    Donne une catégorie sémantique simple et compréhensible pour regrouper cette propriété (ex : "informations administratives", "localisation", "données temporelles", "identifiants", "relations", etc.).
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un assistant qui classe les propriétés de jeux de données culturels selon leur nature sémantique."},
                {"role": "user", "content": context}
            ],
            temperature=0.2,
            max_tokens=100
        )
        category = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        category = f"Erreur : {str(e)}"

    descriptions.append(category)

# ➕ Ajouter les résultats à la table
df["semantic_category"] = descriptions

# 💾 Sauvegarder
df.to_csv(FICHIER_SORTIE, index=False)
print(f"✅ Catégorisation sémantique enregistrée dans : {FICHIER_SORTIE}")
