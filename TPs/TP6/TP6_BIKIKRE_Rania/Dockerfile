# Image de MaintAI : le code et ses bibliothèques, sans les données ni le modèle.
# Construire : docker build -t maintai:0.4.0 .

# Image de base : Python 3.11 version légère
FROM python:3.11-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier uniquement le fichier des dépendances
COPY requirements-docker.txt .

# Installer les bibliothèques nécessaires
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copier le code de l'application
COPY maintai ./maintai
COPY ui ./ui

# Définir les chemins des données et du modèle
ENV MAINTAI_MODELS_DIR=/app/models
ENV MAINTAI_DATA_PATH=/app/data/sensors.csv

# Port utilisé par l'API
EXPOSE 8000

# Démarrer l'API avec Uvicorn
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
