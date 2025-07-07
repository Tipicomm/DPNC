Cartographie des données - MetaMc
Le répertoire .github/workflows/ regroupe l’ensemble des pipelines d’automatisation utilisés pour la cartographie des jeux de données culturels. Ces workflows permettent de traiter, enrichir et structurer les données via des scripts Python, des appels à des LLMs ou des imports depuis des sources ouvertes.



| Fichier YAML                           | Description                                                                                                    |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `MetaMc_Analyse.yaml`                  | Analyse sémantique des propriétés à l’aide du métamodèle MetaMC. Utilise GPT pour produire un mapping enrichi. |
| `analyse_semantique.yaml`              | Traitement par lot de propriétés d’un CSV, avec génération de colonnes sémantiques standardisées.              |
| `CartoDataMC_exemples_proprietes.yaml` | Traitement d’un échantillon restreint de propriétés pour test ou démonstration.                                |
| `CartoDataMc.yaml`                     | Pipeline général d’orchestration pour les traitements sur le dépôt `CartoDataMC`.                              |
| `extraction_properties.yaml`           | Extraction des noms et types de propriétés à partir des jeux de données publiés.                               |
| `definition-llm.yml`                   | Génération de définitions compréhensibles à partir des noms de colonnes via modèle LLM.                        |
| `automation.yml`                       | Automatisation transversale : déclenchements planifiés, synchronisation, surveillance.                         |
| `importsDataGouv.yaml`                 | Import automatique de métadonnées depuis data.gouv.fr (catalogue DCAT, fichiers, titres, descriptions).        |
