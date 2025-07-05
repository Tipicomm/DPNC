import pandas as pd
import openai
import os

# 📥 Charger le fichier des propriétés
df = pd.read_csv("CartoDataMC/Cartographie_Culture_properties.csv").dropna(subset=["property_name"]).head(100)

# 🧠 Regrouper les noms uniques
proprietes_uniques = sorted(df["property_name"].unique().tolist())

# 🔑 Clé API (assurez-vous qu'elle est bien disponible comme secret GitHub)
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✉️ Préparer le prompt
prompt = (
    "Tu es expert en gouvernance des données pour le ministère de la Culture.\n"
    "Voici une liste de noms de colonnes extraites de fichiers CSV. "
    "Regroupe-les en grandes familles de propriétés sémantiquement proches, "
    "comme par exemple 'identité', 'date', 'localisation', 'typologie', 'culture', etc.\n\n"
    f"Liste des propriétés : {', '.join(proprietes_uniques)}\n\n"
    "Retourne une liste de catégories, chacune accompagnée des propriétés qui s’y rattachent."
)

# 🔍 Appel à l’API
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Tu aides à classer des colonnes de données culturelles par grandes familles sémantiques."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.2
)

# 💾 Résultat brut
reponse_texte = response.choices[0].message.content

# Sauvegarde
with open("CartoDataMC/analyse_semantique_resultat.txt", "w", encoding="utf-8") as f:
    f.write(reponse_texte)

print("✅ Analyse sémantique enregistrée dans CartoDataMC/analyse_semantique_resultat.txt")
