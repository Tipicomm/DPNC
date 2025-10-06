# -*- coding: utf-8 -*-
import pandas as pd
import openai
import os
import io

# =======================
# Paramètres
# =======================
DATASET_ID = "6842b8e772325215e9dbf196"
RESOURCE_ID = "ad59533c-1c18-4eb4-a079-7e061ec5dbcd"

# Fichier de contextualisation produit en étape 1
RESOURCE_contexte = f"UsineSchema/schema_{DATASET_ID}_{RESOURCE_ID}.csv"

# Fichier enrichi produit en étape 2
OUTPUT = f"UsineSchema/schema_enrichi_{DATASET_ID}_{RESOURCE_ID}.csv"

# Initialiser client OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =======================
# Lecture du fichier de contextualisation
# =======================
if not os.path.exists(RESOURCE_contexte):
    raise FileNotFoundError(f"Fichier introuvable: {RESOURCE_contexte} (as-tu exécuté l’étape 1 ?)")

df = pd.read_csv(RESOURCE_contexte, sep=",")

# Récupérer titre et description du dataset
dataset_title = df["title.dataset"].iloc[0] if "title.dataset" in df.columns else ""
dataset_description = df["description.dataset"].iloc[0] if "description.dataset" in df.columns else ""

# =======================
# Préparation du contexte des propriétés
# =======================
rows_context = []
for _, row in df.iterrows():
    context = (
        f"property_name: {row.get('column_name','')}"
        f" | property_type: {row.get('column_datatype','')}"
        f" | dataset_title: {dataset_title}"
        f" | dataset_description: {dataset_description}"
        f" | tags: {row.get('tags.dataset','')}"
        f" | top_values: {row.get('top_1','')}, {row.get('top_2','')}, {row.get('top_3','')}"
    )
    rows_context.append(context)

# =======================
# Prompt pour définitions
# =======================
prompt = f"""
Voici une liste de propriétés issues du jeu : {dataset_title}
Description du dataset : {dataset_description}

Chaque ligne ci-dessous décrit le contexte d'une propriété :
- nom de la propriété (column_name)
- type de donnée (column_datatype)
- titre et description du jeu de données
- quelques valeurs fréquentes (top_values)

Ta tâche est la suivante pour CHAQUE propriété :

1. Colonne "definition" :
   Propose une définition claire, précise et compréhensible en une phrase,
   adaptée à un public professionnel travaillant sur des données culturelles.

⚠️ Contraintes de sortie :
- Présente STRICTEMENT la réponse au format CSV.
- Le CSV doit avoir exactement deux colonnes : property_name;definition
- Utilise « ; » comme séparateur.
- N’ajoute AUCUNE ligne vide, aucun commentaire, ni texte hors tableau avant ou après.
- Conserve le nom exact de la propriété tel qu’il apparaît dans property_name.
"""

# =======================
# Appel API OpenAI
# =======================
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt + "\n\n" + "\n".join(rows_context)}],
    temperature=0.2,
    max_tokens=4000
)

csv_result = response.choices[0].message.content or ""

# Nettoyage : garder uniquement les lignes contenant ';'
lines = [line for line in csv_result.splitlines() if ";" in line]
csv_cleaned = "\n".join(lines)

# Conversion en DataFrame (definition jointe aux colonnes)
df_defs = pd.read_csv(io.StringIO(csv_cleaned), sep=";")

# Fusion avec le dataframe d'origine (ajout de la colonne definition)
df_merged = df.merge(df_defs, left_on="column_name", right_on="property_name", how="left")

# Supprimer la colonne "property_name" qui est redondante
if "property_name" in df_merged.columns:
    df_merged = df_merged.drop(columns=["property_name"])

# =======================
# Export
# =======================
os.makedirs("UsineSchema", exist_ok=True)
df_merged.to_csv(OUTPUT, index=False, encoding="utf-8")

print(f"✅ Fichier enrichi exporté dans {OUTPUT} ({len(df_merged)} propriétés)")
