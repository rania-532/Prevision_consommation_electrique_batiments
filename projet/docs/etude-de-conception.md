# Étude de conception — Application intelligente de prévision de la consommation électrique d'un bâtiment

**Groupe :** 4  
**Version :** 1.0 — Brouillon  
**Date :** 19/10/2026

## 1. Contexte et utilisateurs

### 1.1 Contexte

La consommation électrique représente un enjeu important pour les bâtiments tertiaires, notamment en matière de coûts énergétiques et d'efficacité énergétique.

Ce projet consiste à développer une application intelligente capable de prévoir la consommation électrique future d'un bâtiment à partir de ses données historiques. L'application permettra de visualiser les consommations passées et les prévisions afin d'aider l'utilisateur à mieux anticiper ses besoins énergétiques.

### 1.2 Utilisateur cible

L'utilisateur principal est le responsable énergétique du bâtiment. Il pourra consulter l'historique de consommation, visualiser les prévisions et identifier les périodes de consommation élevée.

## 2. Problématique et objectifs

### 2.1 Problématique

Comment exploiter les données historiques de consommation électrique d'un bâtiment pour prévoir sa consommation future et faciliter la prise de décision énergétique ?

### 2.2 Objectif principal

Développer une application basée sur le machine learning permettant de prévoir la consommation électrique d'un bâtiment et de présenter les résultats dans une interface interactive.

### 2.3 Objectifs spécifiques

- Collecter et préparer les données de consommation électrique.
- Analyser les tendances et les variations de consommation.
- Entraîner et comparer plusieurs modèles de prévision.
- Évaluer les performances des modèles.
- Intégrer le modèle retenu dans une application Streamlit.
- Visualiser les données historiques et les consommations prévues.

### 2.4 Fonctionnalités prévues

- Consultation des données historiques.
- Visualisation de la consommation sous forme de graphiques.
- Sélection de l'horizon de prévision selon les capacités du modèle.
- Affichage des consommations prévues.
- Comparaison entre les valeurs prévues et les valeurs réelles lorsque celles-ci sont disponibles.

## 3. Approche de résolution

| Sous-problème | Approche retenue | Objectif |
|---|---|---|
| Préparation des données | Règles de nettoyage avec pandas et numpy | Obtenir des données fiables |
| Analyse des consommations | Statistiques et visualisations | Identifier les tendances et la saisonnalité |
| Prévision de la consommation | Machine learning avec scikit-learn | Apprendre les comportements de consommation |
| Évaluation des modèles | MAE et RMSE | Comparer les performances |
| Interface utilisateur | Streamlit | Présenter les données et les prévisions |
| Tests | pytest | Vérifier le fonctionnement des composants |

Une méthode de référence simple sera comparée aux modèles de machine learning afin de vérifier que leur complexité apporte une amélioration réelle.

## 4. Données

### 4.1 Source envisagée

Le jeu de données envisagé est le **Building Data Genome Project 2 (BDG2)**, qui contient des mesures de consommation de bâtiments ainsi que des données météorologiques associées.

Source : https://github.com/buds-lab/building-data-genome-project-2

Publication scientifique : https://doi.org/10.1038/s41597-020-00712-x

La sélection définitive des données sera effectuée après vérification de leur disponibilité, de leur structure, de leur licence et de leur adéquation avec le problème étudié.

### 4.2 Variables envisagées

- Date et heure de mesure.
- Consommation électrique.
- Identifiant du bâtiment, si nécessaire.
- Variables météorologiques disponibles et pertinentes.

### 4.3 Préparation des données

Les opérations prévues comprennent :

- Le chargement des fichiers.
- La vérification des types et des unités.
- Le traitement des valeurs manquantes et des doublons.
- La vérification des dates et de la fréquence des mesures.
- La création de variables temporelles.
- La séparation chronologique des données pour l'entraînement, la validation et le test.

Les données brutes seront conservées séparément des données préparées.

## 5. Modélisation et critères d'évaluation

### 5.1 Modèles envisagés

Les approches suivantes seront étudiées :

- **Baseline :** utilisation de la consommation observée à une période comparable.
- **Régression Ridge :** modèle de régression linéaire régularisée.
- **Random Forest :** modèle basé sur un ensemble d'arbres de décision.
- **Gradient Boosting :** modèle d'ensemble à évaluer selon les résultats obtenus.

Le choix final dépendra des performances mesurées sur les données de validation.

### 5.2 Métriques d'évaluation

- **MAE (Mean Absolute Error) :** mesure l'erreur absolue moyenne.
- **RMSE (Root Mean Squared Error) :** pénalise davantage les erreurs importantes.

Les résultats seront calculés sur des données de test qui n'auront pas servi à entraîner ou à régler les modèles.

### 5.3 Stratégie de validation

La séparation des données respectera leur ordre chronologique afin d'éviter d'utiliser des informations futures pour prévoir le passé.

Les performances des modèles seront comparées à celles de la baseline. Les résultats et les critères d'acceptation définitifs seront fixés après les premiers essais.

## 6. Architecture de l'application

L'application sera organisée en plusieurs composants indépendants :

1. **Configuration :** centralisation des chemins et paramètres dans `config.py`.
2. **Gestion des données :** chargement et préparation dans `data.py`.
3. **Entraînement :** entraînement et évaluation des modèles dans `train.py`.
4. **Stockage du modèle :** sauvegarde du modèle retenu dans `models/`.
5. **Prédiction :** chargement du modèle et génération des prévisions dans `predict.py`.
6. **Interface :** affichage interactif des données et des prévisions avec Streamlit dans `ui/`.
7. **Tests :** vérification du fonctionnement des composants dans `tests/`.

### Flux de fonctionnement

Données brutes → Préparation → Entraînement et évaluation → Modèle sauvegardé → Prédiction → Interface Streamlit.

## 7. Choix technologiques

| Besoin | Technologie | Utilisation |
|---|---|---|
| Langage | Python | Développement général |
| Manipulation des données | pandas, numpy | Chargement, nettoyage et transformation |
| Machine learning | scikit-learn | Entraînement et évaluation |
| Sauvegarde des modèles | joblib | Sérialisation du modèle |
| Interface utilisateur | Streamlit | Application interactive |
| Visualisation | Matplotlib ou Plotly | Graphiques de consommation |
| Tests | pytest | Tests unitaires et d'intégration |
| Gestion des versions | Git et GitHub | Collaboration et suivi du code |
| Conteneurisation | Docker et Docker Compose | Exécution reproductible |
| Intégration continue | GitHub Actions | Automatisation des tests |

Les versions précises des dépendances seront définies dans `requirements.txt`.

## 8. Risques et considérations

| Risque | Conséquence possible | Mesure prévue |
|---|---|---|
| Données manquantes ou incorrectes | Prévisions moins fiables | Contrôle et nettoyage des données |
| Historique insuffisant | Difficulté à apprendre les tendances | Vérification de la couverture temporelle |
| Surapprentissage | Mauvaise généralisation | Validation chronologique et comparaison des modèles |
| Pics difficiles à prévoir | Erreurs importantes pendant les périodes critiques | Analyse spécifique des erreurs |
| Différences entre bâtiments | Performances variables | Évaluation adaptée aux données disponibles |
| Mauvaise utilisation des prévisions | Décisions énergétiques inadaptées | Présentation claire des limites du modèle |

Le système constitue une aide à la décision. Il ne commande pas automatiquement les équipements électriques du bâtiment.

Les données utilisées seront vérifiées afin de limiter l'exposition d'informations sensibles. Aucune donnée ne sera envoyée à un service externe sans nécessité et décision explicite.

## 9. Limites et périmètre du projet

### 9.1 Périmètre

Le projet comprend la préparation des données, l'analyse exploratoire, le développement et l'évaluation d'un modèle de prévision, la création d'une interface Streamlit ainsi que les tests et le déploiement.

### 9.2 Limites

- Les performances dépendent de la qualité et de la quantité des données disponibles.
- La généralisation à d'autres bâtiments devra être évaluée séparément.
- Les prévisions météorologiques futures ne pourront être utilisées que si elles sont disponibles au moment de la prédiction.
- Le système fournit des prévisions et ne réalise pas de pilotage automatique.
- Les résultats ne garantissent pas une prédiction exacte de la consommation future.

Les extensions éventuelles, comme les alertes avancées ou les recommandations d'efficacité énergétique, seront envisagées après la réalisation du périmètre principal.

## Conclusion

Ce projet vise à concevoir une application intelligente permettant d'anticiper la consommation électrique d'un bâtiment grâce au machine learning. La séparation entre la préparation des données, l'entraînement, la prédiction et l'interface Streamlit permettra de développer une solution modulaire, testable et évolutive.
