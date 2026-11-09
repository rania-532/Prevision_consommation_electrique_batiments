# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Membre :** BIKIKRE Rania  **Date :** 09/11/2026

## 1. Mise en place (dans `TPs/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```text
5 failed, 18 passed, 1 warning in 5.02s
```

**Quels fichiers de tests échouent, et quelle erreur donnent-ils ?**

- `tests/test_client.py` :
  - `test_client_returns_prediction` : `NotImplementedError`
  - `test_client_wrong_key_raises_401` : `NotImplementedError`
  - `test_client_bad_reading_raises_422` : `NotImplementedError`
- `tests/test_ui.py` :
  - `test_ui_shows_the_data` : `IndexError: list index out of range`
  - `test_ui_shows_the_prediction` : `IndexError: list index out of range`

## 2. Lancer Streamlit

**Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il ?**

```text
ModuleNotFoundError: No module named 'maintai'
```

**Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?**

La commande `python -m streamlit` lance Streamlit avec l'interpréteur Python de l'environnement virtuel actif. Elle permet donc d'utiliser les bonnes dépendances et de résoudre correctement le module `maintai`.


## 3. Sprint 1 : l'onglet « Données »

**Code de l'onglet « Données » :**

```python
with onglet_donnees:
    df = charger(get_settings().data_path)

    # Trois indicateurs
    c1, c2, c3 = st.columns(3)
    c1.metric("Nombre de relevés", len(df))
    c2.metric("Taux de panne", f"{df['failure'].mean():.1%}")
    c3.metric("Température moyenne", f"{df['temperature_c'].mean():.1f} °C")

    # Choix d'une variable
    variable = st.selectbox("Choisir une variable", FEATURES)

    # Taux de panne par tranche
    tranches = pd.cut(df[variable], bins=10)
    taux = df.groupby(tranches, observed=True)["failure"].mean()

    graphique = pd.DataFrame(
        {"Taux de panne": taux.values},
        index=[round(i.mid, 2) for i in taux.index]
    )

    st.subheader(f"Taux de panne selon {variable}")
    st.bar_chart(graphique)

    # Nuage de points
    df["etat_panne"] = df["failure"].map({0: "Non", 1: "Oui"})

    st.subheader("Température et vibration selon l'état de panne")
    st.scatter_chart(
        df,
        x="temperature_c",
        y="vibration_mm_s",
        color="etat_panne"
    )
```

**Résultats affichés :**

| Indicateur | Valeur |
|---|---:|
| Nombre de relevés | 5000 |
| Taux de panne | 13,6 % |
| Température moyenne | 59,8 °C |

**Comment évolue le taux de panne quand la vibration augmente ?**

Le taux de panne augmente avec le niveau de vibration.

**Que montre l'affichage de `relance` dans le terminal après le déplacement d'un curseur ?**

Il montre que Streamlit réexécute automatiquement le script lorsqu'un utilisateur interagit avec un widget.

**À quoi sert `@st.cache_data` sur la fonction `charger` ?**

Il évite de relire le fichier CSV à chaque réexécution, tant que les données mises en cache restent valides.

## 4. Sprint 2 : l'onglet « Prédiction »

**Méthode `predict` dans `maintai/client.py` :**

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé ; lève APIError si l'API refuse."""

    headers = {}
    if self.api_key:
        headers["X-API-Key"] = self.api_key

    r = self.http.post(
        "/v1/predict",
        json=reading,
        headers=headers
    )

    if r.status_code != 200:
        raise APIError(r.status_code, r.json().get("detail"))

    return r.json()
```

**Dernière ligne de `python -m pytest` à la fin du sprint 2 :**

```text
À compléter avec le résultat final réellement obtenu.
```

**Résultats des essais avec l'API lancée :**

| Essai | Ce qu'affiche Streamlit |
|---|---|
| Valeurs par défaut, bonne clé | Probabilité de panne et message d'alerte ou de fonctionnement normal. |
| Valeurs par défaut, fausse clé | Erreur 401 : clé API incorrecte. |
| API arrêtée (`Ctrl+C`) | Message indiquant que l'API est injoignable. |

**Pourquoi la prédiction fonctionne-t-elle même si le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS` ?**

Parce que la requête est envoyée par Python depuis le serveur Streamlit vers FastAPI. Il ne s'agit pas d'une requête directe du navigateur : la politique CORS ne s'applique donc pas.

## 5. Questions de compréhension

**1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?**

Dans le TP2, c'est JavaScript qui envoie la requête avec `fetch`. Dans le TP3, c'est le code Python de Streamlit qui communique avec l'API.

**2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'Uvicorn ?**

Ils utilisent `TestClient`, qui permet de tester directement l'application FastAPI sans démarrer un serveur Uvicorn.

**3. HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous ?**

Pour une démonstration à un client, je choisirais Streamlit pour sa simplicité et sa rapidité de mise en place. Pour une application destinée à un technicien de maintenance, je privilégierais HTML + JavaScript pour disposer d'une interface plus personnalisable.

## 6. Le rendu Git

- Lien de la pull request : **À compléter**
- Le tag `tp3` existe sur GitHub : **À compléter**
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? **À vérifier**

## 7. Ce qui reste flou

Aucun point particulier pour le moment.