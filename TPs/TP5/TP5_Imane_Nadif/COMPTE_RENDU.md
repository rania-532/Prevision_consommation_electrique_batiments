# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

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
-    # TODO TP5 sprint 1 : enregistrer le run dans MLflow
-    #   1. choisir l'expérience : mlflow.set_experiment(EXPERIMENT)
-    #   2. ouvrir un run :        with mlflow.start_run() as run:
-    #   3. dans le with :
-    #        - les paramètres :   mlflow.log_params(params)
-    #        - la version des données : un paramètre "data_md5", calculé par file_md5(data_path)
-    #        - les métriques :    mlflow.log_metrics(metrics)
-    #        - le modèle :        mlflow.sklearn.log_model(model, name="model", input_example=X_example,
-    #                                                      skops_trusted_types=TRUSTED_TYPES)
-    #   4. renvoyer l'identifiant : run.info.run_id
-    return ""
+    mlflow.set_experiment(EXPERIMENT)
+    with mlflow.start_run() as run:
+        mlflow.log_params(params)
+        mlflow.log_param("data_md5", file_md5(data_path))
+        mlflow.log_metrics(metrics)
+        mlflow.sklearn.log_model(
+            model,
+            name="model",
+            input_example=X_example,
+            skops_trusted_types=TRUSTED_TYPES,
+        )
+    return run.info.run_id
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

Le `requirements.txt` du modèle indique `scikit-learn==X.Y.Z`. MLflow enregistre, avec chaque modèle, les versions exactes des bibliothèques utilisées pour l'entraîner.

Au TP4, `models\model.joblib` ne contenait que le modèle, sans aucune trace des versions de bibliothèques. Un modèle sauvegardé avec une version de scikit-learn peut se charger mal, ou donner d'autres résultats, avec une autre version. Maintenant, on peut recréer l'environnement exact d'un run (`pip install -r requirements.txt`) et recharger le modèle dans les mêmes conditions que lors de l'entraînement.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow enregistre les runs dans le dossier `TP5`, là où on lance `python -m maintai.train` :
- `mlflow.db` : une base SQLite (un seul fichier) qui contient les paramètres, les métriques et les tags de chaque run ;
- `mlruns\` : un dossier qui contient les modèles enregistrés (`model.skops`, `requirements.txt`...).

Ces fichiers ne vont pas dans Git : le `.gitignore` de `TP5` les exclut. Ce sont des résultats locaux, qu'on peut régénérer en relançant les entraînements. Ils changent à chaque run, et Git garde chaque version de chaque fichier pour toujours : ils alourdiraient l'historique pour rien. Chaque membre du groupe a ses propres runs sur son PC.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
(collez ici)
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

…

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

…

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
(collez ici)
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | | | |
| v2 | | | |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

…

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

…

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | | | | |
| v2 | | | | |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

…

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   …
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   …
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   …

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp5` existe sur GitHub : oui / non
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? oui / non

## 8. Ce qui reste flou

…
