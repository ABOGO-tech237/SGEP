# AGENT.md — SGEP (Système de Gestion d'École Primaire)

## Rôle de l'agent

Tu es l'assistant de développement backend du SGEP. Tu travailles exclusivement sur le backend Django. Tu ne génères jamais de code frontend, jamais de templates HTML (sauf pour WeasyPrint PDF). Tu produis du code propre, testé, conforme à l'architecture définie ci-dessous.

---

## Stack technique

| Couche | Technologie | Version |
|---|---|---|
| Framework | Django | 5.2 LTS |
| API REST | Django REST Framework | 3.15+ |
| Base de données | Appwrite Cloud | latest |
| SDK Python Appwrite | appwrite | 7.0.0 |
| Cache / Broker | Redis | 7 |
| Tâches async | Celery + django-celery-beat | 5.4 |
| PDF | WeasyPrint | 62+ |
| Excel | pandas + openpyxl | 2.2+ |
| Auth | Simple JWT (DRF) | 5.x |
| Serveur | Gunicorn + Nginx | — |

---

## Architecture du projet

```
sgep/
│   ├── core/           # École, année scolaire, configuration
│   ├── accounts/       # Utilisateurs, rôles, JWT blacklist
│   ├── students/       # Élèves, tuteurs, inscriptions
│   ├── classes/        # Classes, matières, emplois du temps
│   ├── grades/         # Notes, bulletins, compétences
│   ├── attendance/     # Absences déclarées
│   ├── parents/        # Portail parent, messagerie, statut compte
│   ├── finance/        # Factures, paiements, reçus
│   └── reports/        # Exports PDF et Excel asynchrones
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── appwrite_client.py   # Client Appwrite centralisé
│   └── celery.py
└── requirements.txt
```

---

## Règles absolues
 Toujours produire un document et mettre à jour le README.md
1. **Jamais d'ORM Django** — Appwrite n'est pas une base SQL. Tous les accès aux données passent par le Repository pattern.
2. **Jamais de logique dans les views** — les views DRF appellent uniquement les services et repositories.
3. **Jamais de secret en dur dans le code** — tout passe par `django.conf.settings`.
4. **Toujours typer** — toutes les fonctions ont des type hints Python.
5. **Toujours valider** — chaque endpoint a un serializer DRF qui valide les entrées.
6. **Toujours gérer les erreurs Appwrite** — wrapper les appels SDK dans try/except `AppwriteException`.
7. **Les tâches lourdes sont asynchrones** — PDF, Excel, emails → Celery. Jamais dans la request/response.
8. **Toujours demander avant d'installer ou exécuter une commande** tu demande et on appprouve 
9. **C'est l'environnement base de anaconda qu'on utilise pas l'environnement python du système qu'on n'utilise pas** seulement l'environnement anaconda qui est utiiser pas un autre 
 
10. **Toujours documenter les routes avec swagger** 
11. **Ne Jamais créer d'environnement, jamais installer une dépendances**
---

## Appwrite — Structure des collections

**Base de données ID** : `sgep_db` (récupéré depuis `settings.APPWRITE_DB_ID`)

### Collections principales

| Collection ID | Description |
|---|---|
| `schools` | Informations de l'établissement |
| `academic_years` | Années scolaires |
| `classes` | Classes par niveau et année |
| `students` | Fiches élèves |
| `guardians` | Parents et tuteurs |
| `enrollments` | Inscription élève → classe + année |
| `users` | Comptes (SuperAdmin, Comptable, Parent) |
| `subjects` | Matières avec coefficients |
| `grades` | Notes par élève / matière / période |
| `report_cards` | Bulletins générés |
| `attendance_records` | Absences enregistrées |
| `fee_types` | Types de frais scolaires |
| `invoices` | Factures par élève |
| `payments` | Paiements enregistrés |
| `messages` | Messagerie admin ↔ parent |
| `notifications` | File de notifications |
| `report_jobs` | Tâches d'export async |
| `audit_logs` | Journal d'audit |

---

## Pattern obligatoire : Repository

Chaque application a un fichier `repository.py`. La view appelle le service, le service appelle le repository.

```
View (DRF) → Service → Repository → Appwrite SDK
```

### Template Repository

```python
# apps/<module>/repository.py
from appwrite.exception import AppwriteException
from appwrite.query import Query
from config.appwrite_client import databases
from django.conf import settings

DB_ID = settings.APPWRITE_DB_ID
COLLECTION_ID = "<nom_collection>"


class <Nom>Repository:

    @staticmethod
    def list(filters: list | None = None) -> dict:
        queries = filters or []
        try:
            return databases.list_documents(DB_ID, COLLECTION_ID, queries)
        except AppwriteException as e:
            raise

    @staticmethod
    def get(document_id: str) -> dict:
        try:
            return databases.get_document(DB_ID, COLLECTION_ID, document_id)
        except AppwriteException as e:
            raise

    @staticmethod
    def create(data: dict) -> dict:
        try:
            return databases.create_document(DB_ID, COLLECTION_ID, "unique()", data)
        except AppwriteException as e:
            raise

    @staticmethod
    def update(document_id: str, data: dict) -> dict:
        try:
            return databases.update_document(DB_ID, COLLECTION_ID, document_id, data)
        except AppwriteException as e:
            raise

    @staticmethod
    def soft_delete(document_id: str) -> dict:
        try:
            return databases.update_document(
                DB_ID, COLLECTION_ID, document_id,
                {"is_deleted": True, "deleted_at": _now()}
            )
        except AppwriteException as e:
            raise
```

---

## Pattern obligatoire : Service

```python
# apps/<module>/services.py
from .repository import <Nom>Repository
from apps.core.exceptions import NotFoundError, ConflictError


class <Nom>Service:

    @staticmethod
    def list(**kwargs) -> list[dict]:
        result = <Nom>Repository.list()
        return result["documents"]

    @staticmethod
    def get(document_id: str) -> dict:
        doc = <Nom>Repository.get(document_id)
        if not doc:
            raise NotFoundError(f"Document {document_id} introuvable.")
        return doc

    @staticmethod
    def create(validated_data: dict) -> dict:
        return <Nom>Repository.create(validated_data)
```

---

## Pattern obligatoire : View DRF

```python
# apps/<module>/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import <Nom>Service
from .serializers import <Nom>Serializer, <Nom>CreateSerializer
from apps.accounts.permissions import IsSuperAdmin


class <Nom>ListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        items = <Nom>Service.list()
        serializer = <Nom>Serializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = <Nom>CreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = <Nom>Service.create(serializer.validated_data)
        return Response(<Nom>Serializer(item).data, status=status.HTTP_201_CREATED)


class <Nom>DetailView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, pk: str):
        item = <Nom>Service.get(pk)
        return Response(<Nom>Serializer(item).data)

    def patch(self, request, pk: str):
        serializer = <Nom>CreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        item = <Nom>Service.update(pk, serializer.validated_data)
        return Response(<Nom>Serializer(item).data)

    def delete(self, request, pk: str):
        <Nom>Service.soft_delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
```

---

## Rôles et permissions

Trois rôles uniquement :

| Rôle | Constante | Accès |
|---|---|---|
| SuperAdministrateur | `ROLE_SUPERADMIN` | Tout |
| Comptable | `ROLE_COMPTABLE` | Module Finance uniquement |
| Parent | `ROLE_PARENT` | Portail parent (lecture seule, compte actif) |

### Classes de permission DRF à créer dans `apps/accounts/permissions.py`

```python
from rest_framework.permissions import BasePermission

ROLE_SUPERADMIN = "superadmin"
ROLE_COMPTABLE  = "comptable"
ROLE_PARENT     = "parent"


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == ROLE_SUPERADMIN
        )


class IsComptable(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in (ROLE_SUPERADMIN, ROLE_COMPTABLE)
        )


class IsActiveParent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == ROLE_PARENT
            and request.user.account_status == "active"
        )


class IsParentAny(BasePermission):
    """Accès parent même si compte suspendu (factures, reçus)."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == ROLE_PARENT
        )
```

---

## Gestion des erreurs

### Exceptions personnalisées dans `apps/core/exceptions.py`

```python
from rest_framework.exceptions import APIException
from rest_framework import status


class NotFoundError(APIException):
    status_code = 404
    default_code = "NOT_FOUND"


class ConflictError(APIException):
    status_code = 409
    default_code = "CONFLICT"


class AccountSuspendedError(APIException):
    status_code = 403
    default_code = "ACCOUNT_SUSPENDED"
    default_detail = "Compte parent suspendu. Veuillez renouveler l'inscription."
```

### Handler global dans `config/settings.py`

```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.core.handlers.custom_exception_handler",
}
```

---

## Tâches Celery — règles

- Tout export PDF ou Excel est une tâche Celery.
- La view crée un document `report_jobs` dans Appwrite (statut `pending`), lance la tâche, retourne le `job_id`.
- La tâche met à jour le statut (`processing` → `done` ou `failed`) et stocke le chemin du fichier généré.
- Le client poll `/reports/{job_id}/status/` puis télécharge via `/reports/{job_id}/download/`.

### Template tâche Celery

```python
# apps/reports/tasks.py
from celery import shared_task
from .repository import ReportJobRepository


@shared_task(bind=True, max_retries=3)
def generate_report_task(self, job_id: str, report_type: str, params: dict):
    try:
        ReportJobRepository.update(job_id, {"status": "processing"})
        # ... logique de génération
        file_path = _generate(report_type, params)
        ReportJobRepository.update(job_id, {"status": "done", "file_path": file_path})
    except Exception as exc:
        ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
        raise self.retry(exc=exc, countdown=60)
```

---

## Génération PDF (WeasyPrint)

```python
# apps/grades/pdf.py
from weasyprint import HTML
from django.template.loader import render_to_string
import tempfile, os


def generate_report_card_pdf(student: dict, grades: list, period: str) -> str:
    html_content = render_to_string("pdf/report_card.html", {
        "student": student,
        "grades": grades,
        "period": period,
    })
    with tempfile.NamedTemporaryFile(
        suffix=".pdf", delete=False, dir="/srv/sgep/media/bulletins/"
    ) as tmp:
        HTML(string=html_content).write_pdf(tmp.name)
        return tmp.name
```

---

## Export Excel (pandas)

```python
# apps/reports/excel.py
import pandas as pd
import tempfile


def generate_students_excel(students: list[dict]) -> str:
    df = pd.DataFrame(students, columns=[
        "matricule", "last_name", "first_name", "birth_date", "class", "level"
    ])
    with tempfile.NamedTemporaryFile(
        suffix=".xlsx", delete=False, dir="/srv/sgep/media/exports/"
    ) as tmp:
        df.to_excel(tmp.name, index=False, engine="openpyxl")
        return tmp.name
```

---

## Client Appwrite centralisé

```python
# config/appwrite_client.py
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.services.messaging import Messaging
from django.conf import settings

client = Client()
client.set_endpoint(settings.APPWRITE_ENDPOINT)
client.set_project(settings.APPWRITE_PROJECT_ID)
client.set_key(settings.APPWRITE_API_KEY)

databases  = Databases(client)
users      = Users(client)
messaging  = Messaging(client)
```

---

## Variables d'environnement requises

```env
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=
CORS_ALLOWED_ORIGINS=

APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=
APPWRITE_API_KEY=
APPWRITE_DB_ID=sgep_db

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

---

## Conventions de nommage

| Élément | Convention | Exemple |
|---|---|---|
| Fichiers Python | snake_case | `student_repository.py` |
| Classes | PascalCase | `StudentRepository` |
| Fonctions / méthodes | snake_case | `list_by_class()` |
| Collections Appwrite | snake_case | `attendance_records` |
| Champs Appwrite | snake_case | `birth_date`, `is_active` |
| Endpoints URL | kebab-case | `/report-cards/` |
| Constantes | UPPER_SNAKE | `ROLE_SUPERADMIN` |

---

## Ce que l'agent ne fait jamais

- Générer du code frontend (React, HTML hors PDF)
- Utiliser `django.db.models` — pas d'ORM SQL
- Appeler Appwrite directement dans une view (passer par le repository)
- Mettre des credentials en dur dans le code
- Créer des migrations Django (Appwrite gère le schéma)
- Lancer des opérations longues (PDF, Excel) de manière synchrone dans une view
- Ignorer la gestion des `AppwriteException`