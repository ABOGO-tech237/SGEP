# Résumé technique du codebase

Date: 2026-05-15

Ce dépôt héberge principalement l'application backend d'un système de gestion d'école primaire (Django). Le code applicatif principal se trouve sous le dossier `backend/`. Le dossier `frontend/` est volontairement vide et contient un fichier repère.

Branches importantes
- `main`: Branche principale volontairement vide (commit racine vide).
- `backenddevellopement-01`: Branche de développement active contenant l'ensemble du backend.

Vue d'ensemble de l'architecture
- Projet Django localisé dans `backend/SGEP` (module projet).
- Apps Django (chaque app est sous `backend/<appname>`) : `accounts`, `students`, `teachers`, `classes`, `attendance`, `finance`, `grades`, `parents`, `reports`, `notifications`, `core`, etc.
- Pattern d'accès aux données : `View (DRF) -> Service -> Repository -> Appwrite SDK`.
- Authentification : modèle utilisateur custom (`accounts.models.User`) + génération/validation de JWT (Simple JWT) ; persistance utilisateurs et blacklist via Appwrite.

Fichiers et dossiers clés
- `backend/manage.py` : commandes Django (tests, runserver, etc.).
- `backend/SGEP/settings.py` : configuration Django.
- `backend/config/appwrite_client.py` et `backend/core/services/appwrite_service.py` : wrapper/connexion à Appwrite.
- `backend/accounts/` : logique auth (vues, services, repository, permissions, serializers, modèles).
- `backend/core/management/commands/` : scripts utilitaires (ex. `setup_appwrite.py`, `populate_cameroon_data.py`).
- `backend/requirements.txt` : dépendances Python.
- `backend/docker-compose.yml`, `backend/Dockerfile` : fichiers d'orchestration et containerisation.

Dépendances et environnement
- Utilise Appwrite pour la persistence métier et Redis/Celery pour les tâches asynchrones.
- Variables d'environnement attendues (extrait) :
	- `APPWRITE_ENDPOINT`, `APPWRITE_PROJECT_ID`, `APPWRITE_API_KEY`, `APPWRITE_DB_ID`
	- `REDIS_URL`, `CELERY_BROKER_URL`
	- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`

Exécution locale (rapide)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
# définir les variables d'environnement requises (Appwrite, Redis...)
python backend/manage.py test
python backend/manage.py runserver
```

Tests
- Les tests unitaires et d'API sont dans les répertoires `backend/*/tests.py` (ex. `backend/accounts/tests.py`, `backend/students/tests.py`).
- Les tests qui touchent Appwrite utilisent des mocks afin d'isoler la logique métier.




