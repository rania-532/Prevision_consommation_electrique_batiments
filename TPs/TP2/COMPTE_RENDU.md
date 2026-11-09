# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** G2  **Membres :**  Imane Nadif **Date :** 02/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---:|---:|
| `POST /v1/predict` sans `load_pct` | champ manquant | 422 | 422 |
| `POST /v1/predict` avec `temperature_c: 500` | valeur hors limites | 422 | 422 |
| `POST /v1/predict` avec `temperature_c: "chaud"` | texte au lieu d'un nombre | 422 | 422 |
| `POST /v1/predict` avec le champ `unknown` | champ en trop | 422 | 422 |
| `POST /v1/inconnue` | mauvaise route | 404 | 404 |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

Non, toutes les prévisions étaient correctes. L'API a réagi comme prévu : elle a refusé les données incorrectes avec le code 422 et a retourné 404 lorsque la route demandée n'existait pas.

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
2 failed, 16 passed in 13.98s
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

Ce décorateur permet de tester plusieurs situations avec une seule fonction. Dans notre cas, les cinq scénarios sont exécutés séparément, donc pytest les considère comme cinq tests différents.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
UP017 [*] Use `datetime.UTC` alias
--> maintai\train.py:58:36
Found 1 error.
[*] 1 fixable with the `--fix` option.
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

Ruff sert à repérer les problèmes dans le code, comme les erreurs de syntaxe, les mauvaises pratiques et les problèmes de style. Pytest permet plutôt de lancer des tests pour vérifier que les fonctionnalités de l'application donnent les résultats attendus.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
===================================== 2 failed, 16 passed, 1 warning in 3.82s =====================================
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

Les deux tests sont test_missing_key_is_rejected et test_wrong_key_is_rejected. Ils reçoivent 200 au lieu de 401, car l'API n'est pas encore protégée : elle accepte toutes les requêtes.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
cle_attendue = get_settings().api_key

    if cle_attendue is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La clé API n'est pas configurée sur le serveur",
        )

    if x_api_key is None or not secrets.compare_digest(x_api_key, cle_attendue):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

2 tests échouent encore. La fonction require_api_key() existe, mais aucune route ne l'appelle : il faut l'ajouter au router avec dependencies=[Depends(require_api_key)].

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
========================================== 18 passed, 1 warning in 3.59s ==========================================
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé |200 | {"status":"ok","model_loaded":true}|
| `POST /v1/predict`, relevé normal, sans clé |401 | {"detail":"Clé API absente ou invalide"}|
| `POST /v1/predict`, relevé normal, fausse clé |401 | {"detail":"Clé API absente ou invalide"}|
| `POST /v1/predict`, relevé normal, bonne clé |200 |{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-11-02T17:33:13Z"}|
| `POST /v1/predict`, 500 °C, sans clé |401 |{"detail":"Clé API absente ou invalide"} |
| `POST /v1/predict`, 500 °C, bonne clé |422 | {"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150}}]}|

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

-Sans clé : 401. L’API vérifie d’abord qui tu es (authentification) et refuse, sans même regarder le corps.
-Avec la bonne clé : 422. Tu es authentifié, donc l’API examine le corps, et la valeur 500 dépasse la limite autorisée (150 °C) : la requête est refusée parce que les données sont invalides.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

Code 500 (erreur serveur).
Sans .env, MAINTAI_API_KEY n’est pas chargée, donc get_settings().api_key vaut None. Ton code teste ce cas en premier et lève un 500 : le problème vient du serveur mal configuré, pas de la requête du client.
Un 401 voudrait dire « ta clé est fausse ». Ici, ta clé n’est même pas comparée, car le serveur n’a rien à comparer avec.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
const reading = Object.fromEntries(FEATURES.map(f => [f, Number(document.getElementById(f).value)]));
  const url = document.getElementById("url").value;
  const key = document.getElementById("key").value;
  try {
    const res = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": key },
      body: JSON.stringify(reading),
    });
    const data = await res.json();
    if (!res.ok) {
      show("err", `Erreur ${res.status} : ${JSON.stringify(data.detail)}`);
      return;
    }
    const pct = (data.failure_probability * 100).toFixed(1);
    show(data.alert ? "alert" : "ok", `Probabilité de panne : ${pct} % (${data.alert ? "ALERTE" : "OK"})`);
  } catch (e) {
    show("err", `Impossible de joindre l'API : ${e.message}`);
  }
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé |Probabilité de panne : 94.8 % (ALERTE) |
| 500 °C, bonne clé |Erreur 422 : [{“type”:”less_than_equal”,”loc”:[“body”,”temperature_c”],”msg”:”Input should be less than or equal to 150",”input”:500,”ctx”:{“le”:150}}] |
| relevé normal, fausse clé |Erreur 401 : "Clé API absente ou invalide" |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

La page affiche : « Impossible de joindre l'API : Failed to fetch ».
La console affiche : « Access to fetch at 'http://localhost:8000/v1/predict' from origin 'http://localhost:5501' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource. »
Le port 5501 n'est pas dans MAINTAI_CORS_ORIGINS (seul 5500 est autorisé), donc l'API ne renvoie pas l'en-tête d'autorisation et le navigateur bloque la réponse.


Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

CORS est une protection appliquée par le navigateur, pas par le serveur. Le serveur répond à toutes les requêtes ; c'est le navigateur qui refuse de donner la réponse à une page venant d'une origine non autorisée. curl.exe n'est pas un navigateur : il n'a pas de notion d'origine et ne vérifie pas l'en-tête Access-Control-Allow-Origin.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

Sans `headers=HEADERS`, les quatre cas envoyés à `/v1/predict` échouent avec 401, car la clé est
vérifiée avant les données. Le cas de mauvaise route passe quand même avec 404 : aucune route
correspondante n'existe pour exécuter la dépendance d'authentification.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
============================= 23 passed in 4.36s ==============================
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?

401 Unauthorized : la clé API est absente ou invalide. Le client n'est pas authentifié.

422 Unprocessable Entity : la requête est bien reçue, mais les données envoyées ne respectent pas les règles de validation.

403 Forbidden : le client est authentifié, mais il n'a pas l'autorisation d'accéder à la ressource demandée.

2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   La clé API est une information confidentielle. Si elle est écrite directement dans le code ou publiée sur GitHub, d'autres personnes pourraient l'utiliser.

.env contient les vraies variables d'environnement, notamment la clé API. Il ne doit pas être envoyé sur Git.

.env.example contient un modèle des variables nécessaires, avec des valeurs fictives ou des exemples. Il peut être partagé sur GitHub.

C'est donc .env.example qui est commité, tandis que .env doit être ignoré par Git.

3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   La clé API est envoyée dans l'en-tête HTTP X-API-Key. Cela évite de l'exposer dans l'URL, qui peut être enregistrée dans l'historique du navigateur, les journaux du serveur ou les outils de suivi. Il faut également utiliser HTTPS pour protéger la clé pendant son transport.

4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   secrets.compare_digest compare deux chaînes de manière conçue pour limiter les attaques par analyse du temps d'exécution (timing attacks). Contrairement à une comparaison classique avec ==, il réduit les informations qu'un attaquant pourrait déduire de la durée de comparaison.

5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine est définie par trois éléments : le protocole, le nom de domaine ou l'hôte et le port.

http://localhost:5500 et http://localhost:8000 ne sont pas de la même origine, car leurs ports sont différents.

C'est pour cette raison que le navigateur applique la politique CORS et vérifie si l'origine est autorisée par l'API.

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp2` existe sur GitHub : oui 
- `git status` avant le commit : le fichier `.env` apparaissait-il ? non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ? Rania Bikikre
  …

## 9. Ce qui reste flou

Les notions principales du TP sont comprises, notamment la validation des données avec Pydantic, la sécurisation de l'API avec une clé API, les codes HTTP et le fonctionnement de CORS.
