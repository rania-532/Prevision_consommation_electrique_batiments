# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** G2  ·  **Membres :** Imane Nadif  ·  **Date :** 09/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
=================== 2 failed, 25 passed, 1 warning in 7.18s ===================
```

Quels sont les deux tests qui échouent, et pourquoi ?

Les deux tests qui échouent sont dans `tests/test_package.py` :
- `test_installed_version_matches_the_code` : `maintai` n'est pas installé comme package, donc `importlib.metadata` ne trouve aucune métadonnée (`PackageNotFoundError`).
- `test_command_is_declared` : la commande `maintai-predict` n'est pas déclarée dans `[project.scripts]` et n'a pas été installée, donc elle est absente de la liste des commandes.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "pandas>=2.2",
    "numpy>=1.26",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "httpx>=0.27",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

Parce que `dependencies` ne contient que ce qu'il faut pour que le package fonctionne chez tout le monde (par exemple pour lancer `maintai-predict`). `pytest` ne sert qu'aux développeurs (groupe `dev`) et `fastapi` qu'à ceux qui lancent l'API (groupe `api`). Ils s'installent à la demande avec `pip install -e ".[api,dev]"`.

Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: Prédiction de panne de machines (MaintAI)
Home-page:
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
============================== 27 passed, 1 warning in 7.82s ===============================
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

Depuis `AppData\Local\Temp`, `maintai-predict 72 6 85 15000` affiche « Probabilité de panne : 95 % (ALERTE) ». La commande fonctionne hors du dossier du projet, car pip a créé un `.exe` dans `.venv\Scripts`.

`python -c "import maintai; print(maintai.__file__)"` affiche `C:\Users\andal\Downloads\TP4\maintai-starter-tp4\maintai\__init__.py`. Python trouve donc le code directement dans mon dossier `TP\TP4\maintai\` : l'installation éditable (`pip install -e .`) a posé dans `site-packages` un lien vers ce dossier, et non une copie du code.

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

J'ai remplacé « Probabilité de panne » par « Risque de panne » dans le `print` de `maintai/cli.py`. Après relance de `maintai-predict` sans réinstaller, le changement est visible immédiatement : « Risque de panne : 95 % (ALERTE) ». C'est parce que `pip install -e .` ne copie pas le code : il pose un lien vers mon dossier `TP\TP4\maintai\`. La commande exécute donc toujours le fichier que je modifie.

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
Mode                 LastWriteTime         Length Name                                      
----                 -------------         ------ ----                                      
-a----        09/11/2026     11:24          11627 maintai-0.2.0-py3-none-any.whl            
-a----        09/11/2026     11:23          12210 maintai-0.2.0.tar.gz   
```

Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`). Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?

```
maintai/__init__.py
maintai/cli.py
maintai/client.py
maintai/config.py
maintai/data.py
maintai/dataset.py
maintai/predict.py
maintai/train.py
maintai/api/__init__.py
maintai/api/main.py
maintai/api/schemas.py
maintai/api/security.py
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL
maintai-0.2.0.dist-info/entry_points.txt
maintai-0.2.0.dist-info/top_level.txt
maintai-0.2.0.dist-info/RECORD
```
Non : le modèle, les tests et `ui/` ne sont pas dans le wheel. Dans `pyproject.toml`, `[tool.setuptools.packages.find]` a `include = ["maintai*"]`, donc seul le dossier `maintai/` entre dans le package. `models/` contient des fichiers générés (`model.joblib`, `model_info.json`), pas du code, et `tests/` et `ui/` ne servent pas à utiliser la commande. Le wheel contient donc le code, mais pas le modèle : il faut le livrer à part et indiquer son dossier avec `MAINTAI_MODELS_DIR`.

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | `Modèle introuvable : C:\Users\andal\AppData\Local\Temp\essai\.venv\Lib\site-packages\models\model.joblib`, puis « Entraînez-le (python -m maintai.train) ou indiquez son dossier dans MAINTAI_MODELS_DIR. » |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | 3 `InconsistentVersionWarning` (StandardScaler, LogisticRegression, Pipeline : « Trying to unpickle estimator ... from version 1.8.0 when using version 1.9.1 »), puis `Probabilité de panne : 95 % (ALERTE)` |
| après `pip install scikit-learn==1.8.0` | Plus aucun avertissement : seulement `Probabilité de panne : 95 % (ALERTE)` |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

L'avertissement vient d'un décalage de version : le modèle (`model.joblib`) a été entraîné et écrit avec scikit-learn 1.8.0, mais pip a installé la version 1.9.1 avec le wheel, parce que `pyproject.toml` demande seulement `scikit-learn>=1.5` (« au moins »). Au chargement, scikit-learn voit que le modèle a été écrit par une autre version et prévient que les résultats peuvent être faux. La ligne `"sklearn_version": "1.8.0"` de `models/model_info.json` donne la version qui a écrit le modèle. Avec `pip install scikit-learn==1.8.0`, comme dans `requirements.txt` (« exactement »), l'avertissement disparaît.

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?
   `dependencies` dit « au moins » (`>=`) : elle liste ce dont le package a besoin pour fonctionner et reste souple, pour pouvoir s'installer à côté d'autres packages. `requirements.txt` dit « exactement » (`==`) : il fixe les versions de tout l'environnement, pour retrouver les mêmes conditions. C'est nécessaire pour un modèle, qui se relit avec la version qui l'a écrit : avec `scikit-learn>=1.5`, pip a installé la 1.9.1 et on a eu l'`InconsistentVersionWarning`, alors que le modèle avait été écrit avec la 1.8.0 (`==1.8.0`).
2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?
   `pip install -e .` (éditable) pose dans `site-packages` un lien vers mon dossier `TP\TP4\maintai\` : mes modifications sont visibles tout de suite (le message de `cli.py` a changé sans réinstaller). Il sert à développer. Le wheel est une copie du code, figée au moment du `python -m build` : modifier `TP\TP4` ne change plus rien dans l'environnement où il est installé, il faut reconstruire et réinstaller. Il sert à livrer à quelqu'un d'autre.
3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?
   Un point d'entrée associe un nom de commande à une fonction Python, au format `nom = "module:fonction"` (ici `maintai-predict = "maintai.cli:main"`). À l'installation, pip crée un petit fichier `.exe` qui appelle cette fonction. Il le place dans le dossier `Scripts` de l'environnement, donc `.venv\Scripts\maintai-predict.exe`, ce qui rend la commande disponible quand le `.venv` est activé. Il ne marche donc pas si le `.venv` n'est pas activé.
   …

## 5. Le rendu Git

- Lien de la pull request : …
- Le tag `tp4` existe sur GitHub : oui / non
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? oui / non

## 6. Ce qui reste flou

…
