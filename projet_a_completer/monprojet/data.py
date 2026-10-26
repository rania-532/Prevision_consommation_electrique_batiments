
"""Chargement et découpage des données.

Chargement du fichier CSV et séparation des données
pour entraîner et tester les modèles.
"""

import pandas as pd
from sklearn.model_selection import train_test_split

from monprojet import config


def load_data(path=None) -> pd.DataFrame:
    """Lit le fichier CSV et renvoie un DataFrame.

    - Lit config.DATA_PATH ou le chemin path s'il est fourni.
    - Vérifie que la colonne cible existe.
    - Supprime les lignes où la cible est manquante.
    """
    if path is None:
        path = config.DATA_PATH

    df = pd.read_csv(path)

    if config.TARGET not in df.columns:
        raise ValueError(
            f"La colonne cible '{config.TARGET}' "
            "n'existe pas dans le fichier CSV."
        )

    df = df.dropna(subset=[config.TARGET]).reset_index(drop=True)

    if df.empty:
        raise ValueError(
            "Aucune donnée disponible après suppression "
            "des lignes dont la cible est manquante."
        )

    return df


def feature_columns(df: pd.DataFrame) -> list:
    """Retourne les colonnes d'entrée du modèle.

    Utilise config.FEATURES si elle est définie.
    Sinon, exclut la cible et la colonne de date.
    """
    if config.FEATURES is not None:
        missing = [c for c in config.FEATURES if c not in df.columns]

        if missing:
            raise ValueError(
                f"Les colonnes suivantes sont absentes : {missing}"
            )

        return list(config.FEATURES)

    excluded = {config.TARGET, config.TIME_COLUMN}

    return [c for c in df.columns if c not in excluded]


def split(df: pd.DataFrame):
    """Renvoie X_train, X_test, y_train, y_test.

    - En mode random : découpage aléatoire.
    - En mode chronologique : les observations les plus récentes
      sont utilisées pour le test.
    """
    if config.TARGET not in df.columns:
        raise ValueError(
            f"La colonne cible '{config.TARGET}' "
            "n'existe pas dans le DataFrame."
        )

    if not 0 < config.TEST_SIZE < 1:
        raise ValueError("TEST_SIZE doit être compris entre 0 et 1.")

    features = feature_columns(df)

    if not features:
        raise ValueError(
            "Aucune colonne disponible pour les variables d'entrée."
        )

    X = df[features]
    y = df[config.TARGET]

    if len(df) < 2:
        raise ValueError(
            "Au moins deux lignes sont nécessaires pour le découpage."
        )

    if config.SPLIT == "random":
        stratify = None

        if config.TASK == "classification":
            counts = y.value_counts()

            if len(counts) > 1 and counts.min() >= 2:
                n_test = max(1, int(len(df) * config.TEST_SIZE))
                n_train = len(df) - n_test

                if n_test >= len(counts) and n_train >= len(counts):
                    stratify = y

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=config.TEST_SIZE,
            random_state=config.SEED,
            stratify=stratify,
        )

    elif config.SPLIT == "chronologique":
        if config.TIME_COLUMN is None:
            raise ValueError(
                "TIME_COLUMN doit être défini pour un découpage chronologique."
            )

        if config.TIME_COLUMN not in df.columns:
            raise ValueError(
                f"La colonne temporelle '{config.TIME_COLUMN}' "
                "n'existe pas dans le DataFrame."
            )

        dates = pd.to_datetime(
            df[config.TIME_COLUMN],
            errors="raise",
        )

        if dates.isna().any():
            raise ValueError(
                "La colonne temporelle contient des dates manquantes."
            )

        # Trier chronologiquement : passé pour l'entraînement,
        # observations les plus récentes pour le test.
        indices = dates.sort_values(kind="stable").index

        n_test = max(1, int(len(df) * config.TEST_SIZE))

        if n_test >= len(df):
            raise ValueError(
                "Le jeu de données est trop petit pour effectuer le découpage."
            )

        train_indices = indices[:-n_test]
        test_indices = indices[-n_test:]

        X_train = X.loc[train_indices]
        X_test = X.loc[test_indices]
        y_train = y.loc[train_indices]
        y_test = y.loc[test_indices]

    else:
        raise ValueError(
            f"Valeur SPLIT invalide : '{config.SPLIT}'. "
            "Utilisez 'random' ou 'chronologique'."
        )

    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    # Vérification rapide du chargement et du découpage.
    df = load_data()

    print("Données chargées avec succès.")
    print(f"Fichier : {config.DATA_PATH}")
    print(f"Nombre de lignes : {len(df)}")
    print(f"Cible : {config.TARGET}")
    print(f"Variables d'entrée : {feature_columns(df)}")

    X_train, X_test, y_train, y_test = split(df)

    print("\nDécoupage terminé.")
    print(f"X_train : {X_train.shape}")
    print(f"X_test  : {X_test.shape}")
    print(f"y_train : {y_train.shape}")
    print(f"y_test  : {y_test.shape}")

    if config.SPLIT == "chronologique":
        print(
            "\nPériode d'entraînement :",
            pd.to_datetime(df.loc[X_train.index, config.TIME_COLUMN]).min(),
            "→",
            pd.to_datetime(df.loc[X_train.index, config.TIME_COLUMN]).max(),
        )
        print(
            "Période de test :",
            pd.to_datetime(df.loc[X_test.index, config.TIME_COLUMN]).min(),
            "→",
            pd.to_datetime(df.loc[X_test.index, config.TIME_COLUMN]).max(),
        )
