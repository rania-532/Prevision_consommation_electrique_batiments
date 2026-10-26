
"""Entraîne chaque modèle candidat, l'évalue sur le jeu de test et les compare.

Usage, depuis la racine du projet :
    python -m monprojet.train
"""

import json

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from monprojet import config
from monprojet.data import load_data, split
from monprojet.models import candidates


HIGHER_IS_BETTER = {
    "accuracy": True,
    "recall": True,
    "precision": True,
    "f1": True,
    "mae": False,
    "rmse": False,
    "r2": True,
}


def build_preprocessing(X: pd.DataFrame) -> ColumnTransformer:
    """Prépare les colonnes numériques, catégorielles et textuelles."""

    text_column = config.TEXT_COLUMN

    if text_column is not None and text_column not in X.columns:
        raise ValueError(
            f"La colonne textuelle '{text_column}' est absente des features."
        )

    text = [text_column] if text_column else []

    numeric = [
        column
        for column in X.columns
        if column not in text
        and pd.api.types.is_numeric_dtype(X[column])
    ]

    categorical = [
        column
        for column in X.columns
        if column not in text and column not in numeric
    ]

    steps = []

    if numeric:
        steps.append(
            (
                "nombres",
                make_pipeline(
                    SimpleImputer(strategy="median"),
                    StandardScaler(),
                ),
                numeric,
            )
        )

    if categorical:
        steps.append(
            (
                "categories",
                make_pipeline(
                    SimpleImputer(strategy="most_frequent"),
                    OneHotEncoder(handle_unknown="ignore"),
                ),
                categorical,
            )
        )

    if text:
        # TfidfVectorizer attend une séquence de textes.
        # Le transformeur reçoit ici une colonne unique.
        steps.append(
            (
                "texte",
                make_pipeline(
                    SimpleImputer(
                        strategy="constant",
                        fill_value="",
                    ),
                    TfidfVectorizer(),
                ),
                text,
            )
        )

    if not steps:
        raise ValueError(
            "Aucune feature exploitable n'a été trouvée pour le prétraitement."
        )

    return ColumnTransformer(
        transformers=steps,
        remainder="drop",
    )


def evaluate(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Évalue le modèle et renvoie les métriques arrondies à 3 décimales."""

    y_pred = model.predict(X_test)

    if config.TASK == "classification":
        average = "binary" if y_test.nunique() == 2 else "macro"

        metric_options = {
            "average": average,
            "zero_division": 0,
        }

        if average == "binary":
            classes = list(pd.unique(y_test))

            if 1 in classes:
                pos_label = 1
            elif True in classes:
                pos_label = True
            else:
                pos_label = sorted(classes, key=str)[-1]

            metric_options["pos_label"] = pos_label

        scores = {
            "accuracy": accuracy_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred, **metric_options),
            "precision": precision_score(y_test, y_pred, **metric_options),
            "f1": f1_score(y_test, y_pred, **metric_options),
        }

    elif config.TASK == "regression":
        scores = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }

    else:
        raise ValueError(
            f"TASK invalide : '{config.TASK}'. "
            "Choisissez 'classification' ou 'regression'."
        )

    return {
        name: round(float(value), 3)
        for name, value in scores.items()
    }


def main() -> None:
    """Entraîne, évalue, compare et sauvegarde les modèles."""

    # 1. Vérifier la configuration.
    if config.TASK not in {"classification", "regression"}:
        raise ValueError(
            f"TASK invalide : '{config.TASK}'. "
            "Choisissez 'classification' ou 'regression'."
        )

    if config.MAIN_METRIC not in HIGHER_IS_BETTER:
        raise ValueError(
            f"Métrique inconnue : '{config.MAIN_METRIC}'."
        )

    if config.TASK == "classification":
        allowed_metrics = {"accuracy", "recall", "precision", "f1"}
    else:
        allowed_metrics = {"mae", "rmse", "r2"}

    if config.MAIN_METRIC not in allowed_metrics:
        raise ValueError(
            f"La métrique '{config.MAIN_METRIC}' n'est pas adaptée "
            f"à la tâche '{config.TASK}'."
        )

    # 2. Charger et découper les données.
    df = load_data()

    if config.TARGET not in df.columns:
        raise ValueError(
            f"La cible '{config.TARGET}' est absente du dataset."
        )

    X_train, X_test, y_train, y_test = split(df)

    if X_train.empty or X_test.empty:
        raise ValueError(
            "Le jeu d'entraînement ou le jeu de test est vide."
        )

    if len(X_train.columns) == 0:
        raise ValueError("Aucune feature disponible pour l'entraînement.")

    print(f"Type de problème : {config.TASK}")
    print(f"Cible : {config.TARGET}")
    print(f"Nombre de lignes d'entraînement : {len(X_train)}")
    print(f"Nombre de lignes de test : {len(X_test)}")
    print(f"Métrique principale : {config.MAIN_METRIC}")

    # 3. Entraîner et évaluer chaque modèle candidat.
    resultats = {}
    modeles_entraines = {}

    for nom, estimateur in candidates().items():
        print(f"\nEntraînement du modèle : {nom}")

        model = Pipeline(
            steps=[
                ("preparation", build_preprocessing(X_train)),
                ("modele", estimateur),
            ]
        )

        try:
            model.fit(X_train, y_train)
            scores = evaluate(model, X_test, y_test)

            resultats[nom] = scores
            modeles_entraines[nom] = model

            print(f"Résultats : {scores}")

        except Exception as exc:
            print(f"Échec du modèle '{nom}' : {exc}")

    if not resultats:
        raise RuntimeError(
            "Aucun modèle n'a pu être entraîné et évalué. "
            "Vérifiez les données, la configuration et le prétraitement."
        )

    # 4. Comparer les modèles selon la métrique principale.
    tableau = pd.DataFrame(resultats).T

    ascending = not HIGHER_IS_BETTER[config.MAIN_METRIC]

    tableau = tableau.sort_values(
        by=config.MAIN_METRIC,
        ascending=ascending,
    )

    print("\n" + "=" * 60)
    print("COMPARAISON DES MODÈLES")
    print("=" * 60)
    print(tableau.to_string())

    # 5. Identifier le meilleur modèle.
    meilleur_nom = tableau.index[0]
    meilleur_modele = modeles_entraines[meilleur_nom]
    meilleure_valeur = resultats[meilleur_nom][config.MAIN_METRIC]

    print(f"\nMeilleur modèle : {meilleur_nom}")
    print(
        f"Métrique principale ({config.MAIN_METRIC}) : "
        f"{meilleure_valeur}"
    )

    # 6. Sauvegarder le modèle et les métriques.
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = config.MODELS_DIR / "model.joblib"
    metrics_path = config.MODELS_DIR / "metrics.json"

    joblib.dump(meilleur_modele, model_path)

    metrics = {
        "main_metric": config.MAIN_METRIC,
        "best": meilleur_nom,
        "results": resultats,
    }

    with open(metrics_path, "w", encoding="utf-8") as fichier:
        json.dump(
            metrics,
            fichier,
            ensure_ascii=False,
            indent=4,
        )

    print("\nSauvegarde terminée.")
    print(f"Modèle : {model_path}")
    print(f"Métriques : {metrics_path}")


if __name__ == "__main__":
    main()
