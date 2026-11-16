# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

 **Membres :*Rania BIKIKRE* …  ·  **Date :*11/16/2026* …



## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
========= 5 failed, 27 passed, 2 warnings in 24.23s ==========
```

Quels tests échouent, et pourquoi ?

================== short test summary info ===================
FAILED tests/test_tracking.py::test_training_creates_a_run - AssertionError: aucun run MLflow : log_run n'a rien enregi...
FAILED tests/test_tracking.py::test_run_records_metrics - AssertionError: aucun run MLflow : log_run n'a rien enregi...
FAILED tests/test_tracking.py::test_run_records_data_version - AssertionError: aucun run MLflow : log_run n'a rien enregi...
FAILED tests/test_tracking.py::test_run_stores_the_model - AssertionError: aucun run MLflow : log_run n'a rien enregi...
FAILED tests/test_tracking.py::test_options_change_the_run - AssertionError: aucun run MLflow : log_run n'a rien enregi...
========= 5 failed, 27 passed, 2 warnings in 24.23s ==========


La fonction log_run() n'enregistre pas encore les entraînements dans MLflow. Aucun run n'est créé, donc les paramètres, les métriques, la version des données et le modèle ne sont pas enregistrés.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avant : le package maintai pointait vers le code source du TP4, installé précédemment dans l'environnement virtuel.
Après : il pointe vers le code source du TP5.

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
# 1. Choisir l'expérience
    mlflow.set_experiment(EXPERIMENT)

    # 2. Démarrer un run
    with mlflow.start_run() as run:

        # 3. Enregistrer les paramètres
        mlflow.log_params(params)

        # 4. Enregistrer la version des données
        mlflow.log_param("data_md5", file_md5(data_path))

        # 5. Enregistrer les métriques
        mlflow.log_metrics(metrics)

        # 6. Enregistrer le modèle
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES
        )

    # 7. Retourner l'identifiant du run
    return run.info.run_id
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
================================ 32 passed, 4 warnings in 38.05s =================================```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` |  0.75| 0.622|  0.904|         6d62ec4f9b58430d9a1f2785c7e2675c
| `python -m maintai.train --C 0.01` | 0.691| 0.653| 0.864 |         89a005a69bda4beb955532be45244417
| `python -m maintai.train --threshold 0.2` | 0.838| 0.543| 0.864|       89a005a69bda4beb955532be45244417   
| `python -m maintai.train --model forest` | 0.728| 0.562| 0.864|          25dc19eccdbb48bea19440cb18ccb23c
| (votre essai) | | | |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)
Le run obtenu avec --threshold 0.2, car il présente le recall le plus élevé (0.838).

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

requirements.txt
133B
Path: file:///D:/S9/DevAppInT/Projet_Prediction_Elec/TPs/TP5/TP5_BIKIKRE_RANIA/mlruns/1/models/m-ae957c79859e45ef853c922d71f51f58/artifacts/requirements.txt
mlflow==3.18.0
numpy==2.4.4
pandas==3.0.2
psutil==7.2.2
pyarrow==26.0.1
pytest==9.1.1
scikit-learn==1.8.0
scipy==1.17.1
skops==0.16.0

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow enregistre les informations des runs dans une base de données locale appelée `mlflow.db`, située dans le dossier courant. 
Ces fichiers ne doivent pas être ajoutés à Git, car ils sont générés automatiquement lors des entraînements, peuvent être volumineux et ne correspondent pas au code source du projet.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

data_md5: 73e0b7cb3c6f795c70c3ddf970b99c15, identiques, ce qui confirme que MLflow et DVC font référence à la même version du fichier de données.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Le csv peut être volumineux, DVC le conserve dans son cache et dans un stockage externe afin d'éviter d'encombrer Git avec les différentes versions du fichier.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:                                                           
        changed outs:
                modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | 7bd4de09 | 73e0b7cb| 5 000|
| v2 | 57e5958c | 93fdeef2| 8 000| 

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

```
(.venv) PS D:\S9\DevAppInT\Projet_Prediction_Elec\TPs\TP5\TP5_BIKIKRE_RANIA> git checkout 7bd4de09 -- data/sensors.csv.dvc
(.venv) PS D:\S9\DevAppInT\Projet_Prediction_Elec\TPs\TP5\TP5_BIKIKRE_RANIA> dvc checkout
Building workspace index                              |2.00 [00:00, 56.8entry/s]
Comparing indexes                                     |3.00 [00:00,  701entry/s]
Applying changes                                      |1.00 [00:00,   289file/s]
M       data\sensors.csv
(.venv) PS D:\S9\DevAppInT\Projet_Prediction_Elec\TPs\TP5\TP5_BIKIKRE_RANIA> python -c "import pandas as pd; print(len(pd.read_csv('data/sensors.csv')))"
5000
(.venv) PS D:\S9\DevAppInT\Projet_Prediction_Elec\TPs\TP5\TP5_BIKIKRE_RANIA> git checkout HEAD -- data/sensors.csv.dvc
(.venv) PS D:\S9\DevAppInT\Projet_Prediction_Elec\TPs\TP5\TP5_BIKIKRE_RANIA> dvc checkout
Building workspace index                              |2.00 [00:00, 74.2entry/s]
Comparing indexes                                     |3.00 [00:00,    ?entry/s]
Applying changes                                      |1.00 [00:00,   224file/s]
M       data\sensors.csv
(.venv) PS D:\S9\DevAppInT\Projet_Prediction_Elec\TPs\TP5\TP5_BIKIKRE_RANIA> python -c "import pandas as pd; print(len(pd.read_csv('data/sensors.csv')))"
8000
```

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

DVC récupére le CSV depuis le stockage distant et le remet dans data/.
DVC permet de retrouver les données sans dépendre du cache local.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | 73e0b7cb| |4 000	 |0.750	|0.622
| v2 | |93fdeef2 | 6 400	| 0.741	|0.650

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Le modèle v2 présente une précision de 0,650 contre 0,622 pour la v1, mais son recall diminue légèrement de 0,750 à 0,741. Il n'est donc pas possible d'affirmer que le modèle v2 est globalement meilleur.
Le modèle v2 présente une précision de 0,650 contre 0,622 pour la v1, mais son recall diminue légèrement de 0,750 à 0,741. Il n'est donc pas possible d'affirmer que le modèle v2 est globalement meilleur.

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
  it versionne le code source, les fichiers de configuration et les fichiers de documentation.

DVC versionne les données et les fichiers volumineux, en conservant leurs références dans Git.

MLflow assure le suivi des expériences de Machine Learning : paramètres, métriques, versions des données utilisées et modèles entraînés.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
 L'option --local permet de configurer un stockage DVC uniquement sur la machine locale, sans partager son chemin dans le dépôt Git.

Pour que tout le groupe partage les mêmes données, il faudrait configurer un stockage distant accessible à tous les membres, par exemple un espace de stockage partagé ou un serveur distant, puis enregistrer sa configuration commune dans Git.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
  Le code : le package Python (wheel), construit à partir du dossier maintai/ et décrit par pyproject.toml.

Le modèle entraîné : fichier models/model.joblib.

Les versions exactes des dépendances : fichier requirements.txt.

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp5` existe sur GitHub : oui / non
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non

## 8. Ce qui reste flou

…
