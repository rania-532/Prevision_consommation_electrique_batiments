# ADR 005 : Gestion de l'image Docker et du modèle

Date : 27/11/2026 · Auteur : BIKIKRE Rania

## Contexte

L'application MaintAI utilise un modèle entraîné qui doit être accessible à l'API au démarrage. Nous devons choisir entre intégrer ce modèle directement dans l'image Docker ou le fournir séparément.

## Options étudiées

1. **Intégrer le modèle dans l'image :** l'image contient tout le nécessaire pour exécuter l'application, mais elle devient plus volumineuse et doit être reconstruite à chaque changement du modèle.
2. **Fournir le modèle avec un volume Docker :** l'image reste plus légère et le modèle peut être remplacé sans reconstruire l'image, mais le dossier du modèle doit être disponible sur la machine hôte.

## Décision

Nous avons choisi de conserver le modèle à l'extérieur de l'image et de le monter dans le conteneur API avec un volume Docker en lecture seule : `./models:/app/models:ro`. Cette solution permet de séparer le code de l'application et les fichiers du modèle.

## Conséquences

Cette décision réduit la taille de l'image et facilite la mise à jour du modèle sans reconstruire l'image. En revanche, le dossier `models/` doit être présent et correctement monté au lancement du conteneur.