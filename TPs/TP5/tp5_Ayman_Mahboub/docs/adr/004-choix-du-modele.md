# ADR 004 — Choix du modèle et du seuil à partir des runs MLflow

| Élément | Valeur |
|---|---|
| Date | 16/11/2026 |
| Auteur | Mahboub Ayman |
| Statut | Acceptée |
| Remplace | précise l'ADR 000 (le seuil passe de 0.3 à 0.2) |

## 1. Contexte

Depuis le TP5, chaque entraînement de MaintAI est enregistré comme un run
MLflow (expérience `maintai`) avec ses paramètres, l'empreinte `data_md5` des
données, ses métriques et le modèle avec ses dépendances. Les données sont
versionnées avec DVC. On peut donc choisir le modèle à partir de résultats
comparables et traçables.

Quatre réglages ont été comparés sur les **mêmes données v1**
(`data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15`, 5 000 relevés, 1 000 en test) :

| Run | Modèle | C | Seuil | Recall | Precision | Accuracy |
|---|---|---:|---:|---:|---:|---:|
| `f7b612783c6e4075970cc6724380ebf3` | logreg | 1.0 | 0.3 | 0.750 | 0.622 | 0.904 |
| `df99319979b74e618e50f4645688bc35` | logreg | 0.01 | 0.3 | 0.691 | 0.653 | 0.908 |
| `38f29769b559474db7e05d5d5ce6ebca` | logreg | 1.0 | **0.2** | **0.838** | 0.543 | 0.882 |
| `589f44a69d6d4f559989036935cdae22` | forest | — | 0.3 | 0.728 | 0.562 | 0.886 |

La baseline « toujours pas de panne » a un recall de 0.

## 2. Contrainte qui guide le choix

Une panne manquée (faux négatif) coûte beaucoup plus cher qu'une fausse alerte
(intervention inutile). Le critère principal est donc le **recall**, la
précision restant un critère secondaire.

## 3. Décision

Nous retenons la **régression logistique (pipeline `StandardScaler` +
`LogisticRegression`, C = 1.0) avec un seuil d'alerte de 0.2**.

- Run MLflow de référence : `38f29769b559474db7e05d5d5ce6ebca`
- Données : `data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15` (données v1, commit
  Git « Données v1 » de `data/sensors.csv.dvc`)
- Dépendance figée par MLflow : `scikit-learn==1.8.0`

La forêt aléatoire n'est pas meilleure ici : au même seuil (0.3), elle a un
recall plus faible (0.728 contre 0.750) et une précision plus faible
(0.562 contre 0.622) que la régression logistique, tout en étant plus lourde
et moins explicable. Une régularisation forte (C = 0.01) fait baisser le
recall (0.691) : elle est écartée.

## 4. Ce que nous acceptons en échange

- Plus de fausses alertes : la précision passe de 0.622 (seuil 0.3) à 0.543
  (seuil 0.2), soit près d'une alerte sur deux injustifiée.
- Une accuracy un peu plus basse (0.882 contre 0.904).

En échange, le recall passe de 0.750 à 0.838 : environ 8 pannes sur 100 en
plus sont détectées.

### Confirmation par grid search (25 cas)

Une recherche sur grille (C ∈ {0.01, 0.1, 1, 10, 100} × seuil ∈ {0.1, 0.2,
0.3, 0.4, 0.5}, données v2 `93fdeef2…`, voir `COMPTE_RENDU.md` §5 bis)
confirme ce choix : le seuil influence beaucoup plus le recall que C. Le seuil
0.1 atteint un recall de 0.966 mais une précision de 0.384, ce qui fait trop de
fausses alertes. Le seuil 0.2 donne recall ≈ 0.82–0.83 et précision ≈
0.55–0.57 pour toutes les valeurs de C (run C = 1 : `0c5a8fd7ae0545f7843649668bc14124`).

## 5. Conséquences

- En production, `MAINTAI_THRESHOLD` doit valoir `0.2`.
- Pour retrouver exactement les données de ce run :
  `git checkout <commit Données v1> -- data/sensors.csv.dvc` puis
  `dvc checkout` (ou `dvc pull` sur un autre poste).
- À chaque nouvelle version des données, ré-entraîner avec les mêmes réglages
  et comparer les runs ; ne comparer des recalls que sur un même jeu de test.
