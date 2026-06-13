# SGEP

Système de Gestion d'Ecole Primaire adapte au contexte camerounais.

Ce depot contient le backend Django du projet. La couche metier utilise Appwrite pour la persistence des donnees, et Simple JWT uniquement pour emettre et valider les tokens d'authentification.

## Objectif de ce travail

La zone `accounts` a ete mise en place pour couvrir l'authentification complete:

- modele utilisateur custom base sur `AbstractBaseUser`
- repository Appwrite pour la collection `users`
- generation des tokens `access_token` et `refresh_token`
- renouvellement du token d'acces
- logout avec blacklist du refresh token dans Appwrite
- changement de mot de passe
- permissions DRF conformes au cahier des charges
- rate limiting sur le login

## Architecture

Le projet suit le principe suivant:

`View DRF -> Service -> Repository -> Appwrite SDK`

Les vues ne parlent pas directement a Appwrite. Toute la logique d'acces aux donnees passe par les repositories.

## Authentification

### Modele utilisateur

Le modele utilisateur se trouve dans [accounts/models.py](accounts/models.py).

Champs principaux:

- `id`: UUID primaire
- `email`: identifiant de connexion
- `role`: `superadmin`, `comptable`, `parent`
- `account_status`: `active`, `suspended`
- `student_id`: nullable, prevu pour les parents

Points importants:

- il n'y a pas de champ `username`
- l'email est le login
- le modele est configure pour travailler avec Appwrite cote persistence metier

### Repository Appwrite

Le repository d'auth est dans [accounts/repository.py](accounts/repository.py).

Collections utilisees:

- `users`
- `refresh_token_blacklist`

Responsabilites:

- lire un user par email
- lire un user par id
- creer un user
- mettre a jour un user
- ajouter un refresh token a la blacklist
- verifier si un jti est deja blacklist

### Service d'auth

La logique metier est dans [accounts/services.py](accounts/services.py).

Fonctions fournies:

- `login(email, password)`
- `refresh_access_token(refresh_token)`
- `logout(refresh_token)`
- `change_password(user_id, old_password, new_password)`

### Endpoints

Les routes sont definies dans [accounts/urls.py](accounts/urls.py).

#### POST `/api/v1/auth/login/`

Retourne:

- `access_token`
- `refresh_token`

#### POST `/api/v1/auth/refresh/`

Retourne:

- `access_token`

#### POST `/api/v1/auth/logout/`

Effet:

- blacklist du refresh token dans Appwrite

#### POST `/api/v1/auth/change-password/`

Effet:

- verification de l'ancien mot de passe
- hash du nouveau mot de passe
- mise a jour du user dans Appwrite

## Permissions

Les permissions DRF sont dans [accounts/permissions.py](accounts/permissions.py).

Classes disponibles:

- `IsSuperAdmin`
- `IsComptable`
- `IsActiveParent`
- `IsParentAny`

Roles geres:

- `superadmin`
- `comptable`
- `parent`

## Rate limiting

Le login est protege par un rate limit de 5 tentatives toutes les 10 minutes.

Implementation:

- decorateur `django-ratelimit`
- applique sur `LoginView`

## Configuration Django

Le routage global est branche dans [config/urls.py](config/urls.py).

Les points importants de configuration sont:

- `AUTH_USER_MODEL = "accounts.User"`
- auth JWT custom via `accounts.authentication.AppwriteJWTAuthentication`
- handler global d'erreur dans `core.handlers.custom_exception_handler`
- app `accounts` ajoutee a `INSTALLED_APPS`

## Gestion des erreurs

Les exceptions metier reutilisables sont dans [core/exceptions.py](core/exceptions.py).

Le handler global DRF est dans [core/handlers.py](core/handlers.py).

## Dependances ajoutees

La dependance suivante a ete ajoutee dans [requirements.txt](requirements.txt):

- `django-ratelimit`

## Appwrite Cloud

Le backend cible maintenant Appwrite Cloud au lieu d'une instance locale Docker.

Variables importantes:

- `APPWRITE_ENDPOINT=https://<your-region>.cloud.appwrite.io/v1`
- `APPWRITE_PROJECT_ID=<your-project-id>`
- `APPWRITE_API_KEY=<server-api-key>`
- `APPWRITE_DB_ID=sgep_db`
- `MEDICAL_ENCRYPTION_KEY=<fernet-key>`

Le guide d'integration se trouve dans [docs/appwrite-cloud-integration.md](docs/appwrite-cloud-integration.md).

## Documentation API (Swagger)

La documentation interactive OpenAPI est disponible via **drf-spectacular** :

| URL | Interface |
|-----|-----------|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | Schéma OpenAPI brut |

Guide complet : [docs/swagger.md](docs/swagger.md)

Pour s'authentifier dans Swagger UI : login via `POST /api/v1/auth/login/`, puis **Authorize** avec `Bearer <access_token>`.

Générer le schéma en fichier :

```bash
python manage.py spectacular --color --file schema.yml
```

## Tests

Des tests API cibles ont ete ajoutes dans [accounts/tests.py](accounts/tests.py).

Ils couvrent:

- login
- refresh
- logout
- change-password
- service d'auth avec tokens JWT reels

Les tests utilisent des mocks pour isoler Appwrite et verifier le comportement de chaque endpoint sans backend externe.

## Commandes utiles

### Activation de l'environnement Anaconda

```bash
source /home/atangana/anaconda3/etc/profile.d/conda.sh
conda activate base
```

### Lancer les tests cibles

```bash
/home/atangana/anaconda3/bin/conda run -p /home/atangana/anaconda3 --no-capture-output python manage.py test accounts.tests.AuthApiTests -v 2
```

### Lancer tous les tests

```bash
/home/atangana/anaconda3/bin/conda run -p /home/atangana/anaconda3 --no-capture-output python manage.py test -v 2
```

### Demarrer le serveur Django

```bash
/home/atangana/anaconda3/bin/conda run -p /home/atangana/anaconda3 --no-capture-output python manage.py runserver
```

### Verifier les erreurs Python / Django

```bash
/home/atangana/anaconda3/bin/conda run -p /home/atangana/anaconda3 --no-capture-output python manage.py check
```

### Installer les dependances

```bash
/home/atangana/anaconda3/bin/conda run -p /home/atangana/anaconda3 --no-capture-output pip install -r requirements.txt
```

## Variables d'environnement

Variables attendues par la configuration:

```env
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=
CORS_ALLOWED_ORIGINS=

APPWRITE_ENDPOINT=https://<your-region>.cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=
APPWRITE_API_KEY=
APPWRITE_DB_ID=sgep_db
MEDICAL_ENCRYPTION_KEY=

REDIS_URL=redis://redis:6380/0
CELERY_BROKER_URL=redis://redis:6380/1

EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

JWT_ACCESS_TOKEN_LIFETIME=900
JWT_REFRESH_TOKEN_LIFETIME=604800
```

## Notes d'implementation

- Le code source du backend utilise la structure reelle `accounts/` a la racine du depot.
- La persistance metier ne passe pas par `django.contrib.auth` ni par l'ORM SQL de Django.
- Simple JWT sert uniquement a produire et valider les tokens.
- Appwrite stocke les users et la blacklist des refresh tokens.
