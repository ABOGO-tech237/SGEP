# SGEP

Système de Gestion d'École Primaire adapté au contexte camerounais.

Backend Django REST exposant une API versionnée (`/api/v1/`). La persistance métier passe par **Appwrite Cloud** ; l'authentification utilise **Simple JWT** (tokens émis et validés côté Django, users stockés dans Appwrite).

## Architecture

```
View DRF → Service → Repository → Appwrite SDK
```

Les vues ne parlent jamais directement à Appwrite. Les opérations lourdes (PDF, Excel, emails) sont déléguées à **Celery**.

### Modules

| Module | Rôle |
|--------|------|
| `accounts/` | Auth JWT, rôles, blacklist refresh tokens |
| `core/` | Écoles, années scolaires, audit, middleware IP, OpenAPI |
| `classes/` | Classes et matières |
| `students/` | Élèves, inscriptions, promotions, exports |
| `attendance/` | Absences, retards, statistiques, exports |
| `grades/` | Notes, bulletins PDF, export résultats Excel |
| `finance/` | Factures, paiements, reçus, tableau de bord |
| `parents/` | Portail parent, messagerie, suspension comptes |
| `notifications/` | Tâches Celery email (absences, bulletins, relances) |
| `reports/` | Jobs d'export async, Excel formaté (openpyxl) |

## Authentification

Endpoints : `POST /api/v1/auth/login/`, `refresh/`, `logout/`, `change-password/`.

Rôles : `superadmin`, `comptable`, `parent`. Permissions DRF dans `accounts/permissions.py`.

## Endpoints principaux

### Core
- `GET/POST /api/v1/schools/`
- `GET/PATCH /api/v1/schools/<id>/`
- `GET/POST /api/v1/academic-years/`
- `GET/PATCH /api/v1/academic-years/<id>/`

### Classes
- `GET/POST /api/v1/classes/`
- `GET/PATCH /api/v1/classes/<id>/`
- `GET/POST /api/v1/subjects/`
- `GET/PATCH /api/v1/subjects/<id>/`

### Students
- CRUD élèves, inscription, promotion, historique
- Exports PDF/Excel asynchrones (`202` + `job_id`)

### Attendance
- CRUD absences, justification, statistiques, export

### Grades & bulletins
- CRUD notes, saisie en masse
- Génération bulletins PDF (`report-cards/generate/`)
- Export résultats Excel (`grades/export/results/`)

### Finance
- Factures, paiements, reçus, dashboard, relances automatiques (7/15/30 j)

### Parent portal (`/api/v1/parent/me/...`)
- Profil, élève, notes, absences, bulletins, factures, messagerie

### Reports (jobs async)
- `GET /api/v1/reports/<job_id>/status/`
- `GET /api/v1/reports/<job_id>/download/`

### Admin
- `GET /api/v1/admin/dashboard/` — tableau de bord (stats élèves, classes, finance, activité)

## Documentation API (Swagger)

| URL | Interface |
|-----|-----------|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | Schéma OpenAPI |

Guide : [docs/swagger.md](docs/swagger.md)

```bash
python manage.py spectacular --color --file schema.yml
```

## Appwrite Cloud

Variables : voir [.env.example](.env.example). Guide : [docs/appwrite-cloud-integration.md](docs/appwrite-cloud-integration.md).

Initialiser les collections :

```bash
python manage.py setup_appwrite
```

## Tâches Celery

| Tâche | Déclencheur |
|-------|-------------|
| Exports Excel/PDF | Endpoints export (`job_id`) |
| Relances factures | Beat quotidien 8h (paliers 7/15/30 j) |
| Suspension parents inactifs | Beat annuel 1er septembre |
| Notifications email | Absences, bulletins, credentials, suspension |

## Tests

Environnement **Anaconda base** uniquement :

```bash
cd backend
/home/atangana/anaconda3/bin/python manage.py test -v 2
```

Modules couverts : `accounts`, `students`, `attendance`, `grades`, `finance`, `parents`, `core`, `classes`, `reports`.

### Tests d'intégration Appwrite Cloud

Guide complet : [docs/appwrite-integration-tests.md](docs/appwrite-integration-tests.md)

```bash
# Vérifier la connexion
/home/atangana/anaconda3/bin/python manage.py verify_appwrite

# Tests live (ignorés si .env contient des placeholders)
/home/atangana/anaconda3/bin/python manage.py test core.tests_appwrite_integration -v 2
```

## Commandes utiles

```bash
# Activer conda base
source /home/atangana/anaconda3/etc/profile.d/conda.sh
conda activate base

# Vérifier la config Django
/home/atangana/anaconda3/bin/python manage.py check

# Démarrer le serveur
/home/atangana/anaconda3/bin/python manage.py runserver
```

## Variables d'environnement

Copier `.env.example` vers `.env` et renseigner les valeurs Appwrite, Redis et email.

```env
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=
APPWRITE_API_KEY=
APPWRITE_DB_ID=sgep_db
```

## Références

- [AGENT.md](AGENT.md) — règles d'architecture et conventions
- [PROMPTS.md](PROMPTS.md) — phases d'implémentation
