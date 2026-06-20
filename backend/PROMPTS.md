# PROMPTS.md — SGEP

Prompts prêts à l'emploi pour Cursor. Chaque prompt est autonome : colle-le directement dans le chat Cursor sans modification.

---

## SETUP

### P-01 — Initialiser le projet Django

```
Lis AGENT.md en entier.

Initialise le projet Django SGEP avec cette structure :
- Django 5.2 LTS
- Crée config/settings.py avec toutes les variables d'environnement listées dans AGENT.md (python-decouple pour les lire)
- Crée config/urls.py avec le préfixe /api/v1/
- Crée config/celery.py avec la configuration Celery (broker Redis)
- Crée config/appwrite_client.py exactement comme dans AGENT.md
- Crée apps/core/exceptions.py avec NotFoundError, ConflictError, AccountSuspendedError
- Crée apps/core/handlers.py avec le custom_exception_handler DRF
- Crée requirements.txt avec toutes les dépendances du stack AGENT.md
- Crée Dockerfile (Python 3.12-slim, gunicorn)
- Crée docker-compose.yml avec les services : api, celery, celery-beat, redis

Ne génère pas de frontend. Pas de models.py. Pas de migrations.
```

---

### P-02 — Créer les collections Appwrite

```
Lis AGENT.md.

Crée un script Python apps/core/management/commands/setup_appwrite.py
C'est une commande Django (manage.py) qui initialise toutes les collections
Appwrite listées dans AGENT.md.

Pour chaque collection, créer :
- La collection avec son ID exact (snake_case)
- Les attributs correspondants au schéma du CDC
- Les index sur les champs fréquemment filtrés (is_active, is_deleted, academic_year_id, class_id)

Utiliser uniquement le SDK python-arango — NON, utiliser le SDK appwrite Python
et databases.create_collection(), databases.create_string_attribute(), etc.

La commande doit être idempotente : si la collection existe déjà, la sauter sans erreur.
Afficher un log clair pour chaque collection créée ou sautée.
```

---

## MODULE ACCOUNTS (Auth)

### P-03 — Authentification JWT complète

```
Lis AGENT.md.

Dans apps/accounts/, implémente l'authentification complète :

1. Modèle utilisateur custom (AbstractBaseUser) avec les champs :
   - id (UUID), email, role (superadmin/comptable/parent), account_status (active/suspended)
   - student_id (nullable, pour les parents)
   - Pas de username, email est le login

2. Repository apps/accounts/repository.py qui lit/écrit les users dans la collection Appwrite `users`

3. Endpoints :
   - POST /api/v1/auth/login/ → retourne access_token + refresh_token
   - POST /api/v1/auth/refresh/ → renouvelle l'access token
   - POST /api/v1/auth/logout/ → blackliste le refresh token (écriture dans collection `refresh_token_blacklist`)
   - POST /api/v1/auth/change-password/

4. Classes de permission dans apps/accounts/permissions.py exactement comme dans AGENT.md

5. Rate limiting sur /auth/login/ : 5 tentatives / 10 min (utiliser django-ratelimit)

Pas de django.contrib.auth pour la persistance — les users sont dans Appwrite.
Simple JWT est utilisé uniquement pour générer/valider les tokens.
```

---

## MODULE STUDENTS

### P-04 — CRUD élèves complet

```
Lis AGENT.md.

Dans apps/students/, implémente le module élèves complet :

Repository (apps/students/repository.py) :
- list(class_id, academic_year_id, is_active, search) avec Query Appwrite
- get(student_id)
- create(data)
- update(student_id, data)
- soft_delete(student_id)

Service (apps/students/services.py) :
- Méthode create() qui après création de l'élève, déclenche automatiquement
  la création du compte parent (appel à ParentAccountService.create_from_student())
- Méthode promote(student_id, target_class_id) pour le passage en classe supérieure
- Méthode list() avec filtres et pagination

Serializers :
- StudentSerializer (lecture complète)
- StudentCreateSerializer (création/modification, validation matricule unique)
- StudentListSerializer (liste allégée)

Views DRF (permission IsSuperAdmin) :
- GET/POST /api/v1/students/
- GET/PATCH/DELETE /api/v1/students/{id}/
- GET /api/v1/students/{id}/history/
- POST /api/v1/students/{id}/enroll/
- POST /api/v1/students/{id}/promote/
- GET /api/v1/students/export/pdf/ → lance tâche Celery, retourne job_id
- GET /api/v1/students/export/excel/ → lance tâche Celery, retourne job_id

Le champ `medical` doit être un sous-objet JSON stocké comme string chiffrée
(utiliser cryptography.fernet, clé dans settings.MEDICAL_ENCRYPTION_KEY).
```

---

### P-05 — Création automatique du compte parent

```
Lis AGENT.md.

Dans apps/parents/services.py, implémente ParentAccountService :

Méthode create_from_student(student_id, guardians: list[dict]) :
1. Pour chaque tuteur dans la liste :
   - Vérifier si un compte parent existe déjà avec cet email (éviter les doublons)
   - Sinon : créer un document dans la collection `users` avec role=parent, account_status=active
   - Générer un mot de passe temporaire (12 caractères aléatoires)
   - Créer le lien dans la collection `parent_student`
   - Déclencher la tâche Celery send_parent_credentials_task(parent_id, email, temp_password)

Méthode suspend(student_id) :
- Trouver tous les comptes parent liés à cet élève
- Mettre account_status=suspended sur chaque compte
- Déclencher send_account_suspended_notification_task()

Méthode reactivate(student_id) :
- Mettre account_status=active
- Déclencher send_account_reactivated_notification_task()

La tâche Celery de suspension des comptes doit aussi être déclenchée automatiquement
au début de chaque nouvelle année scolaire (Celery beat, tâche périodique).
```

---

## MODULE GRADES

### P-06 — Saisie des notes et calcul des moyennes

```
Lis AGENT.md.

Dans apps/grades/, implémente le module notes :

Repository :
- list(class_id, subject_id, period_id, student_id)
- bulk_create(grades: list[dict]) → création en masse via Appwrite batch
- update(grade_id, data)

Service :
- Méthode calculate_averages(class_id, period_id) :
  * Récupère toutes les notes de la classe pour la période
  * Calcule la moyenne pondérée par élève (coefficient par matière)
  * Calcule le rang (avec ex-aequo partagé)
  * Retourne un dict {student_id: {average, rank, subject_averages}}

- Méthode bulk_input(validated_data: list) → appelle bulk_create du repository

Serializers :
- GradeSerializer
- GradeCreateSerializer (student_id, subject_id, period_id, value requis ; value entre 0 et 20)
- BulkGradeCreateSerializer (liste de GradeCreateSerializer)

Views (permission IsSuperAdmin) :
- GET /api/v1/grades/?class_id=&subject_id=&period_id=
- POST /api/v1/grades/
- PUT /api/v1/grades/{id}/
- POST /api/v1/grades/bulk/
```

---

### P-07 — Génération des bulletins PDF

```
Lis AGENT.md.

Implémente la génération des bulletins PDF via WeasyPrint + Celery :

1. Template PDF : apps/grades/templates/pdf/report_card.html
   - Design sobre : en-tête école, nom élève, classe, période
   - Tableau notes par matière (matière, note/20, coefficient, moyenne pondérée, appréciation)
   - Moyenne générale, rang, appréciation générale
   - Signature directeur (placeholder)
   - CSS inline compatible WeasyPrint

2. Fonction apps/grades/pdf.py → generate_report_card_pdf(student, grades, period, school) → str (chemin fichier)

3. Tâche Celery apps/grades/tasks.py → generate_class_report_cards_task(class_id, period_id, job_id) :
   - Pour chaque élève de la classe :
     * Récupère les notes via GradeRepository
     * Calcule les moyennes via GradeService.calculate_averages()
     * Génère le PDF
     * Crée un document dans report_cards avec le chemin du fichier
   - Met à jour le report_job (status=done)

4. Endpoints :
   - POST /api/v1/report-cards/generate/ → body: {class_id, period_id} → retourne {job_id}
   - GET /api/v1/report-cards/{id}/status/ → retourne {status, progress}
   - GET /api/v1/report-cards/{id}/download/ → retourne FileResponse (permission: SuperAdmin ou Parent actif propriétaire)
   - POST /api/v1/report-cards/{id}/publish/ → account_status→published, déclenche notification parent
```

---

## MODULE ATTENDANCE

### P-08 — Enregistrement des absences

```
Lis AGENT.md.

Dans apps/attendance/, implémente le module présence simplifié.

Rappel architecture : les enseignants n'ont pas accès à l'application.
Les absences sont saisies par le SuperAdmin sur déclaration verbale/écrite de l'enseignant.

Repository :
- list(class_id, student_id, date_from, date_to)
- create(data)
- update(record_id, data)
- get_stats(class_id, period) → agrégation par élève

Service :
- Méthode record_absence(student_id, class_id, date, absence_type, motif) :
  * Crée l'enregistrement
  * Déclenche notify_parent_absence_task(student_id, date, absence_type)

- Méthode justify(record_id, motif, justification_doc) :
  * Met à jour is_justified=True, justification_motif

- Méthode get_stats(class_id, date_from, date_to) :
  * Calcule taux d'absentéisme par élève (nb absences / nb jours ouvrés × 100)

Endpoints (IsSuperAdmin) :
- GET /api/v1/attendance/?class_id=&student_id=&date_from=&date_to=
- POST /api/v1/attendance/ → body: {student_id, class_id, date, type: absence|retard, motif}
- PUT /api/v1/attendance/{id}/
- POST /api/v1/attendance/{id}/justify/
- GET /api/v1/attendance/stats/?class_id=&date_from=&date_to=
- GET /api/v1/attendance/export/?format=pdf|excel → lance tâche Celery
```

---

## MODULE FINANCE

### P-09 — Facturation et paiements

```
Lis AGENT.md.

Dans apps/finance/, implémente le module finance :

Repositories : FeeTypeRepository, InvoiceRepository, PaymentRepository

Service InvoiceService :
- generate_for_class(class_id, fee_type_id, academic_year_id) :
  * Récupère tous les élèves actifs de la classe
  * Pour chaque élève, crée une facture si elle n'existe pas déjà (éviter les doublons)
  * Retourne le nombre de factures créées

- generate_bulk(academic_year_id, fee_type_id) → même logique pour toute l'école

Service PaymentService :
- record(invoice_id, amount, method, reference) :
  * Vérifie que la facture n'est pas déjà soldée
  * Crée le paiement
  * Si montant total payé >= montant facture → met invoice.status=paid
  * Déclenche generate_receipt_task(payment_id)

- Tâche Celery generate_receipt_task(payment_id) :
  * Génère un PDF reçu via WeasyPrint
  * Met à jour payment.receipt_path

Tâche Celery périodique (Celery beat) send_overdue_reminders_task() :
- Chaque jour à 8h : trouve les factures impayées dépassées de 7, 15, 30 jours
- Envoie un email de relance au parent via Django send_mail()

Endpoints :
- GET/POST /api/v1/finance/invoices/
- POST /api/v1/finance/invoices/generate/ (IsSuperAdmin + IsComptable)
- POST /api/v1/finance/payments/ (IsComptable)
- GET /api/v1/finance/payments/{id}/receipt/ → FileResponse PDF
- GET /api/v1/finance/overdue/
- GET /api/v1/finance/dashboard/ → {total_billed, total_collected, recovery_rate, overdue_count}
- GET /api/v1/finance/export/excel/ → lance tâche Celery, retourne job_id
```

---

## MODULE PARENTS

### P-10 — Portail parent

```
Lis AGENT.md.

Dans apps/parents/views.py, implémente tous les endpoints du portail parent.

Règle de permission :
- IsActiveParent → accès complet (notes, bulletins, absences, messages)
- IsParentAny → accès restreint (factures, reçus uniquement) même si suspendu

Endpoints :
- GET /api/v1/parent/me/ → profil + statut compte (IsParentAny)
- GET /api/v1/parent/me/student/ → infos élève lié (IsActiveParent)
- GET /api/v1/parent/me/grades/?period_id= (IsActiveParent)
- GET /api/v1/parent/me/attendance/ (IsActiveParent)
- GET /api/v1/parent/me/report-cards/ (IsActiveParent)
- GET /api/v1/parent/me/report-cards/{id}/download/ (IsActiveParent)
- GET /api/v1/parent/me/invoices/ (IsParentAny)
- GET /api/v1/parent/me/invoices/{id}/receipt/ (IsParentAny)
- GET/POST /api/v1/parent/me/messages/ (IsActiveParent)

Pour chaque endpoint IsActiveParent : si le compte est suspendu, retourner 403 AccountSuspendedError
avec le message "Compte suspendu. Veuillez contacter l'administration pour renouveler l'inscription."

Le parent ne peut accéder qu'aux données de son propre enfant.
Vérifier systématiquement que request.user.student_id correspond à la ressource demandée.
```

---

## MODULE RAPPORTS

### P-11 — Export Excel avec pandas

```
Lis AGENT.md.

Dans apps/reports/excel.py, implémente les fonctions d'export Excel :

1. export_students(academic_year_id, class_id=None) → str (chemin fichier) :
   - Colonnes : Matricule, Nom, Prénom, Date naissance, Classe, Niveau, Tuteur principal, Téléphone
   - Une ligne par élève, trié par classe puis par nom
   - En-tête en gras, colonne classe avec fond coloré par niveau

2. export_results(class_id, period_id) → str :
   - Colonnes : Matricule, Nom, Prénom, + une colonne par matière (note/20), Moyenne générale, Rang
   - Ligne totale avec la moyenne de classe par matière
   - Mise en forme : notes < 10 en rouge, >= 10 en vert

3. export_finance(academic_year_id, date_from=None, date_to=None) → str :
   - Colonnes : Élève, Type frais, Montant facturé, Montant payé, Solde, Statut, Date dernier paiement
   - Onglet 1 : détail par élève, Onglet 2 : récapitulatif par type de frais

4. export_attendance(class_id, date_from, date_to) → str :
   - Colonnes : Nom élève, Nb absences, Nb retards, Nb absences justifiées, Taux absentéisme %

Chaque fonction sauvegarde dans /srv/sgep/media/exports/ et retourne le chemin absolu.
Utiliser openpyxl pour la mise en forme (couleurs, gras) via pd.ExcelWriter.
```

---

## NOTIFICATIONS

### P-12 — Tâches de notification Celery

```
Lis AGENT.md.

Dans apps/notifications/tasks.py, implémente toutes les tâches de notification :

1. notify_parent_absence_task(student_id, date, absence_type) :
   - Récupère le parent lié à student_id
   - Envoie email via Django send_mail()
   - Log dans collection `notifications` (status=sent ou failed)

2. notify_bulletin_published_task(student_id, period_label) :
   - Email au parent : "Le bulletin de [prénom] est disponible"

3. notify_payment_overdue_task(invoice_id, overdue_days) :
   - Email de relance avec le montant dû et la date d'échéance dépassée

4. send_parent_credentials_task(parent_id, email, temp_password) :
   - Email de bienvenue avec identifiants de connexion
   - Rappel de changer le mot de passe à la première connexion

5. notify_account_suspended_task(parent_id) :
   - Email informant que le compte est suspendu en attente de réinscription

6. notify_account_reactivated_task(parent_id) :
   - Email confirmant la réactivation du compte

Chaque tâche :
- A un max_retries=3 avec countdown=120 en cas d'échec SMTP
- Crée/met à jour un document dans la collection `notifications` (status, sent_at, error)
- Accepte un paramètre dry_run=False pour les tests sans envoi réel
```

---

## AUDIT

### P-13 — Journal d'audit

```
Lis AGENT.md.

Crée apps/core/audit.py avec une fonction log_action() :

def log_action(
    user_id: str,
    action: str,          # CREATE | UPDATE | DELETE
    collection: str,
    document_id: str,
    diff: dict,
    ip_address: str
) -> None

Cette fonction :
- Crée un document dans la collection Appwrite `audit_logs`
- Est appelée dans les services pour les collections sensibles :
  students, grades, report_cards, payments, users

Crée un middleware Django apps/core/middleware.py → AuditMiddleware :
- Injecte l'IP réelle (X-Forwarded-For si présent, sinon REMOTE_ADDR) dans request.audit_ip
- Ce middleware est ajouté dans settings.MIDDLEWARE

Dans StudentService.create(), StudentService.update(), GradeService.bulk_input(),
PaymentService.record() : appeler log_action() après chaque opération réussie.
```

Lis Agent.md et le Readme.md

La cofiguration actuele utlise appwrite en locale, on modifie tous les fichiers pour utilser appwrite en ligne, 
 je parle de : 
         -backend/config/appwrite_client.py
         -backend/config/settings.py
         -backend/core/management/commands/setup_appwrite.py
c'est configuer pour utiliser appwrite en local via docker 
ce que tu fais :
   tu lis la documentation de appwrite
   tu adaptes le code existant pour que ça utilise le appwrite en ligne 
   tu mets à jours le readme 
   tu crée un doculent d'intégration pour appwrite en ligne 
   tu mets à jour les fichiers .env      

