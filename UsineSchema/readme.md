# Usine à schéma pour les ressources – ministère de la Culture

Générer des définitions pour chaque champ/propriété et créer les schémas à partir d’une ressource et d’un jeu de données disponible sur [data.gouv.fr](https://data.gouv.fr) (API dataset + API tabulaire).

## Fichiers clés

- config.py : identifiants dataset/ressource + chemins
- Ressource_Contexte_Etape1.py : extraction des colonnes + statistiques
- Add_Prompt_Definition_Etape2.py : génération du prompt et du contexte (commun)
- Add_Definition_OpenAI.py : génération des définitions via OpenAI
- Add_Definition_Mistral.py : génération des définitions via Mistral
