# Compte rendu TP5 — MLflow et DVC

| Élément | Valeur |
|---|---|
| Groupe | G2 |
| Membre | Mahboub Ayman |
| GitHub | aymanmahboub1@gmail.com |
| Dépôt | [rania-532/Prevision_consommation_electrique_batiments](https://github.com/rania-532/Prevision_consommation_electrique_batiments) |
| Branche | `feature/tp5-ayman-mahboub` |
| Dossier | `TPs/TP5/tp5_Ayman_Mahboub/` |
| Date | 16/11/2026 |
| Projet | MaintAI |

## 1. Mise en place

Les dépendances ont été installées avec :

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
```

L'installation éditable a créé le package `maintai==0.3.0` et la commande
`maintai-predict`.

### Tests

Les tests ciblés liés au TP5 passent :

```text
tests/test_tracking.py tests/test_client.py
8 passed
```

Les tests du package passent également :

```text
tests/test_package.py
2 passed
```

La suite complète est actuellement bloquée pendant la collecte par une
incohérence préexistante dans `tests/test_cli.py` :

```text
ModuleNotFoundError: No module named 'TP5'
```

Le test importe `TP5.models.cli`, alors que le projet contient le package
`maintai` et aucun package `TP5.models`.

Avant `pip install -e .`, les imports locaux fonctionnaient depuis le dossier
du projet, mais aucune métadonnée de distribution `maintai` n'était installée.
Après l'installation éditable, la distribution `maintai==0.3.0` et son script
`maintai-predict` sont disponibles dans l'environnement Python.

## 2. Sprint 1 — Suivi des entraînements avec MLflow

La fonction `log_run` de `maintai/tracking.py` réalise les opérations
suivantes :

```python
mlflow.set_experiment(EXPERIMENT)
with mlflow.start_run() as run:
    mlflow.log_params(params)
    mlflow.log_param("data_md5", file_md5(data_path))
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(
        model,
        name="model",
        input_example=X_example,
        skops_trusted_types=TRUSTED_TYPES,
    )
    return run.info.run_id
```

### Résultats obtenus

Les quatre entraînements ont été réalisés sur 8 000 relevés, avec 6 400
relevés d'entraînement et 1 600 relevés de test.

| Commande | Run ID | Recall | Precision | Accuracy |
|---|---|---:|---:|---:|
| `python -m maintai.train` | `25db2f38a79e4d68bdc677105f84309b` | 0.741 | 0.650 | 0.916 |
| `python -m maintai.train --C 0.01` | `a31aa4313a71491da6088bb4a44c2467` | 0.698 | 0.688 | 0.921 |
| `python -m maintai.train --threshold 0.2` | `be4a72e53fa74a57aad9a07eec856bf9` | **0.824** | 0.567 | 0.897 |
| `python -m maintai.train --model forest` | `e076afe85a1b49488db7ef8472a4fbab` | 0.722 | 0.609 | 0.905 |

### Choix recommandé

Pour MaintAI, le run recommandé est :

```text
Run : be4a72e53fa74a57aad9a07eec856bf9
Modèle : régression logistique, C=1.0
Seuil : 0.2
Recall : 0.824
Precision : 0.567
Accuracy : 0.897
```

Ce run est retenu car le rappel est le plus élevé. Dans ce projet, une panne
manquée coûte davantage qu'une fausse alerte ; le seuil de 0.2 est donc
préférable malgré une précision plus faible.

### Versionnement du modèle

Le modèle enregistré par MLflow indique `scikit-learn==1.8.0` dans ses
dépendances. Cela règle le problème du TP4 où le modèle pouvait être chargé
avec une version différente de scikit-learn et produire des incompatibilités.

Les runs sont enregistrés localement dans :

```text
mlflow.db
mlruns/
```

Ces fichiers ne doivent pas être versionnés dans Git : ils sont générés
localement, peuvent être volumineux et contiennent les artefacts et
l'historique d'expérimentation. Ils sont exclus par `.gitignore`.

## 3. Sprint 2 — Versionnement des données avec DVC

Dans l'environnement actuel, le projet n'est pas dans un dépôt Git et aucun
dépôt DVC n'a donc été initialisé :

```text
ERROR: you are not inside of a DVC repository
```

Le fichier `data/sensors.csv.dvc` n'est pas présent. Les étapes suivantes ne
peuvent donc pas être produites honnêtement dans cet environnement :

- `dvc add data/sensors.csv` ;
- `dvc status` après modification ;
- comparaison de deux commits Git ;
- `dvc checkout` et `dvc pull`.

La procédure attendue dans un dépôt Git est :

```powershell
git init
dvc init --subdir
dvc add data/sensors.csv
dvc status
```

Le fichier `data/sensors.csv` contient actuellement 8 000 relevés, plus la
ligne d'en-tête. Son empreinte MD5 est :

```text
93fdeef2cac1893c4f720c16457eea75
```

Cette même empreinte est enregistrée dans le dernier run MLflow sous le
paramètre `data_md5`.

DVC versionne le contenu lourd des données dans son cache ou son stockage
distant, tandis que Git versionne le petit fichier `.dvc` contenant la
référence et l'empreinte. Cela évite de placer directement les fichiers de
données volumineux dans Git.

## 4. Relation entre modèle et données

Le run retenu est lié aux données par :

| Run | `data_md5` | `n_train` | Recall | Precision |
|---|---|---:|---:|---:|
| `be4a72e53fa74a57aad9a07eec856bf9` | `93fdeef2` | 6400 | 0.824 | 0.567 |

On ne peut pas déclarer qu'un modèle est meilleur uniquement en comparant
deux métriques provenant de versions différentes des données. Il faut
comparer les modèles sur le même jeu de test, avec les mêmes métriques, le
même seuil et un protocole identique.

## 5. Décision d'architecture

La décision actuelle est documentée dans
[`docs/adr/000-modele.md`](docs/adr/000-modele.md) :

- modèle : régression logistique avec `StandardScaler` ;
- seuil retenu pour l'essai : `0.2` ;
- justification : maximiser le rappel lorsque les pannes manquées sont
  coûteuses.

Le fichier `docs/adr/004-choix-du-modele.md` n'existe pas encore. Le run de
référence pour une future ADR 004 est
`be4a72e53fa74a57aad9a07eec856bf9`, avec la donnée
`93fdeef2cac1893c4f720c16457eea75`.

## 6. Questions de compréhension

### 6.1 Différence entre Git, DVC et MLflow

- **Git** versionne le code, la configuration, la documentation et les petits
  fichiers texte.
- **DVC** versionne les données volumineuses et conserve leur historique via
  des fichiers `.dvc` suivis par Git.
- **MLflow** versionne les expériences de Machine Learning : paramètres,
  métriques, versions de données et artefacts de modèles.

### 6.2 Pourquoi utiliser un stockage DVC local ?

L'option `--local` conserve la configuration du stockage DVC uniquement dans la
machine courante. Elle évite de publier un chemin local propre à un poste dans
le dépôt. Pour partager les données avec tout le groupe, il faudrait utiliser
un stockage distant accessible à tous, par exemple un serveur S3, Azure Blob
Storage ou un partage réseau configuré pour chaque membre.

### 6.3 Les trois éléments nécessaires pour livrer un modèle

Il faut livrer :

1. le code de prétraitement et de prédiction ;
2. le modèle entraîné ;
3. les métadonnées et dépendances nécessaires pour le recharger.

Dans MaintAI :

- le code se trouve dans `maintai/` ;
- le modèle se trouve dans `models/model.joblib` ;
- les métadonnées se trouvent dans `models/model_info.json`,
  `models/metrics.json` et dans les artefacts MLflow ;
- les dépendances sont décrites dans `requirements.txt` et `pyproject.toml`.

## 7. État du rendu Git

- Dépôt GitHub : https://github.com/rania-532/Prevision_consommation_electrique_batiments
- Branche : `feature/tp5-ayman-mahboub`
- Dossier du rendu : `TPs/TP5/tp5_Ayman_Mahboub/`
- Auteur des commits : Ayman Mahboub `<aymanmahboub1@gmail.com>`
- Lien de pull request : https://github.com/rania-532/Prevision_consommation_electrique_batiments/pull/new/feature/tp5-ayman-mahboub
- Tag `tp5` : non créé.
- `.env` (clé API) : exclu du dépôt, seul `.env.example` est versionné.
- `mlflow.db` et `mlruns/` : générés localement et exclus par `.gitignore`.
- `models/` et `data/sensors.csv` : générés localement et exclus par `.gitignore`.

## 8. Points restant à faire

Pour finaliser le rendu sur GitHub :

1. ~~placer le projet dans un dépôt Git~~ (fait, voir section 7) ;
2. initialiser DVC et ajouter `data/sensors.csv` ;
3. configurer un stockage DVC partagé ;
4. créer `docs/adr/004-choix-du-modele.md` si cette ADR est demandée ;
5. corriger l'import obsolète `TP5.models.cli` dans `tests/test_cli.py` ;
6. exécuter à nouveau la suite complète et joindre sa sortie au rendu.
