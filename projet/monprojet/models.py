
"""Les modèles à comparer.

Renvoie une baseline et au moins trois modèles scikit-learn
adaptés au type de problème défini dans config.TASK.
"""

from monprojet import config

from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor


def candidates() -> dict:
    """Renvoie un dictionnaire {nom: modèle scikit-learn non entraîné}.

    - Le premier modèle est toujours la baseline.
    - Au moins trois modèles sont proposés ensuite.
    - Les modèles aléatoires utilisent config.SEED.
    """

    if config.TASK == "classification":
        return {
            # Baseline : prédit la classe la plus fréquente
            "Baseline": DummyClassifier(strategy="most_frequent"),

            # Modèle linéaire
            "Régression logistique": LogisticRegression(
                max_iter=1000,
                random_state=config.SEED,
            ),

            # Arbre de décision
            "Arbre de décision": DecisionTreeClassifier(
                random_state=config.SEED,
            ),

            # Forêt aléatoire
            "Random Forest": RandomForestClassifier(
                n_estimators=100,
                random_state=config.SEED,
            ),

            # K plus proches voisins
            "K plus proches voisins": KNeighborsClassifier(
                n_neighbors=5,
            ),
        }

    elif config.TASK == "regression":
        return {
            # Baseline : prédit la moyenne des valeurs d'entraînement
            "Baseline": DummyRegressor(strategy="mean"),

            # Modèle linéaire régularisé
            "Régression Ridge": Ridge(),

            # Arbre de décision
            "Arbre de décision": DecisionTreeRegressor(
                random_state=config.SEED,
            ),

            # Forêt aléatoire
            "Random Forest": RandomForestRegressor(
                n_estimators=100,
                random_state=config.SEED,
            ),

            # K plus proches voisins
            "K plus proches voisins": KNeighborsRegressor(
                n_neighbors=5,
            ),
        }

    else:
        raise ValueError(
            f"TASK invalide : '{config.TASK}'. "
            "Choisissez 'classification' ou 'regression'."
        )


if __name__ == "__main__":
    modeles = candidates()

    print(f"Type de problème : {config.TASK}")
    print(f"Nombre de modèles : {len(modeles)}")
    print("\nModèles disponibles :")

    for nom, modele in modeles.items():
        print(f"- {nom} : {type(modele).__name__}")
