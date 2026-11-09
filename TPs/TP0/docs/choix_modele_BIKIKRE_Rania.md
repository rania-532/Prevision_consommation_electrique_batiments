# Choix du modèle — MaintAI

**Date :** 26/10/2026 · **Membre :** Rania Bikikre

## Contexte

MaintAI vise à prédire les pannes de machines à partir de relevés de capteurs afin d'aider le responsable de maintenance à planifier les inspections. Une panne manquée pouvant entraîner l'arrêt d'une ligne de production pendant une journée, la métrique principale retenue est le **recall**, qui mesure la proportion de pannes réelles détectées par le modèle.

## Données et découpage

- **Fichier :** `data/exemple_pannes.csv`
- **Nombre de lignes :** 5 000 relevés synthétiques.
- **Variables utilisées :** température, vibration, charge et heures de fonctionnement.
- **Variable cible :** `failure`.
- **Proportion de pannes :** 17,6 %.
- **Découpage :** [aléatoire ou chronologique, à confirmer dans la configuration utilisée].
- **Taille du jeu de test :** [à confirmer à partir du découpage réellement exécuté].

Les modèles sont entraînés sur le jeu d'entraînement, puis comparés sur le même jeu de test afin d'assurer une comparaison cohérente.

## Résultats sur le jeu de test

| Modèle | Recall (métrique principale) | Accuracy | Precision | F1-score |
|---|---:|---:|---:|---:|
| Baseline | 0,000 | 0,824 | 0,000 | 0,000 |
| Régression logistique | **0,847** | 0,839 | 0,527 | 0,649 |
| Forêt aléatoire | 0,540 | 0,882 | 0,720 | 0,617 |
| Gradient Boosting | 0,608 | 0,888 | 0,713 | 0,656 |
| K plus proches voisins (KNN) | 0,540 | 0,878 | 0,699 | 0,609 |

## Décision

Le modèle retenu est la **régression logistique**, car il obtient le meilleur recall parmi les modèles testés, avec un score de **0,847**, soit 84,7 % des pannes réelles détectées.

Par rapport à la baseline, son recall augmente de **0,847 point**, soit 84,7 points de pourcentage. Le gain relatif n'est pas calculable, car le recall initial de la baseline est nul.

Le critère d'acceptation proposé d'un recall d'au moins 0,80 est atteint : le modèle obtient 0,847. Il détecte donc une plus grande proportion de pannes que les autres modèles testés.

Cependant, sa précision de 0,527 indique qu'environ 52,7 % de ses alertes correspondent à des pannes réelles. Des inspections inutiles restent donc possibles.

La forêt aléatoire et le Gradient Boosting obtiennent de meilleures accuracies, respectivement 0,882 et 0,888, mais leurs recalls sont plus faibles. Dans ce projet, une accuracy élevée ne suffit pas si le modèle manque trop de pannes.

## Limites

- **Données synthétiques :** Les résultats ne garantissent pas les mêmes performances sur les machines d'une véritable usine.
- **Taille du test :** Le nombre exact de lignes utilisées pour l'évaluation doit être confirmé à partir du découpage réellement exécuté.
- **Représentativité :** Les situations rares ou les types de pannes absents du jeu de données peuvent être mal détectés.
- **Fausses alertes :** La précision de 0,527 montre qu'une part importante des alertes ne correspond pas à une panne réelle.
- **Seuil de décision :** Les résultats dépendent notamment du seuil de classification utilisé. Celui-ci pourrait être ajusté en fonction du coût des pannes manquées et des inspections inutiles.
- **Validation industrielle :** Une validation sur des données réelles et un suivi régulier des performances sont nécessaires avant le déploiement.
- **Découpage des données :** Le type de découpage utilisé doit être confirmé. Si les données représentent une évolution temporelle des machines, un test chronologique serait préférable pour évaluer la capacité du modèle à généraliser vers des relevés futurs.





//////////////////////////////////////////////////////////////



# Choix du modèle — CantineAI

## 1. Objectif

L'objectif est de sélectionner le modèle capable de prédire le nombre de repas servis le lendemain avec l'erreur moyenne la plus faible.

Le problème étant une régression, la métrique principale retenue est la MAE (*Mean Absolute Error*).

## 2. Modèles comparés

Cinq modèles ont été évalués sur le même jeu de test chronologique :
- **Baseline** : modèle de référence utilisant la moyenne du nombre de repas observé pendant l'entraînement.
- **Ridge** : régression linéaire régularisée.
- **Forêt aléatoire** : ensemble d'arbres de décision.
- **Gradient Boosting** : ensemble d'arbres construits successivement pour améliorer les prédictions.
- **K plus proches voisins** : prédiction fondée sur les observations les plus similaires.

## 3. Résultats obtenus

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Ridge | 19,770 | 24,325 | 0,716 |
| Forêt aléatoire | 21,970 | 27,168 | 0,645 |
| Gradient Boosting | 23,126 | 27,483 | 0,637 |
| K plus proches voisins | 23,397 | 27,674 | 0,632 |
| Baseline | 34,986 | 45,738 | -0,006 |

## 4. Modèle retenu

Le modèle **Ridge** est retenu, car il obtient la MAE la plus faible, soit 19,77 repas, ainsi que le meilleur R², égal à 0,716.

En moyenne, ses prédictions s'écartent d'environ 20 repas des valeurs réelles sur le jeu de test. Son R² indique qu'il explique une part importante de la variabilité observée, contrairement à la baseline dont le R² est proche de zéro.

Par rapport à la baseline, Ridge réduit la MAE d'environ 43,5 % :

Réduction relative = (34,986 − 19,770) / 34,986 × 100 ≈ 43,5 %.

Ces résultats sont encourageants, mais ils ne prouvent pas encore que le modèle surpasse la méthode actuellement utilisée par la cantine.

## 5. Justification du choix

Ridge présente les meilleurs résultats parmi les modèles testés. Il offre une erreur moyenne plus faible que les modèles à base d'arbres et que les k plus proches voisins.

Sa régularisation permet de limiter l'influence excessive des variables et convient à un dataset de taille relativement modeste.

## 6. Limites et améliorations

La baseline actuelle prédit la moyenne des repas du jeu d'entraînement. Or, la méthode actuellement utilisée par la cantine consiste à reprendre le nombre de repas du même jour de la semaine précédente.

Une prochaine amélioration importante consiste donc à comparer Ridge à cette règle métier, afin de vérifier si l'apprentissage automatique apporte réellement un gain supplémentaire.

Il faudra également vérifier que les données météorologiques, les menus et les informations sur les sorties scolaires sont bien disponibles au moment de la prédiction, sans utiliser d'informations futures.

## 7. Conclusion

Au vu des métriques obtenues, Ridge est le meilleur modèle parmi les cinq modèles comparés. Il constitue un choix pertinent pour un premier prototype de CantineAI.

Avant le déploiement, il reste nécessaire de confirmer son avantage par rapport à la méthode actuelle et d'évaluer ses conséquences sur le gaspillage alimentaire et les repas manquants.


