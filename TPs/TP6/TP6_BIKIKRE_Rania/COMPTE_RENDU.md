# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Membres :** BIKIKRE Rania ·  **Date :**23/11/2026



---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :

```
Docker version 29.2.1, build a5c7197

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/



```

Dernière ligne de `python -m pytest` après la mise en place :

```
=========== 5 failed, 33 passed, 4 warnings in 32.59s ============
```

## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?
   Une image Docker est un modèle contenant le code, Python et les bibliothèques nécessaires à l'application. Un conteneur est une instance de cette image en cours d'exécution.
2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?
   Pour profiter du cache Docker : les dépendances changent moins souvent que le code. Docker peut donc réutiliser la couche d'installation lorsque seul le code change.
3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?
   Pour fixer précisément la version de la bibliothèque et garantir un environnement reproductible, sans risque d'installer une version différente.
4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?
   Ce sont des outils destinés principalement au suivi des expériences, à la gestion des données et aux tests pendant le développement. Ils ne sont pas nécessaires à l'exécution de l'API.

## 3. Sprint 1 : le Dockerfile

Votre `Dockerfile` :

```dockerfile
# Image de MaintAI : le code et ses bibliothèques, sans les données ni le modèle.
# Construire : docker build -t maintai:0.4.0 .

# Image de base : Python 3.11 version légère
FROM python:3.11-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier uniquement le fichier des dépendances
COPY requirements-docker.txt .

# Installer les bibliothèques nécessaires
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copier le code de l'application
COPY maintai ./maintai
COPY ui ./ui

# Définir les chemins des données et du modèle
ENV MAINTAI_MODELS_DIR=/app/models
ENV MAINTAI_DATA_PATH=/app/data/sensors.csv

# Port utilisé par l'API
EXPOSE 8000

# Démarrer l'API avec Uvicorn
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

```

| Build | Durée | Taille de l'image (`docker images`) |
|---|---|---|
| premier build | 139,3 s	| 1,13 Go
Build Compose	3,7 s	1,13 Go|
| après une modification de `maintai/predict.py` |3,7 s | 1,13 Go|

Que signifie `CACHED` dans le journal du second build ?

…

## 4. Sprint 1 : lancer un conteneur

Votre commande `docker run` :

```
docker run -d --name maintai-api -p 8000:8000 --env-file .env -v "${PWD}/models:/app/models:ro" maintai:0.4.0
```

| Essai | Réponse |
|---|---|
| `GET /health` | {
  "status": "string",
  "model_loaded": true
}|
| `POST /v1/predict` sans clé |401 Error: Unauthorized |
| `POST /v1/predict` avec la clé |200 Response body |


**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

docker run -d --name maintai-api -p 8000:8000 --env-file .env maintai:0.4.0
{"status":"ok","model_loaded":false}
503
Error: Service Unavailable
{
  "detail": "Modèle non chargé : lancez python -m maintai.train puis redémarrez l'API"
}
Cela s'explique par l'absence du volume qui permet de monter le dossier models/ du PC dans le conteneur. L'API démarre, mais elle ne trouve pas le modèle nécessaire pour effectuer les prédictions.

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?

docker run -d --name test -p 8002:8000 maintai:0.4.0 uvicorn maintai.api.main:app --host 127.0.0.1 --port 8000
This page isn’t working
localhost didn’t send any data.
ERR_EMPTY_RESPONSE
 docker logs test
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

Les logs indiquent que Uvicorn écoute sur http://127.0.0.1:8000. Pourtant, l'accès à http://localhost:8002/health depuis le navigateur échoue (ERR_EMPTY_RESPONSE). Cela s'explique par le fait que 127.0.0.1 limite l'écoute à l'interface locale du conteneur. Pour que le port publié par Docker soit accessible depuis l'extérieur du conteneur, l'application doit écouter sur 0.0.0.0.

## 5. Sprint 2 : Docker Compose

Votre `compose.yaml` :

```yaml
# MaintAI en deux conteneurs : l'API et l'interface Streamlit.
# Lancer : docker compose up --build
# Arrêter : docker compose down

services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro

  ui:
    image: maintai:0.4.0
    command:
      - python
      - -m
      - streamlit
      - run
      - ui/app.py
      - --server.address=0.0.0.0
      - --server.port=8501
      - --server.headless=true
    environment:
      MAINTAI_API_URL: http://api:8000
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data:ro
    depends_on:
      - api

```

Sortie de `docker compose ps` :

```
NAME                      IMAGE           COMMAND                  SERVICE   CREATED          STATUS          PORTS
tp6_bikikre_rania-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       13 minutes ago   Up 13 minutes   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
tp6_bikikre_rania-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        13 minutes ago   Up 13 minutes   0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
```

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

L'URL affichée est http://api:8000. Elle provient de la variable d'environnement MAINTAI_API_URL, définie dans compose.yaml pour le service ui. Le fichier ui/app.py récupère cette valeur avec os.getenv().

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?

```
Avec api :
{"status":"ok","model_loaded":true}

Avec localhost :
httpx.ConnectError: [Errno 111] Connection refused
```

Dans le conteneur UI, localhost désigne le conteneur UI lui-même et non le conteneur API. La communication entre les deux conteneurs doit donc utiliser le nom du service Docker Compose api.

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
======================== 38 passed, 4 warnings in 34.60s ========================
```

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumez ici votre décision en deux phrases :

Nous avons choisi de conserver le modèle à l'extérieur de l'image Docker et de le fournir au conteneur API avec un volume en lecture seule (`./models:/app/models:ro`). Cette solution permet de garder une image plus légère et de mettre à jour le modèle sans reconstruire l'image, à condition que le dossier `models/` soit disponible au lancement.

## 7. Questions de compréhension
1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ?
L'image contient Python 3.11, les bibliothèques nécessaires et le code de l'application (maintai/ et ui/), copiés avec les instructions du Dockerfile. Au lancement, le modèle et les données sont fournis par des volumes Docker, tandis que les variables d'environnement sont transmises par env_file et environment dans compose.yaml.

2. Pourquoi la clé API n'est-elle jamais dans l'image ?
Pour éviter d'intégrer une information confidentielle dans l'image Docker. La clé est injectée au lancement à partir du fichier .env, ce qui permet de la modifier sans reconstruire l'image.

3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?
Docker permet de livrer l'application dans un environnement reproductible contenant Python, ses dépendances et son code. Il facilite également son déploiement grâce aux conteneurs, aux volumes, aux ports et à la communication entre les services.

## 8. Le rendu Git

- Lien de la pull request : (https://github.com/rania-532/Prevision_consommation_electrique_batiments/pull/38)
- Le tag `tp6` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `models/` ou `data/*.csv` apparaissaient-ils ?  non

## 9. Ce qui reste flou

…
