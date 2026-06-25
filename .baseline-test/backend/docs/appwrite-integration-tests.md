# Tests d'intégration Appwrite Cloud

Ce guide décrit comment exécuter les tests backend contre une instance **Appwrite Cloud** réelle.

## Prérequis

1. Un projet Appwrite Cloud créé (région + project ID)
2. Une clé API serveur avec droits lecture/écriture sur la base `sgep_db`
3. L'environnement **Anaconda base** (voir `README.md`)

## Configuration

Copier et renseigner `backend/.env` :

```env
APPWRITE_ENDPOINT=https://fra.cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=votre-project-id
APPWRITE_API_KEY=votre-cle-api-serveur
APPWRITE_DB_ID=sgep_db
MEDICAL_ENCRYPTION_KEY=votre-cle-fernet
```

Les placeholders (`<YOUR_...>`, `your-email@gmail.com`, etc.) font **ignorer** automatiquement les tests d'intégration.

## Initialisation Appwrite

```bash
cd backend
/home/atangana/anaconda3/bin/python manage.py setup_appwrite
/home/atangana/anaconda3/bin/python manage.py populate_cameroon_data
```

`setup_appwrite` est idempotent : les collections existantes sont ignorées.

## Vérifier la connexion

```bash
/home/atangana/anaconda3/bin/python manage.py verify_appwrite
```

Sortie attendue :

```
Connexion Appwrite Cloud
  Endpoint  : https://fra.cloud.appwrite.io/v1
  Project   : ...
  Database  : sgep_db
  ✓ students            12 document(s)
  ✓ users               3 document(s)
  ...
```

## Lancer les tests

### Tests unitaires (mocks, sans réseau)

```bash
/home/atangana/anaconda3/bin/python manage.py test -v 2
```

### Tests d'intégration Appwrite uniquement

```bash
/home/atangana/anaconda3/bin/python manage.py test core.tests_appwrite_integration -v 2
```

### Désactiver les tests d'intégration explicitement

```bash
APPWRITE_INTEGRATION_TESTS=false python manage.py test -v 2
```

## Scénarios couverts

| Test | Description |
|------|-------------|
| `test_list_students_collection` | Lecture paginée de la collection `students` |
| `test_student_crud_cycle` | Création → lecture → mise à jour → soft delete (nettoyage inclus) |
| `test_admin_dashboard_live` | Agrégation du tableau de bord admin depuis Appwrite |

Les tests CRUD utilisent un matricule `TEST-<uuid>` pour éviter les collisions.

## Tableau de bord administrateur

Endpoint backend :

```
GET /api/v1/admin/dashboard/
```

Permission : `IsSuperAdmin`

Réponse :

```json
{
  "generated_at": "2026-06-13T10:00:00+00:00",
  "academic_year": { "id": "...", "name": "2025-2026" },
  "stats": [
    { "label": "Total élèves", "value": "120", "change": "...", "positive": null }
  ],
  "finance": {
    "total_billed": 500000,
    "total_collected": 320000,
    "recovery_rate": 64.0,
    "overdue_count": 8
  },
  "recent_activity": [
    {
      "id": "stu-1",
      "name": "Ada Mbia",
      "action": "Inscrit",
      "grade": "CM2-A",
      "status": "PENDING",
      "time": "il y a 2 h"
    }
  ]
}
```

## Dépannage

| Erreur | Cause probable | Action |
|--------|----------------|--------|
| Tests intégration `skipped` | Placeholders dans `.env` | Renseigner les vraies valeurs Appwrite |
| `401 Unauthorized` | Clé API invalide ou expirée | Régénérer la clé serveur dans Appwrite Console |
| `Collection not found` | Schéma non initialisé | Exécuter `setup_appwrite` |
| `Attribute not found` | Schéma incomplet | Relancer `setup_appwrite` (idempotent) |
| Proxy / réseau | Environnement sandbox | Lancer avec accès réseau complet |

## Fichiers concernés

- `core/appwrite_test_utils.py` — détection configuration valide
- `core/tests_appwrite_integration.py` — tests live
- `core/management/commands/verify_appwrite.py` — diagnostic connexion
- `core/admin_dashboard_service.py` — agrégation tableau de bord
