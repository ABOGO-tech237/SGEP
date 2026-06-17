# Module Presence

Ce document resume le module `attendance` du backend SGEP.

## Objectif

Le module presence est volontairement simple.
Les enseignants n'ont pas acces a l'application.
Les absences sont saisies par le SuperAdmin apres declaration verbale ou ecrite de l'enseignant.

## Architecture

Le module respecte le flux impose par le projet:

`View DRF -> Service -> Repository -> Appwrite SDK`

Les vues ne contiennent pas de logique metier. Elles valident l'entree via les serializers puis deleguent au service.

## Collection Appwrite

- `attendance`

Champs utilises par le code:

- `student_id`
- `class_id`
- `date`
- `type` (`absence` ou `retard`)
- `motif`
- `is_justified`
- `justification_motif`
- `justification_doc`
- `is_deleted`

## Repository

Fichier: [attendance/repository.py](../attendance/repository.py)

Methodes:

- `list(class_id, student_id, date_from, date_to)`
- `create(data)`
- `update(record_id, data)`
- `get_stats(class_id, period)`

Role:

- interroger Appwrite
- normaliser les documents retournes
- garder tout l'acces donnees au meme endroit

## Service

Fichier: [attendance/services.py](../attendance/services.py)

Methodes:

- `record_absence(student_id, class_id, date, absence_type, motif)`
- `justify(record_id, motif, justification_doc)`
- `get_stats(class_id, date_from, date_to)`
- `export(class_id, date_from, date_to, export_format, requested_by)`

Comportement:

- `record_absence` cree l'enregistrement puis declenche `notify_parent_absence_task`
- `justify` marque l'absence comme justifiee
- `get_stats` calcule un taux d'absenteisme par eleve sur la plage demandee
- `export` cree un `report_job` puis lance la tache Celery adaptee au format

## Serializers

Fichier: [attendance/serializers.py](../attendance/serializers.py)

Serializers exposes:

- `AttendanceSerializer`
- `AttendanceCreateSerializer`
- `AttendanceUpdateSerializer`
- `AttendanceJustifySerializer`
- `AttendanceQuerySerializer`
- `AttendanceStatsQuerySerializer`
- `AttendanceExportQuerySerializer`

Role:

- valider les filtres de recherche
- valider la creation d'une absence
- valider la justification
- valider la demande d'export

## Views et routes

Fichier: [attendance/views.py](../attendance/views.py)
Fichier: [attendance/urls.py](../attendance/urls.py)

Toutes les routes sont protegees par `IsSuperAdmin`.

### Endpoints

- `GET /api/v1/attendance/`
- `POST /api/v1/attendance/`
- `PUT /api/v1/attendance/{id}/`
- `POST /api/v1/attendance/{id}/justify/`
- `GET /api/v1/attendance/stats/`
- `GET /api/v1/attendance/export/`

## Taches Celery

Fichier: [attendance/tasks.py](../attendance/tasks.py)

Taches disponibles:

- `notify_parent_absence_task(student_id, date, absence_type)`
- `export_attendance_pdf_task(job_id, class_id, date_from, date_to)`
- `export_attendance_excel_task(job_id, class_id, date_from, date_to)`

Elles suivent le principe du projet:

- aucune generation lourde dans la request/response
- mise a jour du `report_job`
- retour du `job_id` cote API

## Donnees de calcul

### Statistiques

`get_stats(class_id, date_from, date_to)`:

- compte les absences par eleve
- compte les retards par eleve
- calcule le nombre de jours ouvrables entre les deux dates
- retourne un taux `absence_rate` par eleve

### Export

`export/?format=pdf|excel`:

- cree un job asynchrone
- `pdf` genere un fichier PDF via WeasyPrint
- `excel` genere un fichier XLSX via pandas/openpyxl

## Exemple d'usage

### Enregistrer une absence

```http
POST /api/v1/attendance/
Content-Type: application/json

{
  "student_id": "stu_123",
  "class_id": "cls_001",
  "date": "2026-05-18",
  "type": "absence",
  "motif": "Maladie"
}
```

### Justifier une absence

```http
POST /api/v1/attendance/rec_123/justify/
Content-Type: application/json

{
  "motif": "Certificat medical fourni",
  "justification_doc": "https://..."
}
```

### Obtenir les statistiques

```http
GET /api/v1/attendance/stats/?class_id=cls_001&date_from=2026-05-01&date_to=2026-05-31
```

### Lancer un export

```http
GET /api/v1/attendance/export/?class_id=cls_001&date_from=2026-05-01&date_to=2026-05-31&format=pdf
```

## Points a retenir

- le module reste sans ORM Django
- tout passe par Appwrite
- les notifications parent sont declenchees en asynchrone
- l'API reste reservee au SuperAdmin
