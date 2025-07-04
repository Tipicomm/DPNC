## 📝 README.md — Automatisation de `dataAutomation.py`

### 🌟 Objectif

Ce dépôt exécute automatiquement chaque jour un script Python (`dataAutomation.py`) qui :

* Télécharge une ressource open data depuis data.gouv.fr
* Filtre les ressources au format CSV
* Extrait des colonnes utiles
* Génère un fichier `ressources_csv_culture.csv` dans le dossier `/data/`
* Commit et pousse ce fichier dans le dépôt

---

### ⚙️ Fonctionnement

L'automatisation repose sur **GitHub Actions**, via le fichier :

```bash
.github/workflows/automation.yml
```

Ce workflow :

* S’exécute tous les jours à **7h UTC**
* Lance le script Python avec les dépendances `pandas` et `requests`
* Enregistre le fichier dans `data/`
* Le versionne automatiquement via un commit signé “Bot Culture Data”

---

### 🔁 Planification

Déclenchement quotidien via :

```yaml
on:
  schedule:
    - cron: '0 7 * * *'  # chaque jour à 7h UTC
  workflow_dispatch:  # exécution manuelle possible
```

---

### 📁 Structure du projet

```
DPNC/
├── data/
│   └── ressources_csv_culture.csv  ← fichier mis à jour automatiquement
├── dataAutomation.py               ← script Python
└── .github/
    └── workflows/
        └── automation.yml          ← GitHub Action
```

---

### 🔐 Sécurité

Les push automatiques utilisent le **GITHUB\_TOKEN** sécurisé fourni par GitHub :

* Pas d’exposition de clés personnelles
* Permissions limitées au dépôt
* Commits identifiés par :

  ```git
  Author: Bot Culture Data <donnees@culture.gouv.fr>
  ```

---

### ✅ Pré-requis

* Dossier `/data/` existant (avec un fichier `.keep` initial si vide)
* `dataAutomation.py` doit écrire le fichier dans `data/ressources_csv_culture.csv`
* Permissions “Read and write” activées dans `Settings → Actions → General`

---

### 🧲 Tests et débogage

Tu peux lancer le workflow manuellement :

1. Aller dans l’onglet **Actions**
2. Sélectionner `Exécution planifiée de dataAutomation.py`
3. Cliquer sur **“Run workflow”**
