# -*- coding: utf-8 -*-
import pandas as pd
import os
import io
from mistralai import Mistral
from UsineSchema.config import OUTPUT, RESOURCE_contexte

# Charger prompt et contexte
with open("UsineSchema/tmp/prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

with open("UsineSchema/tmp/context.txt", "r", encoding="utf-8") as f:
    rows_context = f.read()

# Charger fichier de base
df = pd.read_csv(RESOURCE_contexte, sep=",")

# Client Mistral
client = Mistral(api_key=os.getenv("GithubMC"))

# Appel API
response = client.chat.complete(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": prompt + "\n\n" + rows_context}]
)

csv_result = response.choices[0].message.content or ""
lines = [line.strip("` ") for line in csv_result.splitlines() if ";" in line]
csv_cleaned = "\n".join(lines)

if not csv_cleaned.strip():
    raise ValueError("❌ Aucun contenu CSV valide généré par Mistral.")

df_defs = pd.read_csv(io.StringIO(csv_cleaned), sep=";")

if "definition" not in df_defs.columns:
    raise ValueError("❌ La sortie du modèle ne contient pas de colonne 'definition'.")

df_merged = df.merge(df_defs, left_on="column_name", right_on="property_name", how="left")
df_merged = df_merged.drop(columns=["property_name"], errors="ignore")

# Ajouter la provenance du LLM
df_merged["llm_origin"] = "mistral-large-latest"

# Export
os.makedirs("UsineSchema", exist_ok=True)
output_file = OUTPUT.replace(".csv", "_mistral.csv")
df_merged.to_csv(output_file, index=False, encoding="utf-8")

print(f"✅ Fichier enrichi (Mistral) exporté dans {output_file} ({len(df_merged)} propriétés)")
