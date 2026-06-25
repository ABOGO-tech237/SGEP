# Authentification - Appwrite Integration

## Statut ✅

Utilisateurs superadmin et comptable créés et liés à la base de données Appwrite.

### Utilisateurs créés
- **Superadmin**: admin_auth@sgep.cm (ID: 6a11d268985d90d20c82)
- **Comptable**: comptable_auth@sgep.cm (ID: 6a11d26fa28eb446e8a8)

## Architecture

### Services créés

**1. AppwriteAuthService** (`accounts/auth_service.py`)
- `create_user_account()` - Crée un compte Appwrite Auth
- `create_user_with_auth()` - Crée user + auth en même temps
- `update_user_password()` - Met à jour le mot de passe
- `delete_user_account()` - Supprime un compte
- `get_user()` - Récupère un utilisateur

**2. Management Command** (`accounts/management/commands/create_admin_users.py`)
```bash
python manage.py create_admin_users \
  --superadmin-email admin@sgep.cm \
  --superadmin-password MyPassword123! \
  --comptable-email comptable@sgep.cm \
  --comptable-password MyPassword123!
```

### Authentication Flow

1. **User Registration**: Crée document dans collection `users`
2. **User Login**: 
   - Récupère email/password
   - Cherche l'utilisateur dans la collection `users`
   - Compare le mot de passe hashé (Django hashers)
   - Génère JWT token (rest_framework_simplejwt)
3. **Token Validation**: Utilise `AppwriteJWTAuthentication`

## Endpoints API

- `POST /api/accounts/login/` - Login
- `POST /api/accounts/refresh/` - Refresh token
- `POST /api/accounts/logout/` - Logout
- `POST /api/accounts/change-password/` - Change password

## Prochaines étapes

### Option 1: Utiliser Appwrite Auth natif ⭐ Recommandé
```python
from config.appwrite_client import users

# Créer un compte Auth
auth_user = users.create(
    user_id="unique()",
    email="user@example.com",
    password="password123"
)

# Créer session
session = users.create_session(auth_user["$id"], "password")
```

**Avantages:**
- Authentification native sécurisée
- Gestion des sessions par Appwrite
- 2FA et autres features

### Option 2: Améliorer le système actuel
- Ajouter l'attribut `password` au schéma Users
- Continuer avec JWT local

**Étapes:**
1. Supprimer la collection Users
2. Recréer avec l'attribut password
3. Migrer les données

## Fichiers créés

```
backend/
├── accounts/
│   ├── auth_service.py                      # Service d'authentification
│   ├── management/
│   │   └── commands/
│   │       └── create_admin_users.py        # Command pour créer admins
│   └── authentication.py                    # JWT Authentication class
├── create_admin_users.py                    # Script de setup
├── setup_auth_users.py                      # Script d'initialisation
├── test_auth_login.py                       # Tests de login
└── config/
    └── appwrite_client.py                   # Client Appwrite configuré
```

## Test d'authentification

```bash
# Créer les utilisateurs
python create_admin_users.py

# Tester le login
python test_auth_login.py

# Ou manuellement
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin_auth@sgep.cm",
    "password": "AdminPassword123!"
  }'
```

## Limitations actuelles

⚠️ **Les utilisateurs créés n'ont pas encore de mots de passe stockés** car l'attribut password n'existe pas dans le schéma de la collection Users.

### Workarounds:
1. Recréer la base de données avec le nouvel attribut
2. Utiliser Appwrite Auth natif pour gérer les passwords
3. Créer une table séparée pour les credentials

## Notes de sécurité

✅ **Implémenter:**
- Rate limiting sur login (déjà en place: 5/10m)
- CSRF protection
- Password complexity validation
- Session expiry
- Audit logging

❌ **À améliorer:**
- Store des tokens en Redis pour invalidation rapide
- 2FA support
- OAuth integration
