# Étude de conception — MaintAI : prédire les pannes de machines

**Membre :** Rania Bikikre · **Version :** Finale· **Date :** 26/10/2026

## 1. Contexte et utilisateurs

- **Utilisateur principal :** Le responsable de maintenance d'une usine, chargé de planifier les inspections des machines.
- **Contexte :** Chaque matin, l'équipe de maintenance doit identifier les machines à inspecter afin d'anticiper les pannes et de limiter les interruptions de production.
- **Objectif du système :** Prédire les pannes à partir des données des capteurs afin d'aider l'équipe à prioriser les inspections.

## 2. Problème et décision

- **Décision que l'utilisateur prend avec le système :** Choisir les machines à inspecter en priorité en fonction du risque de panne prédit.
- **Fréquence :** Toutes les 5 minutes.
- **Coût d'une erreur, et pour qui :**
  - **Faux négatif :** Une panne réelle n'est pas détectée, ce qui peut entraîner l'arrêt d'une ligne de production pendant une journée.
  - **Faux positif :** Une machine est signalée à tort et nécessite une heure d'inspection inutile.
- **Enjeu principal :** Réduire les pannes manquées tout en limitant les inspections inutiles.

## 3. Approche par sous-problème

| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Prédiction des pannes | Machine Learning supervisé : classification binaire | Des seuils fixes sur chaque capteur ne permettent pas toujours de détecter des combinaisons complexes de valeurs annonçant une panne. |
| Identification des machines à risque | Classification à partir de la température, des vibrations, de la charge et des heures de fonctionnement | Une simple règle fondée sur un seul capteur peut manquer des situations à risque. |
| Comparaison des modèles | Évaluation avec une baseline, une régression logistique, une forêt aléatoire, un Gradient Boosting et les k plus proches voisins | Tester plusieurs modèles permet de vérifier si une méthode plus complexe apporte réellement un gain. |
| Aide à la décision | Règles de priorisation fondées sur les prédictions du modèle | Un LLM ou un système RAG n'est pas nécessaire pour prédire une panne à partir de données numériques structurées. |

## 4. Données

| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| `data/exemple_pannes.csv` | Fichier fourni pour le TP ; licence non précisée | 5 000 relevés de capteurs | Non, selon la description du jeu de données |
 
**Variables utilisées :**
- Température
- Vibration
- Charge
- Heures de fonctionnement

**Variable cible :** `failure`, indiquant si une panne est survenue.

**Répartition de la cible :** 17,6 % des relevés se terminent par une panne.

## 5. Métriques, baseline et critères d'acceptation

- **Baseline :** `DummyClassifier` avec la stratégie `most_frequent`, qui prédit systématiquement la classe majoritaire.
- **Score de la baseline :** Recall = 0,000 ; accuracy = 0,824.
- **Métrique principale :** Le recall, car une panne manquée peut provoquer l'arrêt d'une ligne de production pendant une journée. Il est donc important de détecter un maximum de pannes réelles.
- **Métriques complémentaires :**
  - Accuracy : proportion totale de prédictions correctes.
  - Precision : proportion des alertes de panne qui correspondent à de vraies pannes.
  - F1-score : moyenne harmonique entre la précision et le recall.

**Critères d'acceptation proposés :**
1. Le modèle doit obtenir un recall supérieur à celui de la baseline.
2. Le recall doit atteindre au moins 0,80 sur le jeu de test.
3. La précision doit être examinée pour évaluer le volume d'inspections inutiles générées par les alertes.
4. Les résultats doivent être évalués sur des données qui n'ont pas servi à entraîner le modèle.

Le seuil de recall de 0,80 est une cible de conception proposée, à confirmer avec le responsable de maintenance.

## 8. Risques, éthique et confidentialité

- **Pannes manquées :** Le modèle peut ne pas détecter certaines pannes, avec des conséquences importantes sur la production.
- **Fausses alertes :** Un nombre élevé de prédictions positives incorrectes peut entraîner des inspections inutiles et mobiliser excessivement l'équipe de maintenance.
- **Qualité des données :** Des capteurs défectueux, des valeurs manquantes ou des données peu représentatives peuvent réduire les performances du modèle.
- **Biais et représentativité :** Les données synthétiques ne reproduisent pas nécessairement toutes les situations rencontrées dans une véritable usine.
- **Confidentialité :** Le jeu de données décrit contient des mesures techniques de machines, sans données personnelles identifiées. Les données industrielles réelles peuvent néanmoins être confidentielles.
- **Sécurité :** Le modèle doit rester un outil d'aide à la décision. Les décisions critiques doivent tenir compte des procédures de sécurité et de l'expertise humaine.
- **Limites d'utilisation :** Les performances obtenues sur des données synthétiques doivent être validées sur des données réelles avant tout déploiement industriel.



//////


# Étude de conception — CantineAI

## 1. Problème et objectif

La cantine d'un lycée accueille environ 650 élèves inscrits. Chaque jour à 10 h, le gestionnaire doit commander le nombre de repas nécessaires pour le lendemain.

Actuellement, il reprend le nombre de repas servis le même jour de la semaine précédente. Cette méthode reste approximative, car la fréquentation varie selon le menu, la météo, les examens et les sorties scolaires.

L'objectif de CantineAI est de prédire le nombre de repas qui seront servis le lendemain afin de réduire le gaspillage alimentaire et d'éviter le manque de repas.

## 2. Utilisateur principal

L'utilisateur principal est le gestionnaire de la cantine. Il consulte la prédiction chaque jour avant de transmettre sa commande à la cuisine.

## 3. Décision à prendre

Le système prédit le nombre de repas à préparer pour le lendemain. Le gestionnaire utilise cette estimation pour déterminer la quantité à commander, tout en conservant la possibilité de corriger la prévision selon sa connaissance du terrain.

La prédiction doit être disponible chaque jour avant 10 h.

## 4. Données utilisées

Le dataset `cantine_repas.csv` contient 340 journées scolaires, de septembre 2024 à juin 2026.

Les variables explicatives sont :
- `jour` : jour de la semaine ;
- `inscrits` : nombre d'élèves inscrits ;
- `menu` : type de repas proposé ;
- `temperature_c` : température prévue ;
- `pluie_mm` : quantité de pluie prévue ;
- `examens` : présence d'examens ;
- `sortie_scolaire` : présence d'une sortie scolaire ;
- `veille_vacances` : indique si le lendemain est proche des vacances ;
- `repas_semaine_precedente` : nombre de repas servis le même jour de la semaine précédente.

La variable cible est `repas_servis`, qui correspond au nombre réel de repas servis.

La colonne `date` est utilisée pour trier les données chronologiquement, et non comme variable explicative.

## 5. Type de problème et approche

Il s'agit d'un problème d'apprentissage supervisé de type **régression**, car le système doit prédire une valeur numérique : le nombre de repas à préparer.

Plusieurs modèles sont comparés : une baseline, la régression Ridge, la forêt aléatoire, Gradient Boosting et les k plus proches voisins.

## 6. Méthode d'évaluation

Les données sont séparées chronologiquement : les premières journées servent à l'entraînement et les journées les plus récentes au test. Cette méthode permet de simuler une utilisation réelle, dans laquelle le modèle apprend à partir du passé pour prédire le futur.

La métrique principale est la MAE (*Mean Absolute Error*). Elle indique l'écart absolu moyen entre le nombre de repas prédit et le nombre réellement servi.

Une MAE plus faible signifie que les prédictions sont en moyenne plus proches des valeurs réelles.

## 7. Contraintes et risques

- Le nombre de repas préparés en trop entraîne un gaspillage alimentaire et un coût estimé à 15 DH par repas.
- Un nombre insuffisant de repas peut provoquer un manque de déjeuner et des réclamations.
- Les données météorologiques doivent correspondre aux prévisions disponibles au moment de la commande.
- Les informations utilisées doivent être disponibles avant 10 h.
- Les périodes de vacances et les valeurs manquantes doivent être correctement prises en compte.

## 8. Déploiement envisagé

Le modèle pourrait être exécuté chaque jour avant 10 h. Le gestionnaire saisirait ou consulterait les informations disponibles, puis le système afficherait le nombre de repas recommandé.

La décision finale resterait sous le contrôle du gestionnaire.

## 9. Critère de réussite

Le projet sera considéré comme utile si le modèle réduit l'erreur de prédiction par rapport à la méthode actuelle et contribue à limiter les repas excédentaires et les repas manquants.
