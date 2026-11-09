# Compte rendu · TP4 : MaintAI devient un package Python

 **Membre :*BIKIKRE Rania* …  ·  **Date :*09/11/2026* …


---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
=============================== 2 failed, 25 passed, 1 warning in 6.74s ================================
```

Quels sont les deux tests qui échouent, et pourquoi ?

test_installed_version_matches_the_code : le package maintai n'est pas encore installé, donc Python ne trouve pas ses métadonnées de version.

test_command_is_declared : la commande maintai-predict n'est pas encore déclarée dans pyproject.toml, dans la section [project.scripts]

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```
dependencies = [
    "numpy>=2.4.4",
    "pandas>=3.0.2",
    "scikit-learn>=1.8.0",
    "joblib>=1.5.3",
    "httpx>=0.28.1",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

test et fastapi ne sont pas dans dependencies car ils ne sont pas nécessaires au fonctionnement du cœur du package MaintAI :
- pytest sert uniquement à exécuter les tests.
- fastapi sert à lancer l'API, qui est une fonctionnalité optionnelle.


Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: Package Python de prédiction des pannes d'équipements industriels à partir de données de capteurs
Home-page: 
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
==================================== 27 passed, 1 warning in 4.98s =====================================
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

python -c "import maintai; print(maintai.__file__)" affiche :
D:\S9\DevAppInT\Projet_Predict--> Même en étant placé dans le dossier temporaire (%TEMP%), la commande fonctionne. Python trouve le package maintai dans son dossier source d'origine grâce à l'installation en mode éditable (pip install -e .). Il n'est donc pas nécessaire de copier le package dans le dossier courant.


Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

```
(.venv) PS C:\Users\pc\AppData\Local\Temp> maintai-predict 72 6 85 15000
Panne : 95 % (ALERTE)
```
Le changement est visible sans réinstallation. Grâce à l'installation en mode éditable (pip install -e .), la commande utilise directement le code source du dossier TP4. Toute modification de cli.py est donc immédiatement prise en compte, sans avoir besoin de réinstaller le package.

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
(.venv) PS D:\S9\DevAppInT\Projet_Prediction_Elec\TPs\TP4\TP4_BIKIKRE_RANIA> dir dist


    Directory: 
    D:\S9\DevAppInT\Projet_Prediction_Elec\TPs\TP4\TP4_BIKIKRE_RANIA\dist


Mode                 LastWriteTime         Length Name                           
----                 -------------         ------ ----                           
-a----         11/9/2026   9:38 PM          11655 maintai-0.2.0-py3-none-any.whl 
-a----         11/9/2026   9:38 PM          12321 maintai-0.2.0.tar.gz           

```

Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`). Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?

```
Le wheel contient le code Python du package maintai/
Le modèle, les tests et l'interface ne sont pas présents car la configuration setuptools include = ["maintai*"] sélectionne uniquement les packages Python dont le nom commence par maintai.
```

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | odèle introuvable : C:\Users\pc\AppData\Local\Temp\essai\.venv\Lib\site-packages\models\model.joblib
Entraînez-le (python -m maintai.train) ou indiquez son dossier dans MAINTAI_MODELS_DIR.|
| avec `MAINTAI_MODELS_DIR` vers vos `models` |InconsistentVersionWarning: Trying to unpickle estimator StandardScaler from version 1.8.0 when using version 1.9.1. This might lead to breaking code or invalid results. Use at your own risk. |
| après `pip install scikit-learn==1.8.0` |Panne : 95 % (ALERTE) |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

L'avertissement InconsistentVersionWarning vient d'une différence entre la version de scikit-learn utilisée pour entraîner le modèle et celle installée dans le nouvel environnement.
Le modèle a été entraîné avec scikit-learn 1.8.0.
Le nouvel environnement avait installé scikit-learn 1.9.1, car pyproject.toml autorise toute version supérieure ou égale à 1.8.0.
a ligne qui permet de le comprendre dans models/model_info.json est :
"sklearn_version": "1.8.0"

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?
requirements.txt contient les versions exactes des dépendances (==) afin de reproduire le même environnement. La liste dependencies de pyproject.toml définit les dépendances nécessaires au fonctionnement du package, avec des versions minimales (>=). Elle permet donc une installation plus souple.
2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?
pip install -e . installe le package en mode éditable : il utilise directement les fichiers du dossier source. Les modifications du code sont donc prises en compte sans réinstallation. L'installation du fichier .whl installe une version construite du package dans l'environnement Python. Pour intégrer des modifications, il faut reconstruire le wheel puis le réinstaller.
3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?
   Un point d'entrée associe une commande utilisable dans le terminal à une fonction Python. Dans notre projet, maintai-predict = "maintai.cli:main" permet d'exécuter la fonction main() du module maintai.cli. Sous Windows, pip crée le fichier maintai-predict.exe dans le dossier Scripts de l'environnement Python actif, par exemple .venv\Scripts\maintai-predict.exe.

## 5. Le rendu Git

- Lien de la pull request : …
- Le tag `tp4` existe sur GitHub : oui / non
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ?  non

## 6. Ce qui reste flou

…
