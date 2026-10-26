# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** 4  
**Membres :** Farah Otarid, Rania Bikikre, Imane Nadif, Amine Erradha, Ayman Mahboub  
**Date :** 26/10/2026

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place :

```text
À compléter avec la sortie réelle du terminal.
```

Dans `tests/test_api.py`, quatre tests sur sept passent déjà alors que rien n'est écrit. Les noms exacts sont à relever dans le fichier de tests.

Les deux tests qui attendent un code HTTP 422 passent pour une mauvaise raison : le schéma `SensorReading` contient `extra="forbid"`, mais les quatre champs attendus ne sont pas encore déclarés. Pydantic considère donc `temperature_c`, `vibration_mm_s`, `load_pct` et `runtime_hours` comme des champs supplémentaires interdits.

La requête est rejetée, mais pas parce que les valeurs dépassent les limites prévues. Après la déclaration des champs, ces tests doivent vérifier la véritable validation des données.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique |
|---|---|---:|---:|---|
| `temperature_c` | `float` | -50 | 200 | Plage générale plausible pour la température d'une machine industrielle. |
| `vibration_mm_s` | `float` | 0 | 100 | Une vibration ne peut pas être négative ; 100 mm/s constitue une limite supérieure large pour ce TP. |
| `load_pct` | `float` | 0 | 100 | La charge est exprimée en pourcentage et ne peut pas être négative ni dépasser 100 %. |
| `runtime_hours` | `float` | 0 | 200000 | Le nombre d'heures de fonctionnement est positif ou nul ; 200 000 heures représentent une durée de fonctionnement cumulée élevée. |

Après avoir écrit `schemas.py` seul, résultat de `python -m pytest` :

```text
À compléter avec la sortie réelle du terminal.
```

Le nombre de tests réussis et échoués dépend du code de test fourni. Les tests de prédiction peuvent encore échouer parce que la fonction `predict()` de `main.py` n'est pas implémentée.

Si les tests de validation passent désormais et que les tests de prédiction échouent avec une erreur liée à `NotImplementedError`, c'est un bon signe : le schéma valide correctement les entrées, et les tests atteignent maintenant la partie de l'API qui reste à développer.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Notre code :

```python
@router.post("/predict", response_model=PredictionOut)
def predict(reading: SensorReading) -> PredictionOut:
    predictor = state.get("predictor")

    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Le modèle de prédiction n'est pas disponible.",
        )

    return predictor.predict(reading.model_dump())
```

**Pourquoi répondre 503 et pas 500 quand le modèle manque ?**

Le code HTTP 503 signifie que le service est temporairement indisponible. Ici, l'API fonctionne, mais le modèle nécessaire à la prédiction n'est pas disponible. Le code 500 correspond plutôt à une erreur interne inattendue du serveur.

**Pourquoi le modèle est-il chargé une seule fois, au démarrage, et pas à chaque requête ?**

Le modèle est chargé dans la fonction `lifespan`, au démarrage de l'application. Il reste ensuite disponible dans `state` pour toutes les requêtes. Cela évite de recharger le fichier du modèle à chaque appel, réduit le temps de réponse et limite les opérations inutiles.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```text
À compléter après l'implémentation de schemas.py et main.py.
```

Commande utilisée :

```bash
python -m pytest
```

## 5. L'API en marche

Après l'exécution des commandes :

```bash
python -m maintai.dataset
python -m maintai.train
uvicorn maintai.api.main:app --reload
```

Résultats à compléter après les requêtes :

| Requête | Code obtenu | Réponse (corps JSON) |
|---|---|---|
| `GET /health` | À vérifier | `{"status":"ok","model_loaded":true}` si le modèle a été chargé correctement. |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | À vérifier | À copier depuis la réponse réelle de l'API. |
| `POST /v1/predict` avec une température de 500 | 422 attendu | Réponse d'erreur de validation Pydantic indiquant que la température dépasse la limite autorisée. |
| `POST /v1/predicte` | 404 attendu | Réponse indiquant que la ressource demandée n'existe pas. |

**Dans `/docs`, où voit-on les bornes choisies ?**

Dans la documentation interactive Swagger, accessible à l'adresse `http://localhost:8000/docs`, on ouvre le schéma de la requête `POST /v1/predict`. Les bornes apparaissent dans les paramètres du modèle `SensorReading`, notamment dans les champs `minimum` et `maximum`, ainsi que dans les détails du schéma.

## 6. Questions de compréhension

**1. REST et FastAPI : quelle est la différence ?**

REST est un style architectural utilisé pour concevoir des API web. FastAPI est un framework Python qui permet de développer des API, notamment en respectant les principes REST.

**2. Le schéma Pydantic sert à trois choses. Lesquelles ?**

- Valider les données reçues et vérifier leurs types et leurs limites.
- Refuser les champs inconnus lorsque `extra="forbid"` est activé.
- Décrire la structure des données et contribuer à la génération automatique de la documentation OpenAPI/Swagger.

**3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?**

- `localhost` : la machine locale sur laquelle le serveur fonctionne.
- `8000` : le port sur lequel le serveur écoute par défaut avec Uvicorn.
- `/v1/predict` : le chemin de l'endpoint de prédiction, où `v1` désigne la version 1 de l'API.

**4. Pourquoi `/v1` dans l'adresse ?**

Le préfixe `/v1` permet de versionner l'API. Si une nouvelle version incompatible est développée, elle pourra être exposée sous `/v2` sans nécessairement casser les clients utilisant `/v1`.

**5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?**

`maintai.api.main` désigne le module Python contenant le code de l'API. `app` est la variable de ce module qui contient l'instance de l'application FastAPI à lancer.

## 7. Le rendu Git

- **Lien de la pull request :** à compléter avec le lien GitHub réel.
- **Le tag `tp1` existe sur GitHub :** oui / non, à vérifier.
- **Qui a relu la pull request, et quel commentaire a-t-il laissé ?** à compléter après la revue par un membre du groupe.

## 8. Ce qui reste flou

À compléter par les membres du groupe après le TP, en indiquant les notions qui restent à clarifier : validation Pydantic, codes HTTP, fonctionnement de FastAPI, chargement du modèle ou workflow Git avec les pull requests.