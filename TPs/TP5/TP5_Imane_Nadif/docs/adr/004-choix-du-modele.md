# ADR 004 : choix du modèle et du seuil d'alerte

Date : 16/11/2026 · Auteurs : Imane Nadif

## Contexte
MaintAI doit prédire les pannes à partir de relevés de capteurs. Une panne manquée coûte plus cher qu'une fausse alerte : il faut privilégier le recall, et pouvoir justifier le choix à partir des runs MLflow et de la version des données utilisée.

## Options étudiées
Quatre entraînements sur la v1 des données (5000 relevés) :
1. Régression logistique, réglages par défaut (seuil 0.3) : recall 0.75, precision 0.622, accuracy 0.904.
2. Régression logistique, `--C 0.01` : recall 0.691, precision 0.653, accuracy 0.908. Meilleure precision, mais moins de pannes détectées.
3. Régression logistique, `--threshold 0.2` : recall 0.838, precision 0.543, accuracy 0.882. Le plus de pannes détectées, au prix de plus de fausses alertes.
4. Forêt aléatoire (`--model forest`) : recall 0.728, precision 0.562, accuracy 0.886. Pas meilleure que la régression logistique ici.

## Décision
Régression logistique avec un seuil de 0.2. Elle a le meilleur recall (0.838), ce qui répond à la contrainte principale : ne pas manquer de pannes. L'accuracy n'est pas un bon critère ici, car seulement 13.6 % des relevés sont des pannes.

Run MLflow : `06ae2b65adf044e4970bdb6008cec178` · data_md5 : `73e0b7cb3c6f795c70c3ddf970b99c15` (données v1, commit `a5ba1ee`)

## Conséquences
On accepte plus de fausses alertes (precision 0.543 contre 0.622 par défaut), donc plus d'inspections inutiles. Il faudra surveiller le nombre de fausses alertes en usage réel, et ré-évaluer le seuil si les données dérivent. Chaque modèle étant relié à ses données par `data_md5`, on pourra refaire cette comparaison sur une nouvelle version des données, en gardant en tête que des jeux de test différents ne se comparent pas directement.