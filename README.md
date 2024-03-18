# credit_api

Une application de “scoring crédit” pour prédir d'accorder ou réfuser un crédit à un client en utilisant un classifieur LigntGBM optimisé et s'appuyant sur des sources de données test variées (données comportementales, données provenant d'autres institutions financières, etc.)
Réalisée en Flask et Streamlit et deployée via Streamlit, se basant sur ce repo à l'adresse:

https://creditapi-farvaphn8zvqsumca5abcg.streamlit.app

## Les dossiers

data:

-> application_test.csv: les données clients test

-> application_test_ohe.csv: les données clients test traités par One_Hot_Encoding (disponibilité des données pour le modèle)
  
-> best_model.pickle: le modèle optimisé LightGBM
  
-> logo.png: image de page d'accueil
  
sources:

-> main.py: l'application Streamlit (partie IHM)

-> model_data.py: l'api flask (partie module de données et prédiction)
  
tests:

-> test_api: script test de l'api en pytest, intégration continue, GitHub Action
  
.idea: dossier de configuration PyCharm

.github/workflows:

-> test.yml: services d'intégration continue lance le script pytest à chaque commit
  
requirements.txt: liste des packages requis pour le projet

## Utilisation

Ce projet a été créé dans le cadre d'un travail de formation profesionnelle et est ouvert à des fins éducatives et non commerciales. Vous êtes libre de :

- Utiliser le code à des fins éducatives et académiques.
- Modifier le code pour vos propres besoins.
- Distribuer des copies du code aux autres étudiants ou enseignants.

## Contact

Informations de contact
