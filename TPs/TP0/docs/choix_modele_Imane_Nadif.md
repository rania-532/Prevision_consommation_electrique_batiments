# Choix du modèle

Date : 26/10/2026 · Groupe : imane nadif

## Contexte
Prédire les pannes d'équipements à partir de mesures de capteurs (classification binaire), pour aider le technicien maintenance à décider d'une inspection préventive. La métrique principale est le recall de la classe « panne » : rater une panne coûte plus cher qu'une fausse alerte, et l'accuracy est trompeuse (la baseline atteint 0,824 sans rien détecter).

## Données et découpage
- Fichier : data/exemple_pannes.csv, 5000 lignes, 878 pannes (17,6 %) et 4122 cas sans panne.
- Colonnes utilisées : temperature_c, vibration_mm_s, load_pct, runtime_hours (cible : failure).
- Découpage : aléatoire stratifié sur la cible, graine 42.
- Jeu de test : 20 %, soit 1000 lignes dont 176 pannes ; jeu d'entraînement : 4000 lignes.

## Résultats sur le jeu de test

| Modèle | Métrique principale (recall) | Autres métriques |
|---|---|---|
| Baseline (classe majoritaire) | 0,000 | accuracy 0,824 · precision 0,000 · F1 0,000 |
| Régression logistique | 0,574 | accuracy 0,889 · precision 0,737 · F1 0,645 |
| Arbre de décision | 0,597 | accuracy 0,839 · precision 0,538 · F1 0,566 |
| Forêt aléatoire | 0,545 | accuracy 0,873 · precision 0,671 · F1 0,602 |

## Décision
Modèle retenu : l'arbre de décision, qui a le meilleur recall (0,597) donc la meilleure détection des pannes, ce qui suit la règle de sélection fixée en section 5. Il bat largement la baseline (recall 0,597 contre 0,000, F1 0,566 contre 0,000).

Le critère d'acceptation n'est pas atteint : recall 0,597 (< 0,60, de très peu) et precision 0,538 (< 0,60). Aucun des trois modèles ne remplit les deux conditions. La régression logistique est le meilleur compromis (precision 0,737, F1 0,645) avec un recall légèrement inférieur (0,574). Si l'on préfère moins de fausses alertes, c'est elle qu'il faudrait retenir, en le justifiant.

## Limites
- L'écart de recall entre les trois modèles est faible (0,545 à 0,597) : sur 176 pannes de test, cela représente environ 9 pannes détectées en plus ou en moins, donc le classement n'est pas fiable.
- Un seul découpage train/test, sans validation croisée : les scores peuvent changer avec une autre graine.
- Aucun réglage d'hyperparamètres ni ajustement du seuil de décision, leviers possibles pour améliorer le recall.
- Le fichier est un jeu d'exemple (probablement synthétique) : les résultats ne garantissent rien sur des données réelles.
- Pas d'analyse des cas mal couverts (types de pannes ou plages de valeurs ratées).

# Choix du modèle

Date : 26/10/2026 · Groupe : [noms]

## Contexte
Prédire le nombre de repas servis chaque jour à la cantine (régression sur données tabulaires), pour aider le responsable à fixer les quantités à préparer. La métrique principale est le MAE, en nombre de repas par jour : il se lit directement et pénalise gaspillage et pénurie proportionnellement à l'écart.

## Données et découpage
- Fichier : data/cantine_repas.csv, 340 lignes, du 09/09/2024 au 26/02/2026 ; cible : repas_servis (moyenne 538,8).
- Colonnes utilisées : jour, inscrits, menu, temperature_c, pluie_mm, examens, sortie_scolaire, veille_vacances, repas_semaine_precedente (la date sert uniquement au tri).
- Découpage : chronologique (le modèle apprend le passé et est testé sur le futur).
- Jeu de test : 20 %, soit les 68 jours les plus récents ; jeu d'entraînement : 272 jours.

## Résultats sur le jeu de test

| Modèle | Métrique principale (MAE) | Autres métriques |
|---|---|---|
| Baseline (moyenne) | 34,986 | RMSE 45,738 · R² -0,006 |
| Régression linéaire | 19,824 | RMSE 24,363 · R² 0,715 |
| Forêt aléatoire | 21,891 | RMSE 26,950 · R² 0,651 |
| Arbre de décision | 28,118 | RMSE 34,685 · R² 0,422 |

## Décision
Modèle retenu : la régression linéaire, qui a le plus petit MAE (19,8 repas par jour, soit environ 3,7 % de la moyenne) et le meilleur R² (0,715). Elle bat la baseline de 15,2 repas, soit 43 % d'erreur en moins.

Le critère d'acceptation est atteint : MAE ≤ 25 repas et au moins 25 % de moins que la baseline. La forêt aléatoire l'atteint aussi (21,9, soit 37 % de moins), mais elle est moins précise et plus difficile à expliquer. Le modèle linéaire est donc le choix à la fois le plus précis et le plus simple.

## Limites
- Le jeu de test ne contient que 68 jours : l'écart entre la régression linéaire et la forêt (environ 2 repas par jour) est trop petit pour affirmer que l'un est meilleur.
- Un seul découpage, sans validation croisée temporelle : les scores peuvent changer selon la période testée, qui peut avoir des particularités saisonnières (hiver, périodes d'examens).
- Les variables météo (température, pluie) sont connues le jour même dans le fichier : en usage réel, elles devraient venir de prévisions, donc l'erreur réelle serait probablement plus grande.
- Aucun réglage d'hyperparamètres, et la baseline « moyenne » est faible : une baseline « même nombre de repas que la semaine précédente » serait plus exigeante.
- Données d'un seul établissement : pas de garantie sur d'autres cantines ou d'autres années.