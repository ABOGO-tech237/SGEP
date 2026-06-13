# Documentation API (Swagger / OpenAPI)

Le backend SGEP expose une documentation interactive via **drf-spectacular**.

## URLs

| URL | Description |
|-----|-------------|
| `/api/docs/` | Interface **Swagger UI** (interactive) |
| `/api/redoc/` | Interface **ReDoc** (lecture) |
| `/api/schema/` | Schéma OpenAPI 3 (JSON/YAML) |

## Authentification dans Swagger UI

1. Appeler `POST /api/v1/auth/login/` avec `email` et `password`
2. Copier la valeur de `access_token` dans la réponse
3. Cliquer sur **Authorize** en haut de Swagger UI
4. Saisir : `Bearer <access_token>`

## Tags documentés

- **Auth** — login, refresh, logout, change-password
- **Students** — CRUD élèves, export, promotion
- **Attendance** — absences, retards, stats, export
- **Grades** — notes et saisie en masse
- **Report Cards** — génération, statut, téléchargement, publication
- **Finance** — factures, paiements, dashboard (Comptable)
- **Parent Portal** — portail parent (notes, bulletins, factures…)

## Fichiers source

- Annotations : [`core/openapi.py`](../core/openapi.py)
- Serializers de réponse OpenAPI : [`core/openapi_serializers.py`](../core/openapi_serializers.py)
- Configuration : [`config/settings.py`](../config/settings.py) (`SPECTACULAR_SETTINGS`)

## Générer le schéma en CLI

```bash
python manage.py spectacular --color --file schema.yml
```

## Dépendance

```
drf-spectacular>=0.27,<1
```
