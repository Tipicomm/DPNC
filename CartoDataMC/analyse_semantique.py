# analyse_semantique.py

import pandas as pd
import openai
import os
import time

# 🔑 Clé API depuis la variable d’environnement
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📥 Charger les 100 premières lignes du fichier
INPUT_CSV = "CartoDataMc/Cartographie_Culture_properties.csv"
df = pd.read_csv(INPUT_CSV).head(100)

# 🧠 Préparer les requêtes vers l’API
def generer_prompt(property_name, description, tags):
    return f"""
Tu es un expert des données culturelles publiques. À partir du nom de propriété suivant :

- Propriété : {property_name}
- Description du jeu de données : {description}
- Mots-clés : {tags}

Propose une **catégorie générique** (classe) à laquelle cette propriété appartient (exemple : date, localisation, personne, type de structure, œuvre, événement, usage, budget, etc.).
Ta réponse doit être une seule **classe** courte, sans phrase explicative.
"""

# 🗂 Stocker les résultats
classes = []

for _, row in df.iterrows():
    prop = row.get("property_name", "")
    desc = row.get("description", "")
    tags = row.get("tags", "")
    
    prompt = generer_prompt(prop, desc, tags)
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un expert en science des données culturelles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        classe = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        classe = f"❌ {str(e)}"

    classes.append(classe)
    time.sleep(1)  # ⚠️ Pause pour éviter les limites d'usage API

# ✅ Ajout des classes au DataFrame
df["classe_semantique"] = classes

# 💾 Export du fichier enrichi
OUTPUT_CSV = "CartoDataMc/Cartographie_Culture_classes.csv"
df.to_csv(OUTPUT_CSV, index=False)

print(f"✅ Analyse sémantique terminée. Résultat enregistré dans : {OUTPUT_CSV}")
