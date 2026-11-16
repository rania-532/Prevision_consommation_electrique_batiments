# Compte rendu TP5 — Suivre les entraînements et versionner les données

| Élément | Valeur |
|---|---|
| Groupe | G2 |
| Membre | Mahboub Ayman |
| GitHub | aymanmahboub1@gmail.com |
| Dépôt | [rania-532/Prevision_consommation_electrique_batiments](https://github.com/rania-532/Prevision_consommation_electrique_batiments) |
| Branche | `feature/tp5-ayman-mahboub` |
| Dossier | `TPs/TP5/tp5_Ayman_Mahboub/` |
| Date | 16/11/2026 |
| Projet | MaintAI 0.3.0 |
| Outils | MLflow 3.18.0, DVC 3.67.1, scikit-learn 1.8.0 |

## 1. Mise en place

```powershell
pip install -r requirements.txt
pip install -e .
python -m maintai.dataset      # 5000 relevés, taux de panne 13.6 %
python -m pytest
```

Le test `tests/test_cli.py` importait `TP5.models.cli`, un module qui
n'existe pas. L'import a été corrigé en `from maintai.cli import main`.

Résultat final :

```text
32 passed, 3 warnings in 39.26s
```

## 2. MLOps : pourquoi suivre le code, les données et le modèle

Le DevOps ne suit qu'une chose qui change : le code. Le MLOps en suit trois :
le code, les données et le modèle.

**Une raison pour laquelle MaintAI peut devenir moins bon sans modifier son
code :** la dérive des données. Par exemple, si les machines sont remplacées
ou si les capteurs sont recalibrés, les températures et vibrations « normales »
changent. Le modèle, appris sur les anciennes mesures, déclenche alors trop ou
pas assez d'alertes, alors que le code n'a pas changé.

| Outil | Ce qu'il garde |
|---|---|
| Git | le code et le reçu `data/sensors.csv.dvc` (md5 + taille) |
| DVC | le fichier `data/sensors.csv` lui-même, dans le cache et le stockage |
| MLflow | chaque entraînement : paramètres, `data_md5`, métriques, modèle et `requirements.txt` |

## 3. Sprint 1 — Enregistrer chaque entraînement (MLflow)

`log_run` dans `maintai/tracking.py` :

```python
mlflow.set_experiment(EXPERIMENT)
with mlflow.start_run() as run:
    mlflow.log_params(params)
    mlflow.log_param("data_md5", file_md5(data_path))
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(model, name="model", input_example=X_example,
                             skops_trusted_types=TRUSTED_TYPES)
return run.info.run_id
```

### Les quatre entraînements (données v1 : 5000 relevés, 4000 train / 1000 test)

| Entraînement | Run MLflow | recall | precision | accuracy |
|---|---|---:|---:|---:|
| `python -m maintai.train` | `f7b612783c6e4075970cc6724380ebf3` | 0.750 | 0.622 | 0.904 |
| `--C 0.01` | `df99319979b74e618e50f4645688bc35` | 0.691 | 0.653 | 0.908 |
| `--threshold 0.2` | `38f29769b559474db7e05d5d5ce6ebca` | **0.838** | 0.543 | 0.882 |
| `--model forest` | `589f44a69d6d4f559989036935cdae22` | 0.728 | 0.562 | 0.886 |

Les quatre runs ont le même `data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15`.
La baseline (toujours « pas de panne ») a un recall de 0.

**Quel run choisir pour MaintAI ? La forêt aléatoire est-elle meilleure ?**
Le run `--threshold 0.2`. Une panne manquée coûte plus cher qu'une fausse
alerte : on privilégie le recall, qui est le plus élevé (0.838). On accepte en
échange une précision plus faible (0.543), donc plus de fausses alertes.
La forêt aléatoire n'est pas meilleure : au même seuil 0.3, elle fait moins
bien que la régression logistique en recall (0.728 contre 0.750) et en
précision (0.562 contre 0.622), et elle est plus lourde et moins explicable.

**Version de scikit-learn dans le `requirements.txt` du modèle :**
`scikit-learn==1.8.0`. Cela règle le problème du TP4 : le fichier
`model.joblib` ne disait pas avec quelle version il avait été entraîné, et un
chargement avec une autre version de scikit-learn pouvait échouer ou donner
d'autres résultats. MLflow garde maintenant les versions exactes avec le
modèle.

## 4. Sprint 2 — Versionner les données (DVC)

```powershell
dvc init --subdir                     # dans TPs/TP5/tp5_Ayman_Mahboub
git commit -m "DVC : init"
dvc add data/sensors.csv
git add data/sensors.csv.dvc & git commit -m "Données v1"
mkdir %USERPROFILE%\dvc-stockage
dvc remote add --local -d stockage %USERPROFILE%\dvc-stockage
dvc push                              # 1 file pushed
```

Contenu de `data/sensors.csv.dvc` (v1) :

```yaml
outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv
```

**md5 du reçu comparé au `data_md5` des runs :** les deux valeurs sont
identiques (`73e0b7cb…`). `file_md5()` calcule la même empreinte que DVC : un
run MLflow est donc relié à une version précise des données.

**Pourquoi `data/sensors.csv` ne va pas dans Git, mais `data/sensors.csv.dvc`
oui ?** Un fichier de données peut peser des centaines de Mo et Git garde
chaque version pour toujours, ce qui alourdit le dépôt. DVC stocke le fichier
dans son cache et dans le stockage partagé, et Git ne garde que le reçu de
quelques lignes (md5 et taille) qui suffit à retrouver le bon fichier.

### Une deuxième version, et retour

```powershell
python -m maintai.dataset --n 8000 --seed 7
dvc status            # changed outs: modified: data\sensors.csv
dvc add data/sensors.csv
git add data/sensors.csv.dvc & git commit -m "Données v2"
dvc push              # 1 file pushed
python -m maintai.train   # Run MLflow : 3d96fcda9a2a4bf78f9ea848a28e969c
```

| Version | Commit (git log) | md5 (8 caractères) | Lignes |
|---|---|---|---:|
| v1 | `0d423bf` | `73e0b7cb` | 5000 |
| v2 | `bb2e776` | `93fdeef2` | 8000 |

- Retour à la v1 : `git checkout 0d423bf -- data/sensors.csv.dvc` puis
  `dvc checkout` → **5000 lignes**. `git status` montre le `.dvc` modifié
  (l'ancien reçu) : il n'a pas été commité.
- Retour à la v2 : `git checkout HEAD -- data/sensors.csv.dvc` puis
  `dvc checkout` → **8000 lignes**.
- Coéquipier sans les données : suppression de `data/sensors.csv` et de
  `.dvc/cache`, puis `dvc pull` → `1 file fetched and 1 file added`. Le fichier
  est récupéré depuis le stockage et on retrouve les 8000 lignes de la v2.

## 5. D'un modèle à ses données

| Run | Données | n_train | recall | precision | accuracy |
|---|---|---:|---:|---:|---:|
| `f7b612783c6e4075970cc6724380ebf3` | v1 `73e0b7cb` | 4000 | 0.750 | 0.622 | 0.904 |
| `3d96fcda9a2a4bf78f9ea848a28e969c` | v2 `93fdeef2` | 6400 | 0.741 | 0.650 | 0.916 |

**Le run sur la v2 a-t-il un meilleur recall que le run sur la v1, avec les
mêmes réglages ? Peut-on conclure que le modèle v2 est meilleur ?**
Non : le recall est légèrement plus bas (0.741 contre 0.750), alors que la
précision et l'accuracy sont un peu plus hautes. Et on ne peut de toute façon
rien conclure : les deux modèles ne sont pas évalués sur le même jeu de test
(1000 relevés de la v1 contre 1600 de la v2, générés avec une autre graine).
Les écarts observés peuvent venir des données de test plutôt que du modèle.
Pour comparer, il faudrait évaluer les deux modèles sur un même jeu de test.

**Retrouver les données d'un run :** lire `data_md5` dans MLflow, trouver le
commit dont `data/sensors.csv.dvc` porte ce md5
(`git log --oneline -- data/sensors.csv.dvc`), puis
`git checkout <commit> -- data/sensors.csv.dvc` et `dvc checkout` (ou
`dvc pull` sur un autre PC).

| Livrer un modèle | Où c'est maintenant |
|---|---|
| le code | Git (et le wheel du TP4) |
| les données | DVC : le reçu dans Git, le fichier dans le stockage |
| le modèle | MLflow : un run, son identifiant |
| les versions exactes | MLflow : le `requirements.txt` du modèle |

## 5 bis. Grid search sur 25 cas

Pour vérifier le choix du seuil et de C, une recherche sur grille a été faite
avec `maintai/grid_search.py` (`python -m maintai.grid_search`) : régression
logistique, 5 valeurs de C × 5 seuils = **25 runs MLflow**, tous sur les
données v2 (`data_md5 = 93fdeef2cac1893c4f720c16457eea75`, 8000 relevés,
6400 train / 1600 test).

| C | seuil | recall | precision | accuracy | run |
|---:|---:|---:|---:|---:|---|
| 0.01 | 0.1 | 0.966 | 0.384 | 0.797 | `57a084710c3b4f83a61139a4bad9f54c` |
| 0.01 | 0.2 | 0.829 | 0.547 | 0.890 | `f372c7b06634435ba82d2bc405b838db` |
| 0.01 | 0.3 | 0.698 | 0.688 | 0.921 | `e3ab6be514474f9b9a9dd30f231f97c5` |
| 0.01 | 0.4 | 0.571 | 0.780 | 0.924 | `9d66467da91543db854a7dd12c54bbaf` |
| 0.01 | 0.5 | 0.463 | 0.833 | 0.919 | `372355340ee34d5cb6bfe652d9d974eb` |
| 0.1 | 0.1 | 0.922 | 0.445 | 0.843 | `66fa8cfb03df499fb9bbf546a2ebc852` |
| 0.1 | 0.2 | 0.829 | 0.559 | 0.894 | `cd665c5721fe481d80d82070d100628a` |
| 0.1 | 0.3 | 0.732 | 0.652 | 0.916 | `86a0094e6ef041498a61900fc7a6bba1` |
| 0.1 | 0.4 | 0.654 | 0.720 | 0.923 | `f2cc28b7fe6f491ea785274f31d365ef` |
| 0.1 | 0.5 | 0.566 | 0.784 | 0.924 | `9ea1146f28604297bdc06c3fd617d9ab` |
| 1.0 | 0.1 | 0.907 | 0.458 | 0.851 | `52f1f114091a46ca908e0e2743b8d5b6` |
| 1.0 | 0.2 | 0.824 | 0.567 | 0.897 | `0c5a8fd7ae0545f7843649668bc14124` |
| 1.0 | 0.3 | 0.741 | 0.650 | 0.916 | `c1d0e269d90340359671352f04a87c77` |
| 1.0 | 0.4 | 0.663 | 0.723 | 0.924 | `585e46bd43564e8796e8ffc39595506c` |
| 1.0 | 0.5 | 0.580 | 0.773 | 0.924 | `eccd89f3b12a4b30b31b9f1599e066d7` |
| 10.0 | 0.1 | 0.902 | 0.457 | 0.850 | `f18b1ed96ea84693a70f6de4230a0768` |
| 10.0 | 0.2 | 0.824 | 0.567 | 0.897 | `b43fdd1e38e342cb9b1b2023aa7f4695` |
| 10.0 | 0.3 | 0.741 | 0.650 | 0.916 | `6f2c0d4fbadc49f8ad0a1a154d650db0` |
| 10.0 | 0.4 | 0.668 | 0.725 | 0.925 | `4aea57bff77a46a0bc9f3547fb10dc48` |
| 10.0 | 0.5 | 0.580 | 0.768 | 0.924 | `a7853be67a6a44e8b9d96e24042259dd` |
| 100.0 | 0.1 | 0.902 | 0.457 | 0.850 | `2d7f94eadb3c4b89a5bc12c125f8092e` |
| 100.0 | 0.2 | 0.824 | 0.567 | 0.897 | `cafb6640e3b84c25945bf21457ce09a1` |
| 100.0 | 0.3 | 0.741 | 0.650 | 0.916 | `fe0ad975a6d2428086dc1e18aefa26aa` |
| 100.0 | 0.4 | 0.668 | 0.725 | 0.925 | `e5b0687fd3a54ef1a479f8f41006a034` |
| 100.0 | 0.5 | 0.580 | 0.768 | 0.924 | `83cecdb794764f2b96b99b7533904c6b` |

**Analyse.**

- **Le seuil compte beaucoup plus que C.** À C fixé, passer du seuil 0.5 au
  seuil 0.1 fait monter le recall d'environ 0.46–0.58 à 0.90–0.97. À seuil
  fixé, C ne fait varier le recall que de quelques points, et au-delà de
  C = 1 les résultats sont presque identiques (la régularisation n'a plus
  d'effet).
- **Le seuil 0.1 maximise le recall** (0.966 avec C = 0.01), mais la précision
  tombe à 0.384 : environ 1.6 fausse alerte pour chaque vraie panne. C'est trop
  pour une équipe de maintenance, qui finirait par ignorer les alertes.
- **Le seuil 0.2 reste le meilleur compromis** : recall d'environ 0.82–0.83 et
  précision d'environ 0.55–0.57. Les cas C = 0.1 (0.829 / 0.559) et C = 1
  (0.824 / 0.567) sont pratiquement à égalité ; l'écart est d'un ou deux
  relevés sur le jeu de test.

**Conclusion.** Le grid search confirme la décision de l'ADR 004 : une
régression logistique avec un **seuil de 0.2**. C = 1 est conservé (valeur par
défaut, équivalente à C = 0.1 ici). On ne descend à 0.1 que si l'équipe accepte
beaucoup plus de fausses alertes.

## 6. Décision : ADR 004

Voir [docs/adr/004-choix-du-modele.md](docs/adr/004-choix-du-modele.md).
Modèle retenu : régression logistique, C = 1.0, **seuil 0.2**, run
`38f29769b559474db7e05d5d5ce6ebca`, `data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15`.

## 7. Rendu Git

- Branche : `feature/tp5-ayman-mahboub`
- Commits : `DVC : init`, `Données v1`, `Données v2`, compte rendu et ADR 004
- Pull request : https://github.com/rania-532/Prevision_consommation_electrique_batiments/pull/new/feature/tp5-ayman-mahboub
- Non versionnés (exclus par `.gitignore`) : `mlflow.db`, `mlruns/`,
  `data/sensors.csv`, `models/`, `.env`, `.dvc/cache`, `.dvc/config.local`.

Critères de réussite :

| Critère | État |
|---|---|
| 32 tests passent | fait |
| au moins cinq runs dans MLflow | fait (30 runs : 5 du TP + 25 du grid search) |
| deux versions des données sous DVC, poussées dans le stockage | fait |
| retour à la v1 et `dvc pull` réussis | fait |
| ADR 004 avec l'identifiant du run | fait |
| pull request fusionnée et tag `tp5` | à faire après relecture |

## 8. Ticket de sortie

1. **Ce que le MLOps ajoute au DevOps :** le suivi des données et du modèle,
   en plus du code ; la vérification par des métriques comparées run par run ;
   le ré-entraînement quand les données dérivent, même sans nouveau code.
2. **Ce que versionnent Git, DVC et MLflow :** Git le code et les reçus `.dvc` ;
   DVC les fichiers de données ; MLflow les entraînements (paramètres,
   `data_md5`, métriques, modèle et dépendances).
3. **Pourquoi `data/sensors.csv` n'est pas dans Git :** il peut être
   volumineux et Git en garderait chaque version ; seul son reçu de quelques
   octets y est versionné, le fichier est dans le stockage DVC.
4. **Retrouver les données d'un run :** prendre son `data_md5`, retrouver le
   commit du `.dvc` qui porte ce md5, `git checkout <commit> --
   data/sensors.csv.dvc` puis `dvc checkout` / `dvc pull`.
5. **Ce qui reste flou :** comment partager un stockage DVC réel (S3, Google
   Drive) entre les membres du groupe, et comment comparer proprement deux
   modèles entraînés sur des versions de données différentes.
