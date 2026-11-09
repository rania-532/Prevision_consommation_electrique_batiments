
"""Configuration du projet : c'est le seul fichier à adapter à votre sujet."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- Vos données -------------------------------------------------------------
DATA_PATH = ROOT / "data" / "cantine_repas.csv"
TARGET = "repas_servis"
FEATURES = None
TEXT_COLUMN = None 

# --- Type de problème --------------------------------------------------------
TASK = "regression"
MAIN_METRIC = "mae"  # Métrique principale pour choisir le meilleur modèle
# Classification : accuracy, recall, precision, f1
# Régression : mae, rmse, r2

# --- Découpage entraînement / test -------------------------------------------
SPLIT = "chronologique"  # "random" ou "chronologique"
TIME_COLUMN = "date"  # colonne de date, obligatoire si SPLIT = "chronologique"
TEST_SIZE = 0.2
SEED = 42

MODELS_DIR = ROOT / "models"
