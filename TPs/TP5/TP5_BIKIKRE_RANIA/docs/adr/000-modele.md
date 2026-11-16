# ADR 004 : Choix du modèle de prédiction

Date : 16/11/2026 · Auteurs : BIKIKRE Rania

## Contexte

Le projet MaintAI doit détecter les pannes de machines à partir de données de capteurs. Il faut retenir un modèle et un seuil de décision adaptés à cette tâche. La détection des pannes réelles est prioritaire afin de limiter les pannes non détectées.

## Options étudiées

1. **Régression logistique** : modèle simple et interprétable, avec de bonnes performances selon le seuil choisi.
2. **Random Forest** : modèle plus complexe, testé comme alternative à la régression logistique.

## Décision

La régression logistique avec `C=1.0` et un seuil de décision de `0.2` est retenue.

Ce choix privilégie le recall, qui atteint `0.838`, contre une précision de `0.543`. Le recall est prioritaire dans ce projet afin de détecter le maximum de pannes réelles.

- **Run ID MLflow :** `89a005a69bda4beb955532be45244417`
- **Version des données :** v1
- **data_md5 :** `73e0b7cb3c6f795c70c3ddf970b99c15`

## Conséquences

Ce choix permet de détecter davantage de pannes réelles, mais entraîne davantage de fausses alertes. Il faudra surveiller l'équilibre entre le recall et la précision lors des prochaines évaluations.