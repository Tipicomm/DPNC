## Convention de comparaison entre environnements (production / démo)

Lors de la comparaison des sauvegardes DataGouv, on applique la convention suivante :

| Variable | Environnement | Rôle logique | Recommandation |
|-----------|----------------|---------------|----------------|
| **X = prod / www** | Production : [`https://data.gouv.fr`](https://data.gouv.fr) | Référence officielle, source de vérité
| **Y = demo** | Démonstration : [`https://demo.data.gouv.fr`](https://demo.data.gouv.fr) | Environnement de test / comparaison

> **Principe :**  
> La production (X) est la base de référence, la démo (Y) sert à vérifier les différences éventuelles avant publication.  
> Les fichiers et colonnes suivent donc l’ordre : `X → Y` (ex. `title_prod`, `title_demo`).



