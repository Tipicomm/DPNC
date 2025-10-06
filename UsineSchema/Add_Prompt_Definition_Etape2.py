# -*- coding: utf-8 -*-
import pandas as pd
import os
from UsineSchema.config import DATASET_ID, RESOURCE_ID, RESOURCE_contexte

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
rows_context = [
    f"property_name: {row.get('column_name','')}"
    f" | property_type: {row.get('column_datatype','')}"
    f" | dataset_title: {dataset_title}"
    f" | dataset_description: {dataset_description}"
    f" | tags: {row.get('tags.dataset','')}"
    f" | top_values: {row.get('top_1','')}, {row.get('top_2','')}, {row.get('top_3','')}"
    for _, row in df.iterrows()
]

# =======================
# Prompt commun
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
# Sauvegarde dans fichiers temporaires
# =======================
os.makedirs("UsineSchema/tmp", exist_ok=True)
with open("UsineSchema/tmp/prompt.txt", "w", encoding="utf-8") as f:
    f.write(prompt)

with open("UsineSchema/tmp/context.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(rows_context))

print("✅ Prompt et contexte générés dans UsineSchema/tmp/")
