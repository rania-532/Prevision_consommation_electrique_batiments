# Compte rendu — TP4 : MaintAI devient un package Python

**Groupe :** Groupe 4  
**Membres :** Farah Otarid, Rania Bikikre, Imane Nadif, Amine Erradha et Ayman Mahboub  
**Date :** 09/11/2026

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Après l'installation des dépendances, nous avons exécuté les tests avec :

```text
============================================= 27 passed, 1 warning in 7.85s =============================================
```

Les 27 tests ont réussi. Un avertissement de dépréciation provenant de Starlette indique que l'utilisation de `httpx` avec `starlette.testclient` est dépréciée et qu'il est recommandé d'installer `httpx2`.

**Quels sont les deux tests qui échouent, et pourquoi ?**

Dans notre dernière exécution, aucun test n'échoue : les 27 tests passent.

Il faut distinguer ce résultat de l'exécution initiale demandée dans l'énoncé. Les deux tests qui échouaient éventuellement au départ doivent être identifiés à partir de la première sortie de Pytest.

---

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

### Sections `dependencies` et `[project.scripts]`

```toml
dependencies = [
    "numpy>=1.26",
    "pandas>=2.2",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "httpx>=0.27"
]

[project.scripts]
maintai-predict = "maintai.cli:main"
maintai-ui = "streamlit.web.cli:main"
```

**Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?**

Les dépendances principales correspondent uniquement aux bibliothèques nécessaires au fonctionnement normal du package.

- `pytest` est utilisé pour exécuter les tests. Il appartient au groupe optionnel `dev`.
- `fastapi` est utilisé pour faire fonctionner l'API. Il appartient au groupe optionnel `api`.

Cette séparation permet d'éviter d'installer des bibliothèques inutiles aux utilisateurs qui souhaitent uniquement utiliser les fonctionnalités principales du package.

### Sortie de `pip show maintai`

```text
Name: maintai
Version: 0.2.0
Summary: Package de maintenance prédictive utilisant le machine learning pour détecter les risques de panne des équipements industriels.
Home-page:
```

Le package installé est en version `0.2.0`. La ligne `Editable project location` confirme que nous utilisons une installation éditable pointant vers le dossier du projet.

### Dernière ligne de `python -m pytest` à la fin du Sprint 1

```text
============================================= 27 passed, 1 warning in 7.85s =============================================
```

### Tester le package depuis un autre dossier

Les commandes utilisées sont :

```powershell
cd $env:TEMP
maintai-predict 72 6 85 15000
python -c "import maintai; print(maintai.__file__)"
```

**Résultat :** à compléter avec les sorties réelles des deux commandes.

Python retrouve le package grâce à son installation avec `pip install -e .`. Le chemin est enregistré dans l'environnement Python et permet d'importer `maintai` même depuis un autre dossier.

### Modifier le code sans réinstaller

Nous avons modifié le message affiché dans `maintai/cli.py`, puis relancé `maintai-predict`.

Le changement est visible sans réinstallation, car `pip install -e .` réalise une installation en mode éditable. Le package pointe directement vers les fichiers du projet source.

---

## 3. Sprint 2 : construire et installer le wheel

### Construction du package

Nous avons exécuté :

```powershell
python -m build
```

La construction s'est terminée avec succès :

```text
Successfully built maintai-0.2.0.tar.gz and maintai-0.2.0-py3-none-any.whl
```

Deux distributions ont donc été créées dans `dist/` :
- `maintai-0.2.0.tar.gz` : archive source.
- `maintai-0.2.0-py3-none-any.whl` : distribution au format wheel.

### Contenu du wheel

La commande utilisée est :

```powershell
tar -tf dist\maintai-0.2.0-py3-none-any.whl
```

Le wheel contient les modules Python du package :

```text
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

Le wheel contient le package `maintai`, ses sous-modules et les métadonnées nécessaires à son installation.

Le dossier `tests/`, le dossier `ui/` et les modèles entraînés ne sont pas inclus dans le wheel.

Cela s'explique par la configuration setuptools, qui inclut uniquement les packages correspondant au motif `maintai*`. Les tests servent à vérifier le projet et les autres ressources ne sont pas déclarées comme faisant partie du package.

### Installation dans un environnement neuf

| Étape | Ce qui s'affiche |
|---|---|
| Sans `MAINTAI_MODELS_DIR` | À compléter après le test |
| Avec `MAINTAI_MODELS_DIR` vers le dossier `models` | À compléter après le test |
| Après `pip install scikit-learn==1.8.0` | À compléter après le test |

### Comprendre `InconsistentVersionWarning`

Cet avertissement apparaît lorsque la version de scikit-learn utilisée pour charger un modèle est différente de celle utilisée pour l'entraîner.

La ligne à consulter dans `models/model_info.json` est :

```json
"sklearn_version": "..."
```

Elle permet de connaître la version de scikit-learn utilisée lors de l'entraînement et de la comparer avec la version installée dans l'environnement de test.

---

## 4. Questions de compréhension

### 1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?

`requirements.txt` contient une liste de dépendances destinée à installer l'environnement nécessaire au projet.

La section `dependencies` de `pyproject.toml` déclare les bibliothèques indispensables au fonctionnement du package. Elle permet à pip de les installer automatiquement lors de l'installation du package.

### 2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?

`pip install -e .` installe le package en mode éditable. Il pointe directement vers les fichiers sources. Les modifications sont donc visibles sans réinstaller le package.

L'installation du wheel utilise une version construite du package. Les modifications apportées au code source ne sont pas automatiquement prises en compte : il faut reconstruire et réinstaller le wheel.

### 3. Qu'est-ce qu'un point d'entrée (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?

Un point d'entrée permet de créer une commande exécutable qui appelle une fonction Python.

Dans notre projet :

```toml
[project.scripts]
maintai-predict = "maintai.cli:main"
```

La commande `maintai-predict` appelle la fonction `main()` du fichier `maintai/cli.py`.

Sous Windows, pip crée le fichier `maintai-predict.exe` dans le dossier `Scripts` de l'environnement Python utilisé, par exemple :

```text
.venv\Scripts\maintai-predict.exe
```

---

## 5. Le rendu Git

- **Lien de la Pull Request :** à compléter.
- **Le tag `tp4` existe sur GitHub :** à vérifier.
- **`git status` avant le commit :** à vérifier.

Les dossiers `dist/`, `build/` et `maintai.egg-info/` sont générés pendant la construction ou l'installation du package. Ils ne doivent généralement pas être versionnés.

Ils peuvent être ajoutés au `.gitignore` :

```gitignore
dist/
build/
*.egg-info/
```

---

## 6. Ce qui reste flou

Les points qui méritent encore d'être approfondis sont :

- La différence entre une installation éditable et une installation classique.
- La gestion des fichiers externes, comme les modèles entraînés, lors de la distribution d'un package.
- La compatibilité des modèles sauvegardés entre différentes versions de scikit-learn.
- La configuration des dépendances et des points d'entrée pour rendre un package facilement utilisable sur une autre machine.

Ce TP nous a permis de comprendre les étapes nécessaires pour transformer un projet Python en package installable et réutilisable, et de distinguer le code source, les dépendances et les fichiers générés lors de la distribution.