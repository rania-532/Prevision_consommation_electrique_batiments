# Compte rendu — TP4 : MaintAI devient un package Python

| Information | Valeur |
|---|---|
| Groupe | G2 |
| Membres | AYMAN MAHBOUB |
| Date | 09/11/2026 |
| Projet | MaintAI |

## 1. Mise en place

### Installation des dépendances

L'environnement virtuel `.venv` a été créé, puis les dépendances de
`requirements.txt` ont été installées avec succès.

### Tests avant l'installation du package

Après l'installation des dépendances, les tests de packaging échouent car le
package n'est pas encore installé :

```text
============================== 25 passed, 2 failed ==============================
```

Les deux tests qui échouent sont dans `tests/test_package.py` :

| Test | Cause |
|---|---|
| `test_installed_version_matches_the_code` | Le package `maintai` n'est pas encore installé. |
| `test_command_is_declared` | La commande `maintai-predict` n'est pas encore déclarée. |

## 2. Sprint 1 — `pyproject.toml` et installation éditable

### Configuration ajoutée

```toml
[project]
dependencies = [
    "numpy>=2.4",
    "pandas>=3.0",
    "scikit-learn>=1.8",
    "joblib>=1.5",
    "httpx>=0.28",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

### Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

La section `dependencies` contient uniquement les bibliothèques nécessaires au
fonctionnement principal du package.

- `pytest` est un outil de test et de développement ;
- `fastapi` et `uvicorn` sont nécessaires uniquement pour l'API.

Ils sont donc déclarés dans les dépendances optionnelles `dev` et `api`.

### Installation

Commande exécutée :

```powershell
pip install -e .
```

Sortie de `pip show maintai` :

```text
Name: maintai
Version: 0.2.0
Summary: Prédiction de panne à partir de relevés de capteurs
Home-page:
```

### Validation

```text
============================== 27 passed, 1 warning in 30.89s ==============================
```

La commande déclarée fonctionne :

```text
maintai 0.2.0
```

### Installation éditable

Depuis un autre dossier, la commande suivante :

```powershell
python -c "import maintai; print(maintai.__file__)"
```

affiche un chemin vers le dossier source `maintai` du projet. Avec
`pip install -e .`, Python utilise donc directement les fichiers sources
locaux.

Si le modèle n'est pas indiqué, `maintai-predict 72 6 85 15000` affiche :

```text
Modèle introuvable : ...\models\model.joblib
Entraînez-le (python -m maintai.train) ou indiquez son dossier dans MAINTAI_MODELS_DIR.
```

Avec `MAINTAI_MODELS_DIR` configuré vers le dossier `models`, la commande
affiche la probabilité de panne.

### Modification sans réinstallation

Après une modification de `maintai/cli.py`, le changement est visible sans
réinstaller le package. La raison est que `pip install -e .` crée une
installation éditable qui pointe vers les sources locales.

## 3. Sprint 2 — Construction et installation du wheel

### Construction de la distribution

Commande exécutée :

```powershell
python -m build
```

Contenu du dossier `dist` :

```text
maintai-0.2.0-py3-none-any.whl  11614
maintai-0.2.0.tar.gz             12222
```

### Contenu du wheel

Commande utilisée :

```powershell
tar -tf dist\maintai-0.2.0-py3-none-any.whl
```

Résultat :

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

Le modèle, les tests et le dossier `ui/` ne sont pas inclus. La configuration
Setuptools inclut uniquement les packages Python correspondant à `maintai*`.

### Installation dans un environnement neuf

| Situation | Résultat |
|---|---|
| Sans `MAINTAI_MODELS_DIR` | Erreur `Modèle introuvable`. |
| Avec `MAINTAI_MODELS_DIR` vers `models` | La prédiction est affichée. |
| Après `pip install scikit-learn==1.8.0` | Le modèle est chargé avec la version attendue. |

L'avertissement `InconsistentVersionWarning` apparaît lorsque le modèle est
chargé avec une version de scikit-learn différente de celle utilisée pendant
l'entraînement. Le fichier `models/model_info.json` indique :

```json
"sklearn_version": "1.8.0"
```

## 4. Questions de compréhension

### 4.1 Différence entre `requirements.txt` et `dependencies`

`requirements.txt` décrit l'environnement de travail avec des versions
exactement fixées, par exemple `numpy==2.4.4`.

La section `dependencies` de `pyproject.toml` décrit les dépendances runtime
du package avec des versions minimales, par exemple `numpy>=2.4`.

### 4.2 Différence entre installation éditable et wheel

```powershell
pip install -e .
```

Installe le package en mode éditable et utilise directement les fichiers
sources locaux. Les modifications sont donc immédiatement visibles.

```powershell
pip install dist\maintai-0.2.0-py3-none-any.whl
```

Installe une distribution construite et indépendante du dossier source.

### 4.3 Point d'entrée

Un point d'entrée associe une commande du terminal à une fonction Python :

```toml
[project.scripts]
maintai-predict = "maintai.cli:main"
```

Pip crée le lanceur dans le dossier `Scripts` de l'environnement virtuel :

```text
.venv\Scripts\maintai-predict.exe
```

## 5. Rendu Git

| Élément | État |
|---|---|
| Lien de la pull request | Non fourni |
| Tag `tp4` sur GitHub | Non vérifié |
| `dist/`, `build/`, `maintai.egg-info/` dans Git | Non vérifié |

Ces dossiers sont toutefois exclus par le fichier `.gitignore`.

## 6. Conclusion et points à retenir

Le projet MaintAI peut maintenant être installé comme un package Python. La
commande `maintai-predict` est disponible après installation, une distribution
wheel peut être construite et le code peut être utilisé depuis un autre
dossier.

Le modèle n'est volontairement pas inclus dans le wheel. Il faut donc fournir
son emplacement avec la variable d'environnement `MAINTAI_MODELS_DIR`. Il faut
également utiliser la même version de scikit-learn que celle indiquée dans
`models/model_info.json`.
