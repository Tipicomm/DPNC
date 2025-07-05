import pandas as pd
import requests
import yaml
import ast  # pour décoder les listes JSON (tags)
import os

# 📥 Charger le fichier fusionné
input_path = "CartoDataMC/cartographie_ressources_datasets.csv"
df_csv = pd.read_csv(input_path, sep=";").head(200)

# 📦 Stocker les résultats
rows = []

for _, row in df_csv.iterrows():
    resource_id = row["id.ressource"]
    dataset_id = row["id.dataset"]
    dataset_title = row.get("title.dataset", "")
    dataset_description = row.get("description.dataset", "")

    # 🏷️ Extraction et nettoyage des tags
    tags_raw = row.get("tags.dataset", "")
    if isinstance(tags_raw, str):
        try:
            tags_list = [
                tag["name"]
                for tag in ast.literal_eval(tags_raw)
                if isinstance(tag, dict) and "name" in tag
            ]
            dataset_tags = ", ".join(tags_list)
        except Exception:
            dataset_tags = ""
    else:
        dataset_tags = ""

    # 🔍 Appel à l’API Swagger
    url = f"https://tabular-api.data.gouv.fr/api/resources/{resource_id}/swagger/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            try:
                data = yaml.safe_load(response.text)
                props = data.get("components", {}).get("schemas", {}).get("Resource", {}).get("properties", {})

                if props:
                    for prop_name, prop_info in props.items():
                        rows.append({
                            "resource_id": resource_id,
                            "dataset_id": dataset_id,
                            "dataset_title": dataset_title,
                            "description": dataset_description,
                            "tags": dataset_tags,
                            "property_name": prop_name,
                            "property_type": prop_info.get("type", "unknown")
                        })
                else:
                    rows.append({
                        "resource_id": resource_id,
                        "dataset_id": dataset_id,
                        "dataset_title": dataset_title,
                        "description": dataset_description,
                        "tags": dataset_tags,
                        "property_name": "⚠️ Aucune colonne trouvée",
                        "property_type": ""
                    })
            except yaml.YAMLError as e:
                rows.append({
                    "resource_id": resource_id,
                    "dataset_id": dataset_id,
                    "dataset_title": dataset_title,
                    "description": dataset_description,
                    "tags": dataset_tags,
                    "property_name": f"❌ Erreur YAML : {str(e)}",
                    "property_type": ""
                })
        else:
            rows.append({
                "resource_id": resource_id,
                "dataset_id": dataset_id,
                "dataset_title": dataset_title,
                "description": dataset_description,
                "tags": dataset_tags,
                "property_name": f"❌ HTTP {response.status_code}",
                "property_type": ""
            })
    except Exception as e:
        rows.append({
            "resource_id": resource_id,
            "dataset_id": dataset_id,
            "dataset_title": dataset_title,
            "description": dataset_description,
            "tags": dataset_tags,
            "property_name": f"❌ Exception : {str(e)}",
            "property_type": ""
        })

# 💾 Sauvegarde du résultat
df_properties = pd.DataFrame(rows)
output_path = "CartoDataMC/Cartographie_Culture_properties.csv"
df_properties.to_csv(output_path, index=False)

print(f"✅ Propriétés extraites avec succès dans {output_path}")
