# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :**G2  ·  **Membres :** Imane Nadif  ·  **Date :**09/11/2026
> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
5 failed, 18 passed, 1 warning in 5.02s
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

- tests/test_client.py :
  - test_client_returns_prediction : NotImplementedError
  - test_client_wrong_key_raises_401 : NotImplementedError
  - test_client_bad_reading_raises_422 : NotImplementedError
- tests/test_ui.py :
  - test_ui_shows_the_data : IndexError: list index out of range
  - test_ui_shows_the_prediction : IndexError: list index out of range

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```
ModuleNotFoundError: No module named 'maintai'
```

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

La commande python -m streamlit permet de lancer Streamlit en utilisant directement l’interpréteur Python de l’environnement virtuel actif. Cela garantit l’utilisation des dépendances installées dans cet environnement et permet de résoudre correctement le module maintai.

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
c1, c2, c3 = st.columns(3)
c1.metric("Relevés", len(df))
c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

variable = st.selectbox("Variable", FEATURES)
tranches = pd.cut(df[variable], bins=10)
taux = df.groupby(tranches, observed=True).failure.mean()
taux.index = [round(i.mid) for i in taux.index]
st.bar_chart(taux)

nuage = df.assign(panne=df.failure.map({0: "non", 1: "oui"}))
st.scatter_chart(nuage, x="temperature_c", y="vibration_mm_s", color="panne")
```

| Indicateur | Valeur |
|---|---:|
| Nombre de relevés | 5000 |
| Taux de panne | 13,6 % |
| Température moyenne | 59,8 °C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente avec le niveau de vibration.

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

Dans le terminal, « relance » s'affiche à chaque action sur un widget (hors formulaire). Cela montre que Streamlit exécute de nouveau tout le script, de la première à la dernière ligne, à chaque interaction. Dans le formulaire de l'onglet « Prédiction », les curseurs ne relancent rien : seul le bouton « Prédire » le fait.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

Sans lui, le CSV serait relu à chaque relance du script, donc à chaque clic. Avec lui, il est lu une seule fois, puis le même tableau est renvoyé depuis la mémoire. La page reste rapide.

## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
    headers = {"X-API-Key": self.api_key} if self.api_key else {}
    r = self.http.post("/v1/predict", json=reading, headers=headers)
    if r.status_code != 200:
        raise APIError(r.status_code, r.json().get("detail"))
    return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
======================== 23 passed, 1 warning in 7.75s =========================
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | Probabilité de panne : 95 %, message rouge « ALERTE : au-dessus du seuil 0.3 » |
| valeurs par défaut, fausse clé | Avertissement jaune : « Erreur 401 : ... » (message de l'API) |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | Message rouge : « API injoignable : uvicorn est-il lancé ? » |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

Parce que la requête est envoyée par Python depuis le serveur Streamlit vers FastAPI. Il ne s'agit pas d'une requête directe du navigateur : la politique CORS ne s'applique donc pas.


## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?
   Dans le TP2, c'est le navigateur : le `fetch` JavaScript s'exécute dans le navigateur. Dans Streamlit, c'est le serveur Streamlit en Python, par `MaintaiClient` ; le navigateur affiche seulement la page.
2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?
   Les tests donnent à `MaintaiClient` le client de test de FastAPI (`http=client`). La requête va directement à l'application, en mémoire, sans serveur ni réseau. C'est pourquoi `predict` doit utiliser `self.http` et non `httpx.post`.
3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?
   Pour une démonstration à un client, la page HTML + JavaScript : l'apparence est entièrement personnalisable et le rendu plus professionnel. Pour le technicien, Streamlit : il se construit vite en Python, sans JavaScript, et offre directement graphiques, formulaire et gestion des erreurs, ce qui suffit pour un outil interne. Le prix à payer est une interface moins personnalisable.
   …

## 6. Le rendu Git

- Lien de la pull request : …
- Le tag `tp3` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? oui / non

## 7. Ce qui reste flou

…
