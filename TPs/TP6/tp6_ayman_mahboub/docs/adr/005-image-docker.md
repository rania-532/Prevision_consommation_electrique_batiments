# ADR 005 : une image Docker qui contient le code, pas le modèle ni les données

Date : 23/11/2026 à 12h27 · Auteurs : [noms]

## Contexte

MaintAI doit tourner à l'identique sur n'importe quelle machine, avec les versions exactes des bibliothèques qui ont écrit le modèle (scikit-learn 1.8.0). Le modèle et les données changent à chaque entraînement (TP5), et la clé API est un secret qui ne doit jamais être diffusé.

## Options étudiées

1. **Tout dans l'image (code, bibliothèques, modèle, données)** : une seule pièce à livrer. En contrepartie, l'image est reconstruite à chaque nouveau modèle, elle est plus lourde, et un secret ou des données pourraient fuiter avec elle.
2. **Image avec le code et les bibliothèques seulement ; le modèle, les données et la clé arrivent au lancement (volumes, `--env-file`)** : l'image est stable et réutilisable, et on change de modèle sans la reconstruire. Le lanceur doit en revanche fournir le bon dossier `models/` et un fichier `.env`.

## Décision

Option 2. L'image `maintai:0.4.0` (`python:3.11-slim`) contient `maintai/`, `ui/` et les bibliothèques figées de `requirements-docker.txt`. Le modèle est monté en lecture seule (`./models:/app/models:ro`) et la clé est lue depuis `.env`. Une même image sert l'API et l'interface Streamlit avec deux commandes différentes, orchestrées par `compose.yaml`.

## Conséquences

- Un nouveau modèle ne demande qu'un redémarrage, pas de nouveau build. Grâce au cache, un changement de code se reconstruit en quelques secondes (bibliothèques installées avant `COPY maintai`).
- Aucun secret ni aucune donnée dans l'image : c'est garanti par `.dockerignore` et vérifié par `tests/test_docker.py`.
- À surveiller : sans le volume `models/`, l'API démarre mais répond 503. Il faut aussi garder `requirements-docker.txt` aligné sur `requirements.txt`, sinon le modèle risque d'être incompatible avec les bibliothèques. L'image pèse 1,13 Go sur le disque.
