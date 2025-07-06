import openai
import pandas as pd
import time

# Clé API OpenAI depuis la variable d'environnement 
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Chargement de ton fichier CSV
df = pd.read_csv("cartographie_culture_properties_exemples.csv", sep=";")
df_unique = df[['dataset_title', 'description', 'property_name', 'exemple_1', 'exemple_2', 'exemple_3']].drop_duplicates('property_name')

# Prompt template
def build_prompt(row):
    return f"""
Tu es un expert en modélisation des données culturelles et en documentation des schémas de données.

Ta tâche est de proposer une définition claire et contextuelle d'une propriété issue d’un jeu de données publics dans le domaine culturel. Cette définition doit permettre de comprendre ce que désigne la propriété, à quoi elle correspond dans la réalité (structure, événement, œuvre, etc.), et en quoi les exemples illustrent son usage.

### Données à analyser :

- Nom de la propriété : {row['property_name']}
- Exemples de valeurs : {row['exemple_1']}, {row['exemple_2']}, {row['exemple_3']}
- Titre du jeu de données : {row['dataset_title']}
- Description du jeu de données : {row['description']}

### Consigne :

En t’appuyant uniquement sur ces éléments, rédige une définition de cette propriété, en précisant :
- Ce que la propriété représente
- Son lien avec une entité réelle ou conceptuelle
- Sa fonction ou son usage dans ce jeu de données

### Format attendu :

Définition : <phrase claire et autonome, 1 à 3 phrases maximum>
""".strip()

# Fonction d’appel à l’API OpenAI
def get_definition(prompt, model="gpt-4"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("Erreur :", e)
        return "Erreur"

# Application du traitement
definitions = []
for index, row in df_unique.iterrows():
    prompt = build_prompt(row)
    print(f"⏳ Traitement propriété : {row['property_name']}")
    definition = get_definition(prompt)
    definitions.append(definition)
    time.sleep(1.5)  # Respect du quota OpenAI

# Ajout des résultats
df_unique["définition"] = definitions

# Export CSV
df_unique.to_csv("proprietes_avec_definitions.csv", index=False)
print("✅ Fichier exporté avec définitions.")
