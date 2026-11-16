# ADR 000 — Choix du modèle de prédiction des pannes

| Élément | Valeur |
|---|---|
| Date | 16/11/2026 |
| Auteur | Mahboub |
| Statut | Acceptée |

## 1. Contexte et problème

MaintAI estime la probabilité de panne à partir de quatre mesures :

- température ;
- vibration ;
- charge ;
- durée de fonctionnement.

Le système doit déclencher une alerte lorsque le risque dépasse un seuil.
Comme une panne manquée est plus coûteuse qu'une fausse alerte, le rappel doit
être privilégié, sans supprimer totalement la précision ni l'explicabilité.

## 2. Critères de décision

Le modèle retenu doit :

1. produire une probabilité de panne exploitable par l'API ;
2. favoriser un rappel élevé ;
3. rester rapide à entraîner et à servir ;
4. être explicable et maintenable ;
5. permettre l'ajustement du seuil d'alerte.

## 3. Options étudiées

| Option | Avantages | Limites |
|---|---|---|
| Régression logistique + `StandardScaler` | Rapide, explicable, probabilités directement exploitables | Représente moins bien les relations fortement non linéaires |
| Forêt aléatoire | Robuste, adaptée aux relations non linéaires | Plus lourde et moins explicable |

## 4. Décision

Nous retenons une **régression logistique dans un pipeline avec
`StandardScaler`**.

Le seuil d'alerte reste configurable avec `MAINTAI_THRESHOLD`. Il peut être
abaissé lorsque la priorité est de détecter davantage de pannes. Cette option
offre le meilleur compromis actuel entre rappel, précision, rapidité et
maintenabilité pour les données du projet.

## 5. Conséquences

### Conséquences positives

- modèle simple à entraîner, versionner avec MLflow et servir par l'API ;
- probabilités directement utilisables pour appliquer un seuil métier ;
- coefficients permettant d'analyser l'influence des capteurs ;
- maintenance et évolution facilitées.

### Points de vigilance

- surveiller le rappel et la précision à chaque nouvelle version des données ;
- réévaluer le modèle sur des données réelles ;
- envisager une forêt aléatoire si les relations entre variables deviennent
  fortement non linéaires ;
- documenter chaque changement du seuil et ses effets sur les alertes.
