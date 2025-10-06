# -*- coding: utf-8 -*-
import pandas as pd
import openai
import os
import io
from UsineSchema.config import OUTPUT, RESOURCE_contexte

# Charger prompt et contexte
with open("UsineSchema/tmp/prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

with open("UsineSchema/tmp/context.txt", "r", encoding="utf-8") as f:
    rows_context = f.read()

# Charger fichier de base
df = pd.read_csv(RESOURCE_contexte, sep=",")

# Client OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Appel API
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt + "\n\n" + rows_context}],
    temperature=0.2,
    max_tokens=4000
)

csv_result = response.choices[0].message.content or ""
lines = [line.strip("` ") for line in csv_result.splitlines() if ";" in line]
csv_cleaned = "\n".join(lines)

df_defs = pd.read_csv(io.StringIO(csv_cleaned), sep=";")
df_merged = df.merge(df_defs, left_on="column_name", right_on="property_name", how="left")
df_merged = df_merged.drop(columns=["property_name"], errors="ignore")

os.makedirs("UsineSchema", exist_ok=True)
df_merged.to_csv(OUTPUT.replace(".csv", "_openai.csv"), index=False, encoding="utf-8")

print(f"✅ Fichier enrichi (OpenAI) exporté dans {OUTPUT.replace('.csv','_openai.csv')} ({len(df_merged)} propriétés)")
