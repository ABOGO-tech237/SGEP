from datetime import timedelta
import os
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent


def _apply_env_file(path: Path, *, override: bool) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if override or key not in os.environ:
            os.environ[key] = value


_apply_env_file(BASE_DIR / ".env", override=False)
_apply_env_file(BASE_DIR / ".env.local", override=True)

SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-me")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    # Never expose tracebacks on Render, even if DEBUG=True is set in the dashboard.
    DEBUG = False
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS = [*ALLOWED_HOSTS, RENDER_EXTERNAL_HOSTNAME]

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=Csv())

APPWRITE_ENDPOINT = config("APPWRITE_ENDPOINT", default="https://cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = config("APPWRITE_PROJECT_ID", default="6a11ae3d002ce9eb8fd1")
APPWRITE_API_KEY = config("APPWRITE_API_KEY", default="standard_5ef1fff1a4548cc16fb170c2dffe6cf95682ec21c3a9b880cbb08c0837911dc889af2bc915ee35d8571db60e44bf2eb213c1959b53118dcfabbff223a820e3a1f453d65c429d7ae1446e46e6fbe95988ea64f522584880741b1786b580992c864198b8875bfe2e664ec27ee1f7c897313c83d60cbcb7515555d64c9e4828057a")
APPWRITE_DB_ID = config("APPWRITE_DB_ID", default="6a11c3230008da841ac7")
MEDICAL_ENCRYPTION_KEY = config("MEDICAL_ENCRYPTION_KEY", default="")

REDIS_URL = config("REDIS_URL", default="redis://redis:6380/0")
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://redis:6380/1")

EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="")

JWT_ACCESS_TOKEN_LIFETIME = config("JWT_ACCESS_TOKEN_LIFETIME", default=900, cast=int)
JWT_REFRESH_TOKEN_LIFETIME = config("JWT_REFRESH_TOKEN_LIFETIME", default=604800, cast=int)

# One-time bootstrap: POST /api/v1/auth/bootstrap/ with X-Bootstrap-Token header.
# Leave empty in production after creating the first admin user.
BOOTSTRAP_SECRET = config("BOOTSTRAP_SECRET", default="")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_celery_beat",
    "drf_spectacular",
    "core",
    "accounts",
    "classes",
    "parents",
    "students",
    "notifications",
    "attendance",
    "grades",
    "finance",
    "reports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.AuditMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "SGEP.wsgi.application"
ASGI_APPLICATION = "SGEP.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# SQLite is kept only for Django internals (sessions/admin); business data lives in Appwrite.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
MEDICAL_ENCRYPTION_KEY = config("MEDICAL_ENCRYPTION_KEY", default="")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "accounts.authentication.AppwriteJWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.handlers.custom_exception_handler",
    "URL_FORMAT_OVERRIDE": None,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SGEP API",
    "DESCRIPTION": (
        "API REST du Système de Gestion d'École Primaire (SGEP) — contexte camerounais. "
        "Authentification JWT. Rôles : superadmin, comptable, parent."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "TAGS": [
        {"name": "Auth", "description": "Authentification JWT"},
        {"name": "Core", "description": "Écoles et années scolaires (SuperAdmin)"},
        {"name": "Classes", "description": "Classes et matières (SuperAdmin)"},
        {"name": "Students", "description": "Gestion des élèves (SuperAdmin)"},
        {"name": "Attendance", "description": "Absences et retards (SuperAdmin)"},
        {"name": "Grades", "description": "Saisie des notes (SuperAdmin)"},
        {"name": "Report Cards", "description": "Bulletins PDF (SuperAdmin / Parent)"},
        {"name": "Finance", "description": "Facturation et paiements (Comptable)"},
        {"name": "Admin", "description": "Tableau de bord administrateur (SuperAdmin)"},
        {"name": "Reports", "description": "Exports asynchrones (SuperAdmin / Comptable)"},
        {"name": "Parent Portal", "description": "Portail parent"},
    ],
    "SECURITY": [{"bearerAuth": []}],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Token JWT obtenu via POST /api/v1/auth/login/",
            }
        }
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=JWT_ACCESS_TOKEN_LIFETIME),
    "REFRESH_TOKEN_LIFETIME": timedelta(seconds=JWT_REFRESH_TOKEN_LIFETIME),
}

CELERY_BROKER_URL = CELERY_BROKER_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "suspend-inactive-parents-annual": {
        "task": "parents.tasks.suspend_inactive_parents_task",
        "schedule": crontab(minute=0, hour=0, day_of_month=1, month_of_year=9),
    },
    "send-overdue-reminders-daily": {
        "task": "finance.tasks.send_overdue_reminders_task",
        "schedule": crontab(minute=0, hour=8),
    },
}
