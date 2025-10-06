# -*- coding: utf-8 -*-
import pandas as pd
import openai
import os

# =======================
# Paramètres
# =======================
DATASET_ID = "6842b8e772325215e9dbf196"
RESOURCE_ID = "ad59533c-1c18-4eb4-a079-7e061ec5dbcd"

# Fichier de contextualisation produit en étape 1 (à ajuster manuellement si besoin)
RESOURCE_contexte = f"schema_{DATASET_ID}_{RESOURCE_ID}.csv"

# Fichier enrichi produit en étape 2
OUTPUT = f"schema_semantique_{DATASET_ID}_{RESOURCE_ID}.csv"

# Initialiser client OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =======================
# Lecture du fichier de contextualisation
# =======================
df = pd.read_csv(RESOURCE_contexte, sep=",")

# Limiter le nombre de propriétés (par exemple 50 premières lignes)
df = df.head(50)

# Récupérer titre et description du dataset (mêmes valeurs pour toutes les lignes, on prend la première)
dataset_title = df["title.dataset"].iloc[0] if "title.dataset" in df.columns else ""
dataset_description = df["description.dataset"].iloc[0] if "description.dataset" in df.columns else ""

# Préparation du contexte des propriétés
rows_context = []
for _, row in df.iterrows():
    context = (
        f"property_name: {row.get('column_name','')}"
        f" | property_type: {row.get('column_datatype','')}"
        f" | dataset_title: {row.get('title.dataset','')}"
        f" | dataset_description: {row.get('description.dataset','')}"
        f" | tags: {row.get('tags.dataset','')}"
        f" | top_values: {row.get('top_1','')}, {row.get('top_2','')}, {row.get('top_3','')}"
    )
    rows_context.append(context)

# =======================
# Prompt pour définitions + référentiels
# =======================
prompt = f"""
Voici une liste de propriétés issues du jeu : {dataset_title}
Description du dataset : {dataset_description}
Fichier de contextualisation utilisé : {RESOURCE_contexte}

Chaque ligne ci-dessous décrit le contexte d'une propriété :
- nom de la propriété (column_name)
- type de donnée (column_datatype)
- titre et description du jeu de données
- quelques valeurs fréquentes (top_values)

Ta tâche est la suivante pour CHAQUE propriété :

1. Colonne "Definition" :
   Propose une définition claire, précise et compréhensible en une phrase,
   adaptée à un public professionnel travaillant sur des données culturelles.

2. Colonne "ReferentielEstime" :
   Propose un alignement avec un référentiel standard si pertinent, parmi :
   - schema.org
   - Dublin Core (dcterms)
   - INSEE (identifiants, codes géographiques…)
   - IdRef / ISNI / VIAF
   - CIDOC CRM (patrimoine, musées)
   - autres référentiels ouverts de confiance.
   Si aucun référentiel n’est pertinent, laisse la cellule vide.

⚠️ Contraintes de sortie :
- Présente STRICTEMENT la réponse au format CSV.
- Le CSV doit avoir exactement trois colonnes : property_name;Definition;ReferentielEstime
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
    max_tokens=2000
)

csv_result = response.choices[0].message.content

# Nettoyage : garder uniquement les lignes contenant ';'
lines = csv_result.splitlines()
csv_cleaned = "\n".join(line for line in lines if ";" in line)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(csv_cleaned)

print(f"✅ Définitions + référentiels exportés dans {OUTPUT} (limité à {len(df)} propriétés)")
