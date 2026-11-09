# Compte rendu — TP3 : Une interface Streamlit pour MaintAI

**Groupe :** Groupe 4  
**Membres :** Farah Otarid, Rania Bikikre, Imane Nadif, Amine Erradha et Ayman Mahboub  
**Date :** 09/11/2026

---

# 1. Mise en place du projet

## 1.1 Installation et préparation

Nous avons commencé par préparer l'environnement virtuel et installer les dépendances nécessaires au fonctionnement du projet.

L'environnement virtuel permet d'isoler les bibliothèques du projet des autres installations Python de la machine.

Les principales commandes utilisées sont :

```bash
python -m venv .venv
```

Activation sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installation des dépendances :

```bash
pip install -r requirements.txt
```

## 1.2 Exécution des tests

Après l'installation, nous avons lancé les tests avec :

```bash
python -m pytest
```

Cette commande permet de vérifier automatiquement le fonctionnement des différentes parties du projet.

Les tests peuvent notamment vérifier :
- Le chargement et la préparation des données.
- Le fonctionnement du modèle de prédiction.
- Les réponses de l'API.
- La communication entre les composants.

Lorsqu'un test échoue, Pytest affiche le nom du test concerné ainsi que le message d'erreur. Cela permet d'identifier la partie du projet qui doit être corrigée.

---

# 2. Lancement de l'application Streamlit

## 2.1 Première tentative

Nous avons essayé de lancer l'application avec :

```bash
streamlit run ui/app.py
```

Sous Windows, il est possible que la commande `streamlit` ne soit pas reconnue, notamment lorsque le dossier des exécutables de l'environnement virtuel n'est pas correctement ajouté au PATH.

## 2.2 Deuxième tentative

Nous avons utilisé la commande suivante :

```bash
python -m streamlit run ui/app.py
```

Cette commande lance directement le module Streamlit avec l'interpréteur Python actuellement actif.

Elle permet donc d'éviter certains problèmes liés à la reconnaissance de la commande `streamlit`.

## 2.3 Résultat

L'application MaintAI s'ouvre dans le navigateur. Elle propose une interface composée de deux parties principales :

- **Visualisation des données :** permet d'explorer les relevés des capteurs et de comprendre leur distribution.
- **Prédiction :** permet de saisir les valeurs d'un équipement et d'obtenir une prédiction à travers l'API MaintAI.

---

# 3. Sprint 1 — Visualisation des données

## 3.1 Génération et chargement du dataset

Le dossier `data` était initialement vide. Nous avons donc généré un dataset synthétique afin de pouvoir entraîner le modèle et tester l'application.

Le fichier généré est :

```text
data/sensors.csv
```

Il contient les variables suivantes :

| Variable | Description |
|---|---|
| `temperature_c` | Température de l'équipement en degrés Celsius |
| `vibration_mm_s` | Niveau de vibration en mm/s |
| `load_pct` | Pourcentage de charge |
| `runtime_hours` | Nombre d'heures de fonctionnement |
| `failure` | Indique si une panne est présente (1) ou non (0) |

Les données sont synthétiques : elles servent à tester le fonctionnement du projet et ne représentent pas des mesures réelles provenant d'une installation industrielle.

## 3.2 Indicateurs principaux (KPI)

Nous avons ajouté quatre indicateurs pour obtenir rapidement une vue globale du dataset :

- Nombre total de relevés.
- Nombre de pannes.
- Taux de panne.
- Température moyenne.

Les résultats obtenus sont :

| Indicateur | Résultat |
|---|---:|
| Nombre total de relevés | 5 000 |
| Nombre de pannes | 678 |
| Taux de panne | 13,56 % |
| Température moyenne | 59,8 °C |

Le nombre de pannes est calculé à partir du taux de panne :

\[
5000 \times 0,1356 = 678
\]

Ces indicateurs permettent de comprendre rapidement l'état général des données.

## 3.3 Visualisation de la distribution des pannes

Nous avons ajouté un graphique en barres pour comparer les équipements normaux et ceux présentant une panne.

La variable `failure` possède deux valeurs :
- `0` : fonctionnement normal.
- `1` : panne détectée.

Ce graphique permet de constater que les observations sans panne sont plus nombreuses que celles avec panne.

## 3.4 Analyse du taux de panne selon une caractéristique

Nous avons ajouté un graphique permettant d'étudier l'évolution du taux de panne selon une caractéristique sélectionnée par l'utilisateur.

Les valeurs sont regroupées en cinq intervalles (*bins*). Pour chaque intervalle, nous calculons le taux de panne.

Cela permet notamment d'observer la relation entre les vibrations et les pannes.

Dans notre génération synthétique, les vibrations ont un effet positif sur la probabilité de panne. On s'attend donc globalement à observer davantage de pannes lorsque le niveau de vibration augmente.

Cependant, le taux observé peut varier d'un intervalle à l'autre à cause de la répartition aléatoire des observations.

## 3.5 Nuage de points : température et vibrations

Nous avons également ajouté un nuage de points (*scatter plot*) qui représente :

- L'axe horizontal : la température.
- L'axe vertical : le niveau de vibration.
- La couleur : l'état de l'équipement (normal ou panne).

Ce graphique permet de visualiser la répartition des observations et de repérer les éventuelles concentrations de pannes.

## 3.6 Affichage des données brutes

Enfin, un espace dépliant permet d'afficher le dataset sous forme de tableau.

Cette fonctionnalité permet de consulter les relevés individuels sans surcharger l'interface principale.

## 3.7 Comprendre le fonctionnement de Streamlit

### Question : Que se passe-t-il lorsqu'on ajoute `print("relance")` puis qu'on déplace un slider ?

Streamlit fonctionne avec un système de réexécution du script.

Lorsqu'un utilisateur modifie un élément interactif, Streamlit réexécute le script afin de mettre à jour l'affichage.

Ainsi, si le slider est utilisé directement, le message `relance` apparaît de nouveau dans le terminal à chaque réexécution.

Dans notre interface, les champs de prédiction sont placés dans un formulaire avec `st.form`. Dans ce cas, modifier un slider ne déclenche pas immédiatement la prédiction : il faut cliquer sur le bouton de soumission du formulaire.

### Question : À quoi sert `@st.cache_data` ?

`@st.cache_data` est un décorateur Streamlit qui permet de mettre en cache les résultats d'une fonction.

Par exemple, lorsqu'une fonction charge le fichier CSV, Streamlit peut conserver le résultat pour éviter de relire le fichier à chaque réexécution.

Cela permet :
- D'améliorer les performances.
- De réduire les lectures inutiles du fichier.
- De rendre l'application plus rapide et plus fluide.

Le cache est réutilisé tant que les paramètres de la fonction et les données prises en compte restent identiques.

---

# 4. Sprint 2 — Connexion à l'API MaintAI

## 4.1 Implémentation de la méthode `predict`

Nous avons complété la méthode `predict()` dans le fichier `maintai/client.py`.

Son rôle est d'envoyer les données des capteurs à l'API et de récupérer le résultat de la prédiction.

Code utilisé :

```python
def predict(self, reading: dict) -> dict:
    headers = {}

    if self.api_key:
        headers["X-API-Key"] = self.api_key

    r = self.http.post(
        "/v1/predict",
        json=reading,
        headers=headers
    )

    if r.status_code != 200:
        try:
            detail = r.json().get("detail")
        except ValueError:
            detail = r.text

        raise APIError(r.status_code, detail)

    return r.json()
```

La méthode effectue les opérations suivantes :

1. Prépare les en-têtes de la requête.
2. Ajoute la clé API si elle est disponible.
3. Envoie les valeurs des capteurs à la route `/v1/predict`.
4. Vérifie le code de réponse HTTP.
5. Retourne le résultat au format JSON si la requête réussit.
6. Déclenche une erreur `APIError` si l'API retourne une réponse incorrecte.

## 4.2 Gestion des différents cas

L'interface doit gérer trois situations principales.

| Situation | Comportement attendu |
|---|---|
| Clé API correcte et API disponible | Affichage de la probabilité de panne et de l'alerte |
| Clé API incorrecte | Affichage d'une erreur d'authentification |
| API arrêtée ou inaccessible | Affichage d'un message indiquant que l'API est injoignable |

Lorsque la requête réussit, l'API retourne notamment :

- `failure_probability` : probabilité estimée de panne.
- `alert` : résultat de l'évaluation selon le seuil configuré.

La probabilité est affichée sous forme de pourcentage afin de faciliter sa compréhension.

## 4.3 Pourquoi le port 8501 n'est-il pas nécessaire dans la configuration CORS ?

Streamlit fonctionne généralement sur le port 8501 et l'API FastAPI sur le port 8000.

Cependant, dans notre application, les requêtes sont envoyées depuis le code Python de Streamlit avec la bibliothèque HTTPX.

Il s'agit donc d'une communication entre deux processus côté serveur, et non d'une requête JavaScript directement exécutée dans le navigateur.

La politique CORS concerne principalement les requêtes effectuées par les navigateurs entre différentes origines.

C'est pourquoi le port 8501 n'a pas besoin d'être ajouté aux origines CORS pour cette communication HTTPX.

---

# 5. Comparaison entre TP2 et TP3

## 5.1 Pourquoi le TP3 utilise-t-il un client Python ?

Dans le TP3, nous avons développé un client Python qui communique avec l'API MaintAI.

Ce client permet de centraliser les requêtes HTTP, la transmission de la clé API et la gestion des erreurs.

Cela évite de répéter le même code dans différentes parties de l'application.

## 5.2 Pourquoi `test_client.py` n'a-t-il pas besoin d'Uvicorn ?

Le fichier `test_client.py` peut utiliser un client de test injecté dans `MaintaiClient`.

Par exemple, FastAPI fournit `TestClient`, qui permet d'appeler directement l'application en mémoire.

Il n'est donc pas nécessaire de démarrer un véritable serveur Uvicorn pour ces tests.

Cela rend les tests plus rapides et évite de dépendre d'un serveur externe.

## 5.3 Comparaison entre HTML/JavaScript et Streamlit

| HTML + JavaScript | Streamlit |
|---|---|
| Permet de créer des interfaces web personnalisées | Permet de créer rapidement des interfaces interactives en Python |
| Offre un contrôle important sur le design | Propose des composants déjà prêts |
| Demande davantage de développement front-end | Nécessite principalement des connaissances Python |
| Adapté aux applications web destinées aux utilisateurs finaux | Adapté aux prototypes, tableaux de bord et outils internes |

Dans notre projet, Streamlit est adapté parce qu'il permet de construire rapidement une interface de visualisation et de prédiction sans développer séparément toute la partie front-end.

---

# 6. Git et livraison

Le projet doit être versionné avec Git afin de conserver l'historique des modifications et de faciliter le travail en équipe.

Avant de créer un commit, il faut vérifier les fichiers modifiés :

```bash
git status
```

Les éléments suivants doivent être vérifiés :

| Élément | À versionner ? | Explication |
|---|---|---|
| Code source (`maintai/`, `ui/`, `tests/`) | Oui | Contient le code du projet |
| `COMPTE_RENDU.md` | Oui | Contient le compte rendu |
| `data/sensors.csv` | Selon les consignes du projet | Dataset synthétique nécessaire à la reproduction |
| `.env` | Non | Contient des informations sensibles comme la clé API |
| `.env.example` | Oui | Présente les variables nécessaires sans révéler les secrets |
| `.venv/` | Non | Environnement virtuel local |
| `models/` | Selon les consignes | Les modèles générés peuvent être reproductibles à partir du code d'entraînement |

Il est important de vérifier que `.env` est bien ignoré par Git avant tout commit.

Pour vérifier le tag :

```bash
git tag
```

Pour vérifier la branche et les modifications :

```bash
git status
```

**Lien de la Pull Request :** à renseigner après sa création.

**Tag `tp3` :** à vérifier avec `git tag`.

---

# 7. Difficultés rencontrées et solutions

| Difficulté | Solution |
|---|---|
| Le dossier `data` était vide | Génération d'un dataset synthétique |
| Le fichier `sensors.csv` était introuvable | Création du fichier dans `data/` |
| La commande `streamlit` pouvait ne pas être reconnue | Utilisation de `python -m streamlit run ui/app.py` |
| La clé API n'était pas chargée par le serveur | Chargement du fichier `.env` avec `python-dotenv` |
| L'API pouvait être inaccessible pendant une prédiction | Gestion des erreurs HTTP dans le client Python |

---

# 8. Conclusion

Ce TP nous a permis de compléter le projet MaintAI en ajoutant une interface interactive avec Streamlit.

Nous avons appris à :
- Préparer et exploiter un dataset de capteurs.
- Présenter des indicateurs clés sous forme de KPI.
- Créer des graphiques interactifs pour explorer les données.
- Connecter une interface Python à une API FastAPI.
- Gérer les erreurs de communication et d'authentification.
- Comprendre le fonctionnement de Streamlit, notamment ses réexécutions et son système de cache.
- Utiliser les tests automatisés pour vérifier le fonctionnement des composants.

L'application permet maintenant d'explorer les données et de soumettre des relevés à l'API afin d'obtenir une estimation du risque de panne.

Ce travail constitue une étape importante dans la réalisation d'un outil de maintenance prédictive basé sur l'intelligence artificielle.