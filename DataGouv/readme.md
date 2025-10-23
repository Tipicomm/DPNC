## Convention de comparaison entre environnements (production / démo)

Lors de la comparaison des sauvegardes DataGouv, on applique la convention suivante :

| Variable | Environnement | Rôle logique | 
|-----------|----------------|---------------|
| **X = prod / www** | Production : [`https://data.gouv.fr`](https://data.gouv.fr) | Référence officielle, source de vérité
| **Y = demo** | Démonstration : [`https://demo.data.gouv.fr`](https://demo.data.gouv.fr) | Environnement de test / comparaison

> **Principe :**  
> La production (X) est la base de référence, la démo (Y) sert à vérifier les différences éventuelles avant publication.  
> Les fichiers et colonnes suivent donc l’ordre : `X → Y` (ex. `title_prod`, `title_demo`).


### Ajouter un tag aux datasets 
 ─────────────────────────────────────────────────────────────
📘 Workflow : addTagAll

🎯 Objectif :
Ajouter le tag "culture" (ou "ministeredelaculture") à tous les jeux
de données d'une organisation DataGouv (ici le Ministère de la Culture).
#### ⚙️ Fonctionnement :
 * Ce workflow exécute le script Python :
       DataGouv/scripts/addTagAllDemo.py
 * Le script ajoute le tag à chaque dataset via l’API DataGouv.
 * Les tags existants sont conservés.

#### 🧠 Contrôle via paramètres (lors du lancement) :
   * environment : "demo" ou "www" (production)
   * update_mode : "True" (écriture) ou "False" (simulation)

#### 🗂️ Fichiers utilisés :
 * Script principal : DataGouv/scripts/addTagAllDemo.py
   - Fichier YAML : .github/workflows/add-tag-all-datasets-demo.yml
   - Fichier backup (optionnel) : DataGouv/scripts/backup_tags.json

#### 🏁 Sortie :
   * Liste des jeux de données modifiés ou déjà tagués.
   * Résumé du traitement dans les logs GitHub Actions.
   * Optionnellement, un fichier "backup_tags.json" est commité.
 ─────────────────────────────────────────────────────────────

