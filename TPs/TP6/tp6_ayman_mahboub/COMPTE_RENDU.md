# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** G2  ·  **Membres :** MAHBOUB AYMAN  ·  **Date :** 23/11/2026 à 12h00

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP6.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :

```
Hello Docker!

Client:
 Version:           29.9.3
Server: Docker Desktop 4.99.0 (245822)
 Engine:
  Version:          29.9.3
```

Dernière ligne de `python -m pytest` après la mise en place :

```
2 failed, 36 passed, 4 warnings in 120.11s (0:02:00)
```

(Les 2 échecs venaient de `tests/test_package.py` : le package n'était pas encore installé. Ils passent après `pip install -e .`.)

## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?
   Une image est un modèle figé, en lecture seule : un système de fichiers, les bibliothèques, le code et une commande de démarrage. Un conteneur est une instance de cette image qui s'exécute, avec son propre processus, son réseau et une couche modifiable. Une même image peut lancer plusieurs conteneurs : ici, l'API et l'interface.
2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?
   Docker met chaque instruction en cache et réutilise le cache tant que ce qui a été copié n'a pas changé. Les bibliothèques changent rarement et le code souvent. En installant les bibliothèques d'abord, une modification du code n'invalide que les étapes `COPY maintai` et `COPY ui` : le `pip install` (environ 2 min) reste en cache.
3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?
   Le modèle `model.joblib` a été sérialisé avec scikit-learn 1.8.0. Avec une autre version, le chargement peut échouer ou donner des prédictions différentes. Figer la version rend aussi le build reproductible : le même fichier donne la même image aujourd'hui et dans six mois.
4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?
   L'image sert à servir le modèle (API et interface), pas à l'entraîner, à versionner les données ni à tester. Ces outils alourdiraient l'image, ralentiraient le build et ajouteraient de la surface d'attaque sans servir en production.

## 3. Sprint 1 : le Dockerfile

Votre `Dockerfile` :

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY maintai ./maintai
COPY ui ./ui

ENV MAINTAI_MODELS_DIR=/app/models \
    MAINTAI_DATA_PATH=/app/data/sensors.csv

EXPOSE 8000
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Build | Durée | Taille de l'image (`docker images`) |
|---|---|---|
| premier build (`--no-cache`) | 123 s | 1,13 Go sur disque (259 Mo de contenu) |
| après une modification de `maintai/predict.py` | 9 s | 1,13 Go sur disque (259 Mo de contenu) |

Que signifie `CACHED` dans le journal du second build ?

`CACHED` signifie que Docker a réutilisé la couche déjà construite au lieu de réexécuter l'instruction. Au second build, `WORKDIR`, `COPY requirements-docker.txt` et `RUN pip install` sont `CACHED` parce que rien n'a changé avant eux. Seuls `COPY maintai` et `COPY ui` sont refaits, puisque `predict.py` a changé. C'est pour ça que le build passe de 123 s à 9 s.

```
#6 [2/6] WORKDIR /app                                                CACHED
#7 [3/6] COPY requirements-docker.txt .                              CACHED
#8 [4/6] RUN pip install --no-cache-dir -r requirements-docker.txt   CACHED
#9 [5/6] COPY maintai ./maintai                                      DONE 5.6s
#10 [6/6] COPY ui ./ui                                               DONE 0.1s
```

## 4. Sprint 1 : lancer un conteneur

Votre commande `docker run` :

```
docker run -d --name maintai-api -p 8000:8000 --env-file .env -v "%cd%\models:/app/models:ro" maintai:0.4.0
```

(Pour les essais, le port 8000 étant déjà occupé par la pile Compose, le conteneur a été publié sur `-p 8003:8000`.)

| Essai | Réponse |
|---|---|
| `GET /health` | `200` `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` sans clé | `401` `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict` avec la clé | `200` `{"failure_probability":0.9475,"alert":true,"threshold":0.3,"model_version":"2026-11-23T11:04:41Z"}` |

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

`/health` répond `{"status":"ok","model_loaded":false}` et `/v1/predict` répond `503` `{"detail":"Modèle non chargé : lancez python -m maintai.train puis redémarrez l'API"}`. L'image ne contient pas le modèle (`models/` est dans `.dockerignore`). Sans le volume, `/app/models` est vide, le `FileNotFoundError` est rattrapé au démarrage et l'API tourne sans modèle. Le conteneur paraît sain alors qu'il ne peut rien prédire.

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?

`docker logs test` affiche un démarrage normal : `Uvicorn running on http://127.0.0.1:8000`. En revanche, `curl http://localhost:8002/health` échoue, avec une connexion coupée et aucune réponse (`Empty reply from server`). Dans un conteneur, `127.0.0.1` désigne le conteneur lui-même. Les requêtes publiées par `-p 8002:8000` arrivent par l'interface réseau du conteneur, pas par sa boucle locale, donc personne ne les écoute. Il faut `--host 0.0.0.0` pour écouter sur toutes les interfaces.

## 5. Sprint 2 : Docker Compose

Votre `compose.yaml` :

```yaml
services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env                     # MAINTAI_API_KEY, comme au TP2
    ports:
      - "8000:8000"                    # PC:conteneur
    volumes:
      - ./models:/app/models:ro        # le modèle vient du PC, en lecture seule

  ui:
    image: maintai:0.4.0               # la même image, une autre commande
    command: ["python", "-m", "streamlit", "run", "ui/app.py",
              "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
    environment:
      MAINTAI_API_URL: http://api:8000 # l'API vue depuis ce conteneur : le nom du service
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data:ro            # les données du PC, en lecture seule
    depends_on:
      - api
```

Sortie de `docker compose ps` :

```
NAME        IMAGE           COMMAND                  SERVICE   CREATED          STATUS         PORTS
tp6-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       13 seconds ago   Up 9 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        12 seconds ago   Up 9 seconds   0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
```

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

La barre latérale affiche `http://api:8000`. Cette valeur vient de la variable `MAINTAI_API_URL` définie dans `environment:` du service `ui` de `compose.yaml`, que `ui/app.py` lit avec `os.getenv("MAINTAI_API_URL", "http://localhost:8000")`. Sans la variable, sur le PC, la valeur par défaut reste `http://localhost:8000`.

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?

```
> docker compose exec ui python -c "import httpx; print(httpx.get('http://api:8000/health').text)"
{"status":"ok","model_loaded":true}

> docker compose exec ui python -c "import httpx; print(httpx.get('http://localhost:8000/health').text)"
httpx.ConnectError: [Errno 111] Connection refused
```

Chaque conteneur a sa propre pile réseau. Dans le conteneur `ui`, `localhost` désigne le conteneur `ui` lui-même, où rien n'écoute sur le port 8000 : la connexion est refusée. Compose crée un réseau commun dans lequel chaque service est joignable par son nom, et le DNS interne traduit `api` en adresse du conteneur de l'API.

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
38 passed, 4 warnings in 45.52s
```

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumez ici votre décision en deux phrases :

L'image `maintai:0.4.0` contient seulement le code et les bibliothèques aux versions figées (dont scikit-learn 1.8.0), sur une base `python:3.11-slim`. Le modèle, les données et la clé API arrivent au lancement par des volumes en lecture seule et par `.env`, ce qui permet de changer de modèle sans reconstruire l'image et de ne jamais y enfermer un secret.

## 7. Questions de compréhension

1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.
   - **Dans l'image** : Python 3.11 (`FROM python:3.11-slim`), les bibliothèques (`COPY requirements-docker.txt` + `RUN pip install`), le code `maintai/` et `ui/` (`COPY`), les chemins par défaut (`ENV`) et la commande de démarrage (`CMD`).
   - **Au lancement** : le modèle (volume `./models:/app/models:ro`), les données (volume `./data:/app/data:ro`), la clé API (`--env-file .env` / `env_file:`), l'adresse de l'API pour l'interface (`environment: MAINTAI_API_URL`), les ports (`-p` / `ports:`) et la commande de l'interface (`command:`).
2. Pourquoi la clé API n'est-elle jamais dans l'image ?
   Une image se partage, se pousse sur un registre et se copie, et chacune de ses couches peut être inspectée (`docker history`, extraction des fichiers). Une clé qu'on y mettrait serait diffusée à tous ceux qui ont l'image et ne pourrait plus en être retirée. La clé change selon l'environnement : elle est donc injectée au lancement, et `.env` est exclu par `.dockerignore` et `.gitignore`.
3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?
   Au TP4 on livrait le code et des versions figées (wheel + `requirements.txt`), et au TP5 le modèle traçable et ses données versionnées (MLflow, DVC). Docker ajoute l'environnement d'exécution complet : le système et la version exacte de Python, les bibliothèques déjà installées et la commande de démarrage, le tout dans un artefact unique, `maintai:0.4.0`, qui tourne pareil sur tout hôte Docker. Docker ajoute aussi la façon d'assembler les services (`compose.yaml` : ports, volumes, réseau, variables).

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp6` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `models/` ou `data/*.csv` apparaissaient-ils ? non (ils sont dans `.gitignore`)

## 9. Ce qui reste flou

- L'image pèse 1,13 Go sur disque pour 259 Mo de contenu. Il faudrait voir comment la réduire (build multi-étapes, image plus légère).
- `depends_on` attend que le conteneur de l'API démarre, pas qu'il soit prêt. Il faudrait voir comment ajouter un `healthcheck` pour que l'interface attende un `/health` valide.
