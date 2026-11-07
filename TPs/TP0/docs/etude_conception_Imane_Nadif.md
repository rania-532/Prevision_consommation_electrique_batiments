# Étude de conception — Mainetenance IA

Groupe : Imane Nadif · Version : brouillon · Date : 26/10/2026

## 1. Contexte et utilisateurs
- Utilisateur principal (un rôle précis) : le technicien ou responsable maintenance qui planifie les interventions et doit repérer les équipements susceptibles de tomber en panne. Il s'appuie sur la prédiction pour prioriser, mais garde la décision finale.

## 2. Problème et décision
- Décision que l'utilisateur prend avec le système : pour chaque équipement, déclencher une inspection ou une maintenance préventive (panne prédite) ou le laisser en service.
- Fréquence : à chaque nouvelle mesure ou par lot, selon le rythme de collecte des données.
- Coût d'une erreur, et pour qui :
  - Faux négatif (panne ratée) : coût élevé pour l'exploitant, avec arrêt non planifié, réparation en urgence et risque sécurité éventuel.
  - Faux positif (fausse alerte) : coût plus faible, une inspection inutile pour le technicien.
  - Ce déséquilibre justifie de privilégier le recall.

## 3. Approche par sous-problème
| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Prédire les pannes (classification binaire sur données tabulaires) | ML classique : régression logistique, arbre de décision, forêt aléatoire, comparés dans un même pipeline | La baseline (classe majoritaire) obtient un recall de 0,000 : une règle triviale ne détecte aucune panne. |
| Préparer les données (valeurs manquantes, échelle, catégories) | Règles de prétraitement fixes : imputation, standardisation, encodage one-hot | Un traitement déterministe suffit, sans apprentissage. |
| Choisir le modèle final | Comparaison automatique sur la métrique principale | Une comparaison chiffrée évite un choix arbitraire. |

DL, LLM et RAG ne sont pas retenus : les données sont tabulaires et les modèles classiques sont plus simples à expliquer et à valider.

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| data/exemple_pannes.csv | Jeu d'exemple fourni avec le projet de cours [à confirmer : licence / origine] | 5000 lignes × 5 colonnes (4 variables d'entrée + cible `failure`) | Non : mesures de capteurs uniquement (temperature_c, vibration_mm_s, load_pct, runtime_hours), aucune donnée sur des personnes |

Particularité : classes déséquilibrées, 878 pannes (17,6 %) contre 4122 cas sans panne (82,4 %).

## 5. Métriques, baseline et critères d'acceptation
- Baseline et son score : DummyClassifier (classe majoritaire). Accuracy 0,824, mais recall 0,000, precision 0,000 et F1 0,000 : il ne détecte jamais la classe positive (la panne). Son accuracy vient uniquement du déséquilibre des classes (82,4 % sans panne).
- Métrique principale, et pourquoi : le recall de la classe positive (la panne). L'accuracy est trompeuse, puisque la baseline atteint 0,824 sans rien détecter. Rater une panne coûte plus cher qu'une fausse alerte. La precision et le F1 sont suivis pour éviter de tout classer en panne.
- Critères d'acceptation (métrique, nombre, jeu de données, condition) :
  - Recall ≥ 0,60 sur le jeu de test (même découpage, même graine).
  - Condition : precision ≥ 0,60 sur ce même jeu.
  - Le modèle doit battre la baseline sur le recall et le F1.
  - Résultats actuels (recall / precision / F1) : decision_tree 0,597 / 0,538 / 0,566 ; logistic_regression 0,574 / 0,737 / 0,645 ; random_forest 0,545 / 0,671 / 0,602. Aucun modèle ne remplit encore les deux critères.


  # Étude de conception — cantine ia

Groupe : [noms] · Version : brouillon · Date : 26/10/2026

## 1. Contexte et utilisateurs
- Utilisateur principal (un rôle précis) : le responsable de la cantine, qui commande les denrées et planifie le personnel chaque jour. Il s'appuie sur la prédiction pour ajuster les quantités, mais garde la décision finale.

## 2. Problème et décision
- Décision que l'utilisateur prend avec le système : combien de repas préparer (et donc quelles quantités commander) pour un jour donné.
- Fréquence : quotidienne (un jour de classe = une prédiction).
- Coût d'une erreur, et pour qui :
  - Surestimation : gaspillage alimentaire et surcoût pour la cantine.
  - Sous-estimation : élèves non servis ou portions réduites, mécontentement.
  - Les deux erreurs coûtent à peu près proportionnellement à l'écart en nombre de repas, d'où le choix du MAE.

## 3. Approche par sous-problème
| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Prédire le nombre de repas servis (régression sur données tabulaires) | ML classique : régression linéaire, arbre de décision, forêt aléatoire, comparés dans un même pipeline | La baseline (moyenne) se trompe de 35 repas en moyenne, soit 6,5 % : elle ignore le jour, le menu, la météo et les événements. |
| Préparer les données (valeurs manquantes, échelle, catégories jour et menu) | Règles de prétraitement fixes : imputation, standardisation, encodage one-hot | Un traitement déterministe suffit, sans apprentissage. |
| Choisir le modèle final | Comparaison automatique sur la métrique principale | Une comparaison chiffrée évite un choix arbitraire. |

DL, LLM et RAG ne sont pas retenus : 340 lignes tabulaires, et un modèle linéaire est simple à expliquer au responsable.

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| data/cantine_repas.csv | [source et licence à confirmer] | 340 lignes × 11 colonnes (du 09/09/2024 au 26/02/2026) | Non : effectifs et conditions du jour, aucune donnée sur des personnes |

Colonnes d'entrée : jour, inscrits, menu, temperature_c, pluie_mm, examens, sortie_scolaire, veille_vacances, repas_semaine_precedente. Cible : repas_servis (moyenne 538,8 ; écart-type 47,6 ; min 358 ; max 662). Les premières lignes n'ont pas de repas_semaine_precedente (début de série), gérées par imputation.

## 5. Métriques, baseline et critères d'acceptation
- Baseline et son score : DummyRegressor (moyenne du jeu d'entraînement). MAE 34,986 repas (6,5 % de la moyenne), RMSE 45,738, R² -0,006 : il n'explique aucune variation.
- Métrique principale, et pourquoi : le MAE, en nombre de repas par jour. Il se lit directement par le responsable (« je me trompe de X repas ») et sa pénalité est proportionnelle à l'écart, comme le coût du gaspillage ou de la pénurie. Le RMSE et le R² sont suivis pour détecter les grosses erreurs.
- Critères d'acceptation (métrique, nombre, jeu de données, condition) :
  - MAE ≤ 25 repas par jour (environ 4,6 %) sur le jeu de test chronologique (les 20 % de jours les plus récents).
  - Condition : MAE inférieur d'au moins 25 % à celui de la baseline.
  - Résultats actuels (MAE / RMSE / R²) : régression linéaire 19,824 / 24,363 / 0,715 ; forêt aléatoire 21,891 / 26,950 / 0,651 ; arbre de décision 28,118 / 34,685 / 0,422. Critères atteints par la régression linéaire (MAE 19,8, soit 43 % de moins que la baseline) et par la forêt (21,9, soit 37 % de moins).