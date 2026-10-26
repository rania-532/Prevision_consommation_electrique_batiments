"""Les modèles à comparer.

À vous d'écrire candidates(). Les tests de tests/test_models.py disent ce qui est attendu.
"""
from monprojet import config  # noqa: F401  (config.TASK, config.SEED)


def candidates() -> dict:
    """Renvoie un dictionnaire {nom: modèle scikit-learn non entraîné}.

    Attendu :
    - le PREMIER modèle est la baseline : le modèle le plus simple possible
      (DummyClassifier pour une classification, DummyRegressor pour une régression) ;
    - au moins trois vrais modèles ensuite, adaptés à config.TASK ;
    - random_state=config.SEED pour les modèles qui ont du hasard.

    Pistes : sklearn.dummy, sklearn.linear_model, sklearn.ensemble, sklearn.neighbors, sklearn.tree.
    """
    if str(config.TASK).lower().startswith("classif"):
        from sklearn.dummy import DummyClassifier
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.tree import DecisionTreeClassifier

        return {
            "baseline": DummyClassifier(strategy="most_frequent"),
            "logistic_regression": LogisticRegression(max_iter=1000, random_state=config.SEED),
            "decision_tree": DecisionTreeClassifier(random_state=config.SEED),
            "random_forest": RandomForestClassifier(random_state=config.SEED),
        }

    from sklearn.dummy import DummyRegressor
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.tree import DecisionTreeRegressor

    return {
        "baseline": DummyRegressor(strategy="mean"),
        "linear_regression": LinearRegression(),
        "decision_tree": DecisionTreeRegressor(random_state=config.SEED),
        "random_forest": RandomForestRegressor(random_state=config.SEED),
    }