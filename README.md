# Prévision de la consommation électrique de bâtiments

Projet du cours **Développement et déploiement d'applications intelligentes**.

**Groupe :** ...

## Objectif

Prévoir la consommation électrique horaire de bâtiments à partir d'une série temporelle réelle, puis exposer le modèle via une API FastAPI et une interface Streamlit. Un assistant RAG dédié à l'efficacité énergétique est prévu dans une phase ultérieure.

## Jeu de données

Le projet prévoit d'utiliser le *Building Data Genome Project 2* (BDG2).

Les choix définitifs concernant le site, les bâtiments, les critères de sélection et les règles de nettoyage seront documentés dans `docs/adr/` après analyse des données et validation par le groupe.

## Environnement

- Python 3.11
- Git et GitHub
- VS Code recommandé

Les commandes d'installation et les versions des dépendances seront renseignées après vérification de l'environnement du projet.

## Organisation

- `notebooks/` : exploration et préparation des données.
- `data/` : données locales, jamais versionnées avec Git.
- `monprojet/` : code Python réutilisable.
- `tests/` : tests automatisés.
- `docs/` : étude de conception et décisions d'architecture.
- `ui/` : interface Streamlit.

## Confidentialité et reproductibilité

Les données brutes, les données traitées, les modèles entraînés, l'environnement virtuel et le fichier `.env` ne doivent pas être commités dans Git.

Les décisions méthodologiques seront documentées et les résultats devront pouvoir être reproduits à partir des sources et des instructions du projet.