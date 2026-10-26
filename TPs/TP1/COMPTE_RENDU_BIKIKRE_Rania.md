# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Membre :** Bikikre Rania  ·  **Date :** 26/10/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :
```
python -m pytest
========================================================== test session starts ===========================================================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\andal\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 13 items                                                                                                                        

tests\test_api.py .FF..F.                                                                                                           [ 53%]
tests\test_data.py ...                                                                                                              [ 76%]
tests\test_train.py ...                                                                                                             [100%]

================================================================ FAILURES ================================================================
____________________________________________________ test_predict_returns_probability ____________________________________________________

client = <starlette.testclient.TestClient object at 0x00000294594E3C50>

    def test_predict_returns_probability(client):
        r = client.post("/v1/predict", json=VALID, headers=HEADERS)
>       assert r.status_code == 200
E       assert 422 == 200
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests\test_api.py:18: AssertionError
__________________________________________________ test_high_risk_reading_raises_alert ___________________________________________________

client = <starlette.testclient.TestClient object at 0x0000029459630910>

    def test_high_risk_reading_raises_alert(client):
        r = client.post("/v1/predict", json=HIGH_RISK, headers=HEADERS)
>       assert r.json()["alert"] is True
               ^^^^^^^^^^^^^^^^^
E       KeyError: 'alert'

tests\test_api.py:26: KeyError
______________________________________________________ test_503_when_model_missing _______________________________________________________

settings_env = WindowsPath('C:/Users/andal/AppData/Local/Temp/pytest-of-andal/pytest-4/maintai0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000002945963F150>
tmp_path = WindowsPath('C:/Users/andal/AppData/Local/Temp/pytest-of-andal/pytest-4/test_503_when_model_missing0')

    def test_503_when_model_missing(settings_env, monkeypatch, tmp_path):
        monkeypatch.setenv("MAINTAI_MODELS_DIR", str(tmp_path / "empty"))
        with TestClient(app) as c:
            r = c.post("/v1/predict", json=VALID, headers=HEADERS)
>       assert r.status_code == 503
E       assert 422 == 503
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests\test_api.py:44: AssertionError
============================================================ warnings summary ============================================================
..\..\S3_projet_a_completer\projet_a_completer\.venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\andal\Downloads\S3_projet_a_completer\projet_a_completer\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================================================== short test summary info =========================================================
FAILED tests/test_api.py::test_predict_returns_probability - assert 422 == 200
FAILED tests/test_api.py::test_high_risk_reading_raises_alert - KeyError: 'alert'
FAILED tests/test_api.py::test_503_when_model_missing - assert 422 == 503
================================================ 3 failed, 10 passed, 1 warning in 3.46s =================================================
(.venv) PS C:\Users\andal\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1> 
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

Les 4 tests qui passent sont ceux qui n'ont pas besoin de `predict()` : `test_health`, `test_out_of_range_value_is_rejected`, `test_missing_field_is_rejected` et `test_openapi_documents_predict`. Les trois autres (`test_predict_returns_probability`, `test_high_risk_reading_raises_alert`, `test_503_when_model_missing`) échouent au départ.

Les deux tests « 422 » passent pour une mauvaise raison : `SensorReading` ne déclare encore aucun champ (juste `pass`) et `extra="forbid"` refuse tout champ inconnu. Tout corps contenant une donnée est donc rejeté en 422, même un relevé valide. Le 422 ne vient pas des bornes voulues, mais du schéma vide.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | float | -40 | 150 | Plage de fonctionnement des capteurs industriels courants ; au-delà, le capteur est défaillant ou la valeur est absurde. |
| `vibration_mm_s` | float | 0 | 50 | Une vitesse de vibration est positive ; 50 mm/s dépasse largement les seuils de danger d'une machine, donc c'est une erreur de mesure. |
| `load_pct` | float | 0 | 100 | C'est un pourcentage de la charge nominale. |
| `runtime_hours` | float | 0 | 200000 | Un compteur d'heures n'est jamais négatif ; 200 000 h font environ 23 ans de fonctionnement continu, au-delà de la vie d'une machine. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\andal\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 13 items

tests\test_api.py .FF..F.                                                [ 53%]
tests\test_data.py ...                                                   [ 76%]
tests\test_train.py ...                                                  [100%]

     3 failed, 10 passed, 1 warning in 5.85s

```
Les tests qui échouent encore le font à cause de `NotImplementedError` dans `predict()`. C'est un bon signe : la validation fonctionne (un relevé valide passe le schéma, les cas 422 sont refusés pour la bonne raison) et il ne manque que la logique de prédiction.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    return predictor.predict(reading.model_dump())
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

Un 500 signale un bug inattendu du serveur. Ici l'absence du modèle est une situation connue et prévue (il n'a pas encore été entraîné) : le service est temporairement indisponible, ce que dit exactement le 503. Le client comprend que sa requête est correcte et qu'il peut réessayer plus tard. Nous l'avons observé avant l'entraînement : code 503 avec `{"detail": "Modèle non chargé"}`.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Lire et désérialiser le fichier du modèle sur le disque est lent. Le refaire à chaque requête allongerait fortement les temps de réponse et chargerait le serveur. Chargé une fois au démarrage (par le `lifespan`), le modèle reste en mémoire dans `state` et toutes les requêtes le réutilisent.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :
```
 python -m pytest
========================================================== test session starts ===========================================================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\andal\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 13 items                                                                                                                        

tests\test_api.py .......                                                                                                           [ 53%]
tests\test_data.py ...                                                                                                              [ 76%]
tests\test_train.py ...                                                                                                             [100%]

============================================================ warnings summary ============================================================
..\..\S3_projet_a_completer\projet_a_completer\.venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\andal\Downloads\S3_projet_a_completer\projet_a_completer\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
===================================================== 13 passed, 1 warning in 3.47s ======================================================
(.venv) PS C:\Users\andal\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1> 
```
## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | 200 | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200 | `{"failure_probability": 0.9553, "alert": true, "threshold": 0.3, "model_version": "2026-10-26T20:01:26Z"}` |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail": [{"type": "less_than_equal", "loc": ["body", "temperature_c"], "msg": "Input should be less than or equal to 150", "input": 500, "ctx": {"le": 150}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail": "Not Found"}` |

Dans `/docs`, où voit-on les bornes que vous avez choisies ?

Dans la route `POST /v1/predict`, section « Request body », onglet **Schema** (à côté de « Example Value ») : chaque champ y affiche son minimum, son maximum et sa description. On les retrouve aussi en bas de page, dans la section « Schemas ».

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?

REST est un style de conception d’API web qui utilise des routes, des méthodes HTTP comme GET et POST, et des codes de statut. FastAPI est un framework Python qui permet de créer des API web.

2. Le schéma Pydantic sert à trois choses. Lesquelles ?
- Valider les données reçues : types, valeurs minimales et maximales, champs autorisés.
- Convertir les données JSON en objets Python typés.
- Générer automatiquement la documentation de l’API dans /docs.
3. Dans http://localhost:8000/v1/predict, que désignent localhost, 8000 et /v1/predict ?
- localhost : l’ordinateur local sur lequel le serveur fonctionne.
- 8000 : le port utilisé par le serveur Uvicorn.
- /v1/predict : la route de l’API qui permet d’effectuer une prédiction.
4. Pourquoi /v1 dans l’adresse ?

/v1 indique la version 1 de l’API. Cela permet de créer une nouvelle version, comme /v2, sans perturber les utilisateurs de l’ancienne version.

5. Dans la commande uvicorn maintai.api.main:app, que désignent maintai.api.main et app ?

maintai.api.main désigne le module Python correspondant au fichier maintai/api/main.py. app désigne l’objet FastAPI créé dans ce fichier, que Uvicorn utilise pour démarrer le serveur.

## 7. Le rendu Git

- Lien de la pull request : [À COMPLÉTER]
- Le tag `tp1` existe sur GitHub : [oui / non]
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  Imane Nadif 

## 8. Ce qui reste flou

 Le rôle exact de `lifespan` reste un peu flou. Je comprends qu’il permet d’exécuter du code au démarrage et à l’arrêt de l’API, notamment de charger le modèle de prédiction une seule fois au démarrage afin de le réutiliser pour les requêtes suivantes.