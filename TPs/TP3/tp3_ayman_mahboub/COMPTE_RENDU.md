# Compte rendu — TP3

## Interface Streamlit pour MaintAI

| Information | Valeur |
|---|---|
| Groupe | G2 |
| Membres | AYMAN MAHBOUB… |
| Date | 09/11/2026 |

---

## 1. Mise en place

### Résultat des tests

Après la création de l'environnement virtuel et l'installation des
dépendances, la commande `python -m pytest` donne :

```text
============================== 23 passed ==============================
```

Tous les tests passent. Aucun fichier de test n'échoue.

---

## 2. Lancement de Streamlit

### Première commande

La commande :

```powershell
streamlit run ui/app.py
```

échoue si l'environnement virtuel n'est pas activé ou si son dossier
`Scripts` n'est pas dans le `PATH` :

```text
streamlit n'est pas reconnu comme commande
```

### Commande fonctionnelle

La commande suivante fonctionne :

```powershell
python -m streamlit run ui/app.py
```

Elle demande explicitement à l'interpréteur Python courant d'exécuter le
module Streamlit installé dans `.venv`. Elle ne dépend donc pas de la
présence directe de l'exécutable `streamlit` dans le `PATH`.

---

## 3. Sprint 1 — Onglet « Données »

### Code réalisé

```python
with onglet_donnees:
    df = charger(get_settings().data_path)
    indicateurs = st.columns(3)
    indicateurs[0].metric("Nombre de relevés", f"{len(df)}")
    indicateurs[1].metric("Taux de panne", f"{df.failure.mean() * 100:.1f} %")
    indicateurs[2].metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

    variable = st.selectbox("Variable à analyser", FEATURES)
    tranches = pd.cut(df[variable], bins=8)
    taux_par_tranche = (
        df.groupby(tranches, observed=False)["failure"]
        .mean()
        .rename("Taux de panne")
    )
    taux_par_tranche.index = taux_par_tranche.index.astype(str)
    st.bar_chart(taux_par_tranche)

    st.scatter_chart(
        df,
        x="temperature_c",
        y="vibration_mm_s",
        color="failure",
    )
```

### Indicateurs affichés

| Indicateur | Valeur |
|---|---:|
| Nombre de relevés | 5000 |
| Taux de panne | 13,6 % |
| Température moyenne | 59,8 °C |

### Influence de la vibration

Lorsque `vibration_mm_s` augmente, le taux de panne augmente nettement :

- environ 2,8 % dans la première tranche ;
- environ 15,7 %, 54,1 % et 77,5 % dans les tranches suivantes ;
- jusqu'à 100 % dans les tranches de vibration élevées.

Certaines tranches peuvent être vides, car les données ne contiennent pas
forcément de relevés dans chaque intervalle.

### Fonctionnement de Streamlit

Après l'ajout de `print("relance")` au début de `ui/app.py`, le message
apparaît à chaque déplacement d'un curseur. Streamlit réexécute donc le
script de haut en bas après chaque interaction avec un widget.

### Utilité de `st.cache_data`

Le décorateur `@st.cache_data` mémorise le résultat de la fonction
`charger`. Le fichier CSV n'est ainsi pas relu inutilement à chaque
réexécution du script. Le cache est recalculé lorsque les arguments de la
fonction changent.

---

## 4. Sprint 2 — Onglet « Prédiction »

### Méthode `predict`

```python
def predict(self, reading: dict) -> dict:
    headers = {"X-API-Key": self.api_key} if self.api_key is not None else {}
    response = self.http.post("/v1/predict", json=reading, headers=headers)
    if response.status_code != 200:
        try:
            body = _response_json(response)
        except ValueError:
            body = {}
        detail = body.get("detail") if isinstance(body, dict) else None
        if not detail:
            detail = response.text.strip() or "Réponse d'erreur vide"
        raise APIError(response.status_code, detail)
    return _response_json(response)
```

La méthode :

1. ajoute la clé `X-API-Key` si elle est fournie ;
2. envoie le relevé à `/v1/predict` ;
3. transforme les réponses d'erreur en `APIError` ;
4. renvoie le JSON de prédiction si le statut HTTP est 200.

### Résultat final des tests

```text
============================== 23 passed ==============================
```

### Essais réalisés

| Essai | Résultat dans Streamlit |
|---|---|
| Valeurs par défaut avec la bonne clé | Probabilité de panne affichée, puis « Fonctionnement normal » ou « ALERTE » |
| Valeurs par défaut avec une fausse clé | `Erreur API (401) : Clé API absente ou invalide` |
| API arrêtée | `API injoignable : ...` |

### Pourquoi CORS ne bloque-t-il pas la prédiction ?

Streamlit envoie la requête depuis Python avec `httpx`. Il s'agit d'une
communication serveur-à-serveur, et non d'une requête effectuée par le
navigateur. La règle CORS est appliquée par les navigateurs ; elle ne bloque
donc pas cette requête Python.

---

## 5. Questions de compréhension

### 5.1 Qui envoie la requête à l'API ?

Dans le TP2, le code JavaScript de la page HTML envoie la requête depuis le
navigateur.

Dans le TP3, le code Python de Streamlit utilise `MaintaiClient` et `httpx`
pour envoyer la requête.

### 5.2 Pourquoi Uvicorn n'est-il pas nécessaire pour `test_client.py` ?

Les tests fournissent un `TestClient` à `MaintaiClient`. Les requêtes sont
alors envoyées directement à l'application FastAPI en mémoire. Aucun serveur
Uvicorn ni aucun port réseau ne sont nécessaires.

### 5.3 Quelle interface choisir ?

Pour une démonstration rapide à un client, je choisirais Streamlit : les
graphiques et les contrôles sont rapides à créer et à modifier.

Pour l'utilisation quotidienne par un technicien de maintenance, je
privilégierais une interface web dédiée comme celle du TP2. Elle est plus
légère, plus contrôlable et mieux adaptée à un parcours utilisateur
stabilisé.

---

## 6. Rendu Git

| Élément | État |
|---|---|
| Lien de la pull request | Non applicable dans cet environnement local |
| Tag `tp3` sur GitHub | Non vérifiable : le dossier fourni n'est pas un dépôt Git |
| `.env`, `data/` et `models/` visibles dans `git status` | Non : ces éléments sont ignorés par `.gitignore` |

---

## 7. Conclusion et éléments restant à compléter

L'interface Streamlit permet maintenant :

- d'explorer les données et les indicateurs principaux ;
- de visualiser le taux de panne selon une variable ;
- d'afficher un nuage de points température/vibration ;
- d'envoyer un relevé à l'API ;
- d'afficher une prédiction ou un message d'erreur adapté.

Il reste uniquement à compléter les informations administratives finales
(nom complet des membres et lien de pull request) si le rendu est publié
sur GitHub.
