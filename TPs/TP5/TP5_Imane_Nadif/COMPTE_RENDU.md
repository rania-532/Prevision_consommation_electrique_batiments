# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :**G2  ·  **Membres :** IMANE NADIF  ·  **Date :** 16/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
================== 5 failed, 27 passed, 2 warnings in 17.36s ===================
```

Quels tests échouent, et pourquoi ?

Cinq tests de `tests/test_tracking.py` échouent (`5 failed, 27 passed`) :

- `test_training_creates_a_run`
- `test_run_records_metrics`
- `test_run_records_data_version`
- `test_run_stores_the_model`
- `test_options_change_the_run`

Tous échouent avec le même message : « aucun run MLflow : log_run n'a rien enregistré ». La fonction `log_run` de `maintai/tracking.py` n'est pas encore écrite : elle contient un TODO et ne crée aucun run MLflow (ni paramètres, ni `data_md5`, ni métriques, ni modèle). Les 27 tests du TP4 passent, car le code du TP4 n'a pas changé.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avant, l'environnement était celui du TP4 : `maintai` y était installé en mode éditable depuis le dossier du TP4, donc il pointait vers le code du TP4 (sans `tracking.py`). Après `pip install -e .` lancé dans le dossier du TP5, `maintai` pointe vers le dossier du TP5, donc vers le nouveau code (version 0.3.0, avec `maintai/tracking.py`). C'est ce qui permet à `python -m maintai.train` et à pytest d'utiliser le code du TP5.

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
 def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
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

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
============================== 32 passed, 6 warnings in 38.75s ==============================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.75| 0.622|0.904 |
| `python -m maintai.train --C 0.01` |0.691 |0.653	| 0.908|
| `python -m maintai.train --threshold 0.2` |0.838	|0.543|	0.882|
| `python -m maintai.train --model forest` |  0.728 | 0.562 | 0.886 |
| (votre essai) | | | |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Je choisirais le run `--threshold 0.2` (run `06ae2b65adf044e4970bdb6008cec178`) : c'est celui qui a le meilleur recall (0.838). Comme une panne manquée coûte plus cher qu'une fausse alerte, le recall est la métrique prioritaire. En échange, la precision baisse (0.543, contre 0.622 avec le réglage par défaut) : il y aura plus de fausses alertes. La forêt aléatoire n'est pas meilleure ici : son recall (0.728) est inférieur à celui du seuil 0.2 et même à celui du réglage par défaut (0.75), et sa precision (0.562) est plus basse aussi.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

Le `requirements.txt` du modèle indique `scikit-learn==1.8.0`, avec aussi `numpy==2.4.4`, `pandas==3.0.2`, `skops==0.16.0` et `mlflow==3.18.0`. MLflow enregistre, avec chaque modèle, les versions exactes des bibliothèques utilisées pour l'entraîner.

Au TP4, `models\model.joblib` ne contenait que le modèle, sans aucune trace des versions de bibliothèques. Un modèle sauvegardé avec une version de scikit-learn peut se charger mal, ou donner d'autres résultats, avec une autre version. Maintenant, on peut recréer l'environnement exact d'un run (`pip install -r requirements.txt`) et recharger le modèle dans les mêmes conditions que lors de l'entraînement.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow enregistre les runs dans le dossier `TP5`, là où on lance `python -m maintai.train` :
- `mlflow.db` : une base SQLite (un seul fichier) qui contient les paramètres, les métriques et les tags de chaque run ;
- `mlruns\` : un dossier qui contient les modèles enregistrés (`model.skops`, `requirements.txt`...).

Ces fichiers ne vont pas dans Git : le `.gitignore` de `TP5` les exclut. Ce sont des résultats locaux, qu'on peut régénérer en relançant les entraînements. Ils changent à chaque run, et Git garde chaque version de chaque fichier pour toujours : ils alourdiraient l'historique pour rien. Chaque membre du groupe a ses propres runs sur son PC.

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

Les deux valeurs sont identiques : `73e0b7cb3c6f795c70c3ddf970b99c15`. Le `md5` du fichier `.dvc` (calculé par DVC) et le paramètre `data_md5` du run (calculé par `file_md5` dans `tracking.py`) sont la même empreinte du même fichier `sensors.csv`. C'est ce qui relie un run MLflow à une version précise des données : à partir du `data_md5` d'un run, on retrouve le commit Git du reçu `.dvc` correspondant, puis on récupère les données avec `dvc checkout`.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Un fichier de données peut être gros (ici 127 Ko, mais souvent 100 Mo ou plus), et Git le gère mal : il garde chaque version pour toujours, ce qui alourdit le dépôt. `data/sensors.csv` est donc ignoré par Git (`.gitignore`) et stocké par DVC, dans un cache puis dans le stockage. Dans Git, on ne met que le reçu `sensors.csv.dvc` : quelques lignes (le `md5` et la taille du fichier), versionnées comme du code. Git choisit ainsi la version du reçu, et DVC ramène le fichier qui lui correspond.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:
        changed outs:
                modified:           data\sensors.csv
```
DVC compare le `md5` du fichier actuel à celui du reçu `sensors.csv.dvc` : ils diffèrent, donc le fichier est signalé comme modifié. Git ne voit rien, car `sensors.csv` est ignoré : seul DVC détecte ce changement.

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | `a5ba1ee` | `73e0b7cb` | 5000 |
| v2 | `9486912` | `93fdeef2` | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après `git checkout a5ba1ee -- data/sensors.csv.dvc` et `dvc checkout`, `data/sensors.csv` contient 5000 lignes : Git a remis l'ancien reçu (v1) et DVC a ramené le fichier correspondant depuis le cache. Pour revenir à la v2, `git checkout HEAD -- data/sensors.csv.dvc` puis `dvc checkout` redonnent 8000 lignes.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

DVC récupère le fichier depuis le stockage : `dvc pull` affiche `1 file fetched and 1 file added`. Il relit le reçu `sensors.csv.dvc` (le `md5` de la v2), retrouve le fichier correspondant dans le stockage (`C:\Users\andal\dvc-stockage`), le copie dans le cache `.dvc/cache`, puis le remet dans `data/`. `data/sensors.csv` est de nouveau là, avec 8000 lignes. C'est la situation d'un coéquipier qui clone le dépôt : il a les reçus via Git, et récupère les données avec `dvc pull`.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | `73e0b7cb` | 4000 | 0.75 | 0.622 |
| v2 | `93fdeef2` | 6400 | 0.741 | 0.65 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non, on ne peut pas conclure. Avec les mêmes réglages, le run v2 a un recall un peu plus bas (0.741 contre 0.75) et une precision un peu plus haute (0.65 contre 0.622) : l'écart est faible et ne va pas dans un seul sens.

Il faut être prudent parce que les deux runs ne sont pas évalués sur le même test : le jeu de test de la v1 compte 1000 relevés, celui de la v2 en compte 1600, et ce ne sont pas les mêmes relevés (taux de panne de 13.6 % contre 12.8 %). Une différence de quelques points peut venir du hasard du découpage et de la taille du jeu de test, pas d'un meilleur modèle. Le `data_md5` permet justement de savoir que les données diffèrent, donc que la comparaison n'est pas « toutes choses égales par ailleurs ».

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?

- **Git** versionne le code (`maintai/`, `tests/`, `pyproject.toml`, `requirements.txt`) et, pour les données, seulement un petit reçu `.dvc` de quelques lignes.
- **DVC** versionne les fichiers de données (`sensors.csv`). Il les garde hors de Git, dans un cache puis dans un stockage, et ne met dans Git que le reçu (le `md5` et la taille du fichier).
- **MLflow** garde la trace de chaque entraînement (un « run ») : ses paramètres, l'empreinte des données (`data_md5`), ses métriques et le modèle, avec les versions exactes des bibliothèques (`requirements.txt`).

2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?

Le stockage est un dossier de mon PC (`C:\Users\andal\dvc-stockage`). Ce chemin n'a de sens que sur ma machine et ne doit pas aller dans Git : `--local` l'écrit dans `.dvc/config.local`, qui est ignoré par Git. Chaque personne déclare donc son propre stockage.

Pour que tout le groupe partage les mêmes données, il faudrait un stockage accessible à tous, déclaré dans la configuration versionnée (sans `--local`) : un serveur partagé, un stockage cloud (S3, Azure, Google Drive) ou un dossier réseau. Chacun ferait alors `dvc pull` pour récupérer les fichiers dont les reçus sont dans Git.

3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?

- **Le code** : dans Git (et dans le wheel construit au TP4).
- **Les données** : avec DVC. Le reçu `.dvc` est dans Git et le fichier est dans le stockage.
- **Le modèle** : avec MLflow. Il est enregistré dans un run, retrouvable par son identifiant.

Les versions exactes des bibliothèques sont aussi gardées par MLflow, dans le `requirements.txt` du modèle.

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp5` existe sur GitHub : oui 
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ?  non

## 8. Ce qui reste flou

…
