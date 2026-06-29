"""
Idempotent Django management command to seed demo/sample data into Appwrite Cloud.

This populates every collection the admin dashboard reads from so the UI has
realistic content to interact with: schools, academic years, levels, classes,
subjects, students (varied classes/statuses), parent users, fee types, invoices,
payments, plus a sampling of grades and attendance for the reports section.

It writes through the project's existing Appwrite repositories/client and matches
the exact collection field names defined in ``setup_appwrite.py``. Re-running the
command is safe: existing records (matched on a natural key per collection) are
skipped, never duplicated.

NOTE ON THE APPWRITE SDK / SERVER COMPAT FIX
--------------------------------------------
Appwrite Cloud (fra.cloud.appwrite.io) rejects any GET request that carries a
body with HTTP 400 "request cannot have request body". The bundled appwrite
python SDK (7.1.0) serializes empty params to ``"{}"`` and sends it as a body on
GET requests, which breaks every read (list/get). We apply a small, contained
runtime shim here that strips the JSON content-type from GET requests so the SDK
sends no body. This only affects this command's process and does not modify any
existing business-logic module.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from core.appwrite_utils import documents_of, install_appwrite_get_body_shim, to_dict


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# Deterministic generator so re-runs build the same natural keys.
RNG = random.Random(20260620)

CAMEROON_FIRST_NAMES = [
    "Jean", "Marie", "Paul", "Aïcha", "Emmanuel", "Grâce", "Joseph", "Larissa",
    "Patrick", "Brenda", "Serge", "Nadège", "Hervé", "Carole", "Boris", "Estelle",
    "Cédric", "Yvette", "Armand", "Sandrine", "Franck", "Pauline", "Ulrich", "Mireille",
    "Roland", "Bernadette", "Désiré", "Solange", "Gaston", "Clarisse", "Aristide",
    "Florence", "Thierry", "Joséphine", "Bertrand", "Chantal", "Achille", "Diane",
    "Maxime", "Reine",
]

CAMEROON_LAST_NAMES = [
    "Mballa", "Nkeng", "Fotso", "Tchoua", "Ngono", "Bello", "Abena", "Etoa",
    "Mvondo", "Kamga", "Ndongo", "Essomba", "Owona", "Tabi", "Njoya", "Manga",
    "Onana", "Biya", "Atangana", "Eyenga", "Foe", "Ngo", "Simo", "Tagne",
]

BIRTH_PLACES = ["Yaoundé", "Douala", "Bafoussam", "Bamenda", "Garoua", "Buea", "Maroua", "Ebolowa"]

TEACHER_NAMES = [
    "M. Jean Mballa",
    "Mme Marie Nkeng",
    "M. Paul Fotso",
    "Mme Grâce Ngono",
    "M. Emmanuel Etoa",
    "Mme Larissa Kamga",
]

LEVELS = [
    {"code": "SIL", "name": "SIL", "cycle": "primaire", "age": 6, "language": "fr"},
    {"code": "CP", "name": "Cours Préparatoire", "cycle": "primaire", "age": 7, "language": "fr"},
    {"code": "CE1", "name": "Cours Élémentaire 1", "cycle": "primaire", "age": 8, "language": "fr"},
    {"code": "CE2", "name": "Cours Élémentaire 2", "cycle": "primaire", "age": 9, "language": "fr"},
    {"code": "CM1", "name": "Cours Moyen 1", "cycle": "primaire", "age": 10, "language": "fr"},
    {"code": "CM2", "name": "Cours Moyen 2", "cycle": "primaire", "age": 11, "language": "fr"},
]

SCHOOLS = [
    {
        "code": "EPY-CENTRE",
        "name": "École Primaire Bilingue de Yaoundé-Centre",
        "address": "Avenue Kennedy, Yaoundé",
        "phone": "+237677000001",
        "email": "contact@epy-centre.cm",
    },
    {
        "code": "EPD-AKWA",
        "name": "École Primaire de Douala-Akwa",
        "address": "Boulevard de la Liberté, Douala",
        "phone": "+237677000002",
        "email": "contact@epd-akwa.cm",
    },
]

# Subjects assigned per class (a representative selection).
CLASS_SUBJECTS = [
    {"code": "FR", "name": "Français", "coefficient": 2},
    {"code": "MATH", "name": "Mathématiques", "coefficient": 2},
    {"code": "SCI", "name": "Sciences", "coefficient": 1},
    {"code": "EN", "name": "Anglais", "coefficient": 1},
]

FEE_TYPES = [
    {"code": "INSC", "name": "Frais d'inscription", "amount": 15000.0},
    {"code": "TR1", "name": "1ère tranche", "amount": 25000.0},
    {"code": "TR2", "name": "2ème tranche", "amount": 25000.0},
    {"code": "TR3", "name": "3ème tranche", "amount": 25000.0},
    {"code": "SCOL", "name": "Frais de scolarité", "amount": 75000.0},
    {"code": "CANT", "name": "Frais de cantine", "amount": 30000.0},
    {"code": "UNIF", "name": "Uniforme scolaire", "amount": 12000.0},
    {"code": "TRANSP", "name": "Transport scolaire", "amount": 25000.0},
]

SEQUENCE_LABEL = "Séquence 1"
ATTENDANCE_STATUSES = ["PRESENT", "PRESENT", "PRESENT", "ABSENT", "RETARD", "ABSENT_JUSTIFIE"]

NUM_STUDENTS = 40
NUM_PARENTS = 15


class Command(BaseCommand):
    help = "Seed idempotent demo/sample data into Appwrite for the admin dashboard."

    def add_arguments(self, parser):
        parser.add_argument(
            "--students",
            type=int,
            default=NUM_STUDENTS,
            help="Number of demo students to ensure (default: 40).",
        )
        parser.add_argument(
            "--parents",
            type=int,
            default=NUM_PARENTS,
            help="Number of demo parent users to ensure (default: 15).",
        )

    def handle(self, *args, **options):
        install_appwrite_get_body_shim()
        self.db_id = settings.APPWRITE_DB_ID
        self.counts: dict[str, int] = {}
        self.failures: dict[str, int] = {}
        self.num_students = options["students"]
        self.num_parents = options["parents"]

        self.stdout.write(self.style.SUCCESS("Seeding SGEP demo data into Appwrite..."))

        self.recorded_by = self._find_superadmin_id()

        schools = self._seed_schools()
        primary_school = schools[0]
        secondary_school = schools[1] if len(schools) > 1 else schools[0]

        levels = self._seed_levels()
        years = self._seed_academic_years(primary_school)
        active_year = next((y for y in years if y.get("is_active")), years[-1])

        classes = self._seed_classes(levels, active_year, primary_school)
        subjects_by_class = self._seed_subjects(classes)
        students = self._seed_students(classes, active_year, primary_school)
        self._seed_parents(primary_school, secondary_school, students)
        fee_types = self._seed_fee_types(primary_school)
        invoices = self._seed_invoices(students, active_year, fee_types)
        self._seed_payments(invoices)
        self._seed_grades(students, subjects_by_class, active_year)
        self._seed_attendance(students, active_year)

        self.stdout.write(self.style.SUCCESS("\nDemo data seeding complete. Records created this run:"))
        for collection, count in self.counts.items():
            self.stdout.write(f"  {collection}: +{count}")
        if not any(self.counts.values()):
            self.stdout.write("  (nothing new — data already present)")
        if self.failures:
            self.stdout.write(self.style.WARNING("\nRecords skipped due to errors:"))
            for collection, count in self.failures.items():
                self.stdout.write(f"  {collection}: {count}")

    # ---- helpers -------------------------------------------------------

    def _bump(self, collection: str, n: int = 1) -> None:
        self.counts[collection] = self.counts.get(collection, 0) + n

    def _attrs(self, collection_id: str) -> set[str]:
        """Return the set of attribute keys that actually exist on a collection.

        The deployed Appwrite schema can drift from setup_appwrite.py, so we
        introspect the live collection and only write known attributes.
        """
        cache = getattr(self, "_attr_cache", None)
        if cache is None:
            cache = {}
            self._attr_cache = cache
        if collection_id not in cache:
            from config.appwrite_client import databases

            try:
                response = databases.list_attributes(self.db_id, collection_id)
                cache[collection_id] = {
                    a.get("key") for a in response.get("attributes", []) if a.get("key")
                }
            except Exception:
                cache[collection_id] = set()
        return cache[collection_id]

    def _list_all(self, collection_id: str) -> list[dict]:
        """Return ALL non-deleted documents in a collection (paginated).

        The project repositories call list_documents without a limit, so
        Appwrite caps results at 25. For idempotency we must see every existing
        record, so we paginate explicitly here.
        """
        from appwrite.query import Query

        from config.appwrite_client import databases

        out: list[dict] = []
        offset = 0
        page_size = 100
        while True:
            response = databases.list_documents(
                self.db_id,
                collection_id,
                [Query.limit(page_size), Query.offset(offset)],
            )
            docs = documents_of(response)
            out.extend(_with_id(d) for d in docs)
            if len(docs) < page_size:
                break
            offset += page_size
        return out

    def _filter(self, collection_id: str, payload: dict) -> dict:
        """Drop keys not present in the live collection schema."""
        known = self._attrs(collection_id)
        if not known:
            return dict(payload)
        return {k: v for k, v in payload.items() if k in known}

    def _safe_create(self, collection_id: str, create_fn, payload: dict) -> dict | None:
        """Filter payload to known attributes and create, surviving per-record errors."""
        filtered = self._filter(collection_id, payload)
        try:
            doc = create_fn(filtered)
            self._bump(collection_id)
            return to_dict(doc)
        except Exception as exc:  # noqa: BLE001 - keep seeding the rest
            self.failures[collection_id] = self.failures.get(collection_id, 0) + 1
            self.stdout.write(self.style.WARNING(f"    skip {collection_id}: {exc}"))
            return None

    def _find_superadmin_id(self) -> str:
        from accounts.models import ROLE_SUPERADMIN
        from accounts.repository import UserRepository

        try:
            admins = UserRepository.list_by_role(ROLE_SUPERADMIN)
            if admins:
                return admins[0].get("id", "system")
        except Exception:
            pass
        return "system"

    # ---- collections ---------------------------------------------------

    def _seed_schools(self) -> list[dict]:
        from core.repository import SchoolRepository

        existing = {s.get("code"): s for s in self._list_all("schools")}
        result: list[dict] = []
        for spec in SCHOOLS:
            if spec["code"] in existing:
                result.append(existing[spec["code"]])
                continue
            doc = self._safe_create(
                "schools",
                SchoolRepository.create,
                {
                    **spec,
                    "is_active": True,
                    "is_deleted": False,
                    "created_at": _now(),
                    "updated_at": _now(),
                },
            )
            if doc:
                result.append(doc)
        self.stdout.write(f"  schools ready: {len(result)}")
        return result

    def _seed_levels(self) -> list[dict]:
        from config.appwrite_client import databases

        response = databases.list_documents(self.db_id, "levels")
        existing = {d.get("code"): _with_id(d) for d in documents_of(response)}
        result: list[dict] = []
        for spec in LEVELS:
            if spec["code"] in existing:
                result.append(existing[spec["code"]])
                continue
            doc = self._safe_create(
                "levels",
                lambda data: databases.create_document(self.db_id, "levels", "unique()", data),
                {
                    **spec,
                    "is_active": True,
                    "created_at": _now(),
                    "updated_at": _now(),
                },
            )
            if doc:
                result.append(_with_id(doc))
        self.stdout.write(f"  levels ready: {len(result)}")
        return result

    def _seed_academic_years(self, school: dict) -> list[dict]:
        from core.repository import AcademicYearRepository

        existing = {y.get("name"): y for y in self._list_all("academic_years")}
        specs = [
            ("2023-2024", datetime(2023, 9, 1), datetime(2024, 6, 30), False),
            ("2024-2025", datetime(2024, 9, 1), datetime(2025, 6, 30), False),
            ("2025-2026", datetime(2025, 9, 1), datetime(2026, 6, 30), True),
        ]
        result: list[dict] = []
        for name, start, end, is_active in specs:
            if name in existing:
                result.append(existing[name])
                continue
            doc = self._safe_create(
                "academic_years",
                AcademicYearRepository.create,
                {
                    "name": name,
                    "start_date": start.replace(tzinfo=timezone.utc).isoformat(),
                    "end_date": end.replace(tzinfo=timezone.utc).isoformat(),
                    "school_id": school.get("id", ""),
                    "is_active": is_active,
                    "is_deleted": False,
                    "created_at": _now(),
                    "updated_at": _now(),
                },
            )
            if doc:
                result.append(doc)
        self.stdout.write(f"  academic_years ready: {len(result)}")
        return result

    def _seed_classes(self, levels: list[dict], active_year: dict, school: dict) -> list[dict]:
        from classes.repository import ClassRepository

        existing = {c.get("name"): c for c in self._list_all("classes")}
        result: list[dict] = []
        for index, level in enumerate(levels):
            name = f"{level['code']}-A"
            if name in existing:
                result.append(existing[name])
                continue
            # Leave the last class deliberately unassigned for the Teachers view.
            teacher = "" if index == len(levels) - 1 else TEACHER_NAMES[index % len(TEACHER_NAMES)]
            doc = self._safe_create(
                "classes",
                ClassRepository.create,
                {
                    "name": name,
                    "level_id": level.get("id", ""),
                    "academic_year_id": active_year.get("id", ""),
                    "school_id": school.get("id", ""),
                    "capacity": 35,
                    "teacher_id": teacher,
                    "is_active": True,
                    "is_deleted": False,
                    "created_at": _now(),
                    "updated_at": _now(),
                },
            )
            if doc:
                result.append(doc)
        self.stdout.write(f"  classes ready: {len(result)}")
        return result

    def _seed_subjects(self, classes: list[dict]) -> dict[str, list[dict]]:
        from classes.repository import SubjectRepository

        all_subjects = self._list_all("subjects")
        existing_keys = {
            (s.get("class_id"), s.get("code")) for s in all_subjects
        }
        by_class: dict[str, list[dict]] = {}
        for klass in classes:
            class_id = klass.get("id", "")
            by_class.setdefault(class_id, [])
            for spec in CLASS_SUBJECTS:
                key = (class_id, spec["code"])
                if key in existing_keys:
                    match = next(
                        (s for s in all_subjects if s.get("class_id") == class_id and s.get("code") == spec["code"]),
                        None,
                    )
                    if match:
                        by_class[class_id].append(match)
                    continue
                doc = self._safe_create(
                    "subjects",
                    SubjectRepository.create,
                    {
                        "name": spec["name"],
                        "code": spec["code"],
                        "coefficient": spec["coefficient"],
                        "level_id": klass.get("level_id", ""),
                        "class_id": class_id,
                        "defined_by_admin": True,
                        "is_active": True,
                        "is_deleted": False,
                        "created_at": _now(),
                        "updated_at": _now(),
                    },
                )
                if doc:
                    by_class[class_id].append(doc)
        self.stdout.write(f"  subjects ready: {sum(len(v) for v in by_class.values())}")
        return by_class

    def _seed_students(self, classes: list[dict], active_year: dict, school: dict) -> list[dict]:
        from students.repository import StudentRepository

        result: list[dict] = []
        assignable = [c for c in classes]
        for index in range(self.num_students):
            matricule = f"SGEP-2025-{index + 1:04d}"
            existing = StudentRepository.find_by_matricule(matricule)
            if existing:
                result.append(existing)
                continue

            first_name = CAMEROON_FIRST_NAMES[index % len(CAMEROON_FIRST_NAMES)]
            last_name = CAMEROON_LAST_NAMES[(index * 7) % len(CAMEROON_LAST_NAMES)]
            gender = "M" if index % 2 == 0 else "F"

            # Vary class/status: ~10% unassigned (pending), ~12% inactive (suspended).
            if index % 10 == 4:
                klass = None
            else:
                klass = assignable[index % len(assignable)]
            is_active = not (index % 8 == 3)

            birth_year = 2014 + (index % 6)
            birth = datetime(birth_year, (index % 12) + 1, (index % 27) + 1, tzinfo=timezone.utc)

            payload = {
                "first_name": first_name,
                "last_name": last_name,
                "matricule": matricule,
                "birth_date": birth.isoformat(),
                "birth_place": BIRTH_PLACES[index % len(BIRTH_PLACES)],
                "gender": gender,
                # Mirror the service's history/search helpers; filtered out if the
                # live collection does not declare these attributes.
                "history": json.dumps([{"event": "create", "at": _now()}], ensure_ascii=True),
                "search_index": " ".join(
                    p.strip().lower() for p in [first_name, last_name, matricule] if p
                ),
                "school_id": school.get("id", ""),
                "class_id": klass.get("id", "") if klass else "",
                "current_level_id": klass.get("level_id", "") if klass else "",
                "academic_year_id": active_year.get("id", ""),
                "is_active": is_active,
                "is_deleted": False,
                "created_at": _now(),
                "updated_at": _now(),
            }
            doc = self._safe_create("students", StudentRepository.create, payload)
            if doc:
                result.append(doc)
        self.stdout.write(f"  students ready: {len(result)}")
        return result

    def _seed_parents(self, primary: dict, secondary: dict, students: list[dict]) -> list[dict]:
        from accounts.models import ROLE_PARENT
        from accounts.repository import UserRepository

        password_hash = make_password("ParentDemo123!")
        result: list[dict] = []
        for index in range(self.num_parents):
            email = f"parent{index + 1:02d}@demo.sgep.cm"
            if UserRepository.get_by_email(email):
                continue
            first_name = CAMEROON_FIRST_NAMES[(index * 3) % len(CAMEROON_FIRST_NAMES)]
            last_name = CAMEROON_LAST_NAMES[(index * 5) % len(CAMEROON_LAST_NAMES)]
            # Vary status so the dashboard shows suspended accounts too.
            account_status = "suspended" if index % 6 == 5 else "active"
            school = primary if index % 2 == 0 else secondary
            linked_student = students[index] if index < len(students) else None
            doc = self._safe_create(
                "users",
                UserRepository.create,
                {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": ROLE_PARENT,
                    "school_id": school.get("id", ""),
                    "phone": f"+23767{index:07d}",
                    "password": password_hash,
                    "account_status": account_status,
                    "student_id": (linked_student or {}).get("id", ""),
                    "is_deleted": False,
                    "created_at": _now(),
                    "updated_at": _now(),
                },
            )
            if doc:
                result.append(doc)
        self.stdout.write(f"  parent users created this run: {len(result)}")
        return result

    def _seed_fee_types(self, school: dict) -> list[dict]:
        existing = {f.get("code"): f for f in self._list_all("fee_types")}
        from config.appwrite_client import databases

        result: list[dict] = []
        for spec in FEE_TYPES:
            if spec["code"] in existing:
                result.append(existing[spec["code"]])
                continue
            doc = self._safe_create(
                "fee_types",
                lambda data: databases.create_document(self.db_id, "fee_types", "unique()", data),
                {
                    "name": spec["name"],
                    "code": spec["code"],
                    "amount": spec["amount"],
                    "school_id": school.get("id", ""),
                    "is_active": True,
                    "is_deleted": False,
                    "created_at": _now(),
                    "updated_at": _now(),
                },
            )
            if doc:
                result.append(_with_id(doc))
        self.stdout.write(f"  fee_types ready: {len(result)}")
        return result

    def _seed_invoices(self, students: list[dict], active_year: dict, fee_types: list[dict]) -> list[dict]:
        from finance.repository import InvoiceRepository

        existing = {i.get("number"): i for i in self._list_all("invoices")}
        scolarite = next((f for f in fee_types if f.get("code") == "SCOL"), fee_types[0])
        inscription = next((f for f in fee_types if f.get("code") == "INSC"), fee_types[0])

        result: list[dict] = []
        counter = 0
        active_students = [s for s in students if s.get("is_active") is not False and s.get("class_id")]
        for student in active_students:
            for fee in (inscription, scolarite):
                counter += 1
                number = f"INV-2025-{counter:04d}"
                if number in existing:
                    result.append(existing[number])
                    continue
                # ~65% paid so recovery rate is a meaningful partial figure.
                status = "paid" if RNG.random() < 0.65 else "pending"
                doc = self._safe_create(
                    "invoices",
                    InvoiceRepository.create,
                    {
                        "number": number,
                        "student_id": student.get("id", ""),
                        "academic_year_id": active_year.get("id", ""),
                        "fee_type_id": fee.get("id", ""),
                        "amount": float(fee.get("amount", 0)),
                        "status": status,
                        "due_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                        "is_deleted": False,
                        "created_at": _now(),
                        "updated_at": _now(),
                    },
                )
                if doc:
                    enriched = _with_id(doc)
                    enriched["status"] = status
                    enriched["amount"] = float(fee.get("amount", 0))
                    result.append(enriched)
        self.stdout.write(f"  invoices ready: {len(result)}")
        return result

    def _seed_payments(self, invoices: list[dict]) -> list[dict]:
        from finance.repository import PaymentRepository

        existing = {p.get("reference") for p in self._list_all("payments")}
        methods = ["CASH", "MOBILE_MONEY", "BANK_TRANSFER"]
        result: list[dict] = []
        counter = 0
        for invoice in invoices:
            counter += 1
            status = invoice.get("status")
            amount = float(invoice.get("amount", 0))
            if status == "paid":
                pay_amount = amount
            elif counter % 4 == 0:
                # A few partial payments on pending invoices.
                pay_amount = round(amount * 0.5, 2)
            else:
                continue
            reference = f"PAY-2025-{counter:04d}"
            if reference in existing:
                continue
            doc = self._safe_create(
                "payments",
                PaymentRepository.create,
                {
                    "invoice_id": invoice.get("id", ""),
                    "amount": pay_amount,
                    "method": methods[counter % len(methods)],
                    "reference": reference,
                    "receipt_path": "",
                    "status": "completed",
                    "recorded_by": self.recorded_by,
                    "is_deleted": False,
                    "created_at": _now(),
                    "updated_at": _now(),
                },
            )
            if doc:
                result.append(_with_id(doc))
        self.stdout.write(f"  payments created this run: {len(result)}")
        return result

    def _seed_grades(self, students: list[dict], subjects_by_class: dict[str, list[dict]], active_year: dict) -> None:
        from grades.repository import GradeRepository

        existing_response = self._list_all("grades")
        existing_keys = {
            (g.get("student_id"), g.get("subject_id"), g.get("sequence")) for g in existing_response
        }
        graded_students = [s for s in students if s.get("class_id")][:12]
        for student in graded_students:
            subjects = subjects_by_class.get(student.get("class_id", ""), [])
            for subject in subjects[:3]:
                key = (student.get("id"), subject.get("id"), SEQUENCE_LABEL)
                if key in existing_keys:
                    continue
                value = round(RNG.uniform(8.0, 18.0), 1)
                self._safe_create(
                    "grades",
                    GradeRepository.create,
                    {
                        "student_id": student.get("id", ""),
                        "subject_id": subject.get("id", ""),
                        "sequence": SEQUENCE_LABEL,
                        "value": value,
                        "coefficient": float(subject.get("coefficient", 1)),
                        "academic_year_id": active_year.get("id", ""),
                        "recorded_by": self.recorded_by,
                        "comments": "",
                        "is_deleted": False,
                        "created_at": _now(),
                        "updated_at": _now(),
                    },
                )
        self.stdout.write(f"  grades created this run: {self.counts.get('grades', 0)}")

    def _seed_attendance(self, students: list[dict], active_year: dict) -> None:
        from attendance.repository import AttendanceRepository

        existing = self._list_all("attendance")
        existing_keys = {(a.get("student_id"), a.get("date")) for a in existing}
        attended_students = [s for s in students if s.get("class_id")][:15]
        base_date = datetime(2025, 10, 6, 8, 0, tzinfo=timezone.utc)
        for offset, student in enumerate(attended_students):
            for day in range(2):
                date_iso = (base_date + timedelta(days=day)).isoformat()
                key = (student.get("id"), date_iso)
                if key in existing_keys:
                    continue
                status = ATTENDANCE_STATUSES[(offset + day) % len(ATTENDANCE_STATUSES)]
                self._safe_create(
                    "attendance",
                    AttendanceRepository.create,
                    {
                        "student_id": student.get("id", ""),
                        "class_id": student.get("class_id", ""),
                        "date": date_iso,
                        "status": status,
                        "reason": "Justifié par le tuteur" if status == "ABSENT_JUSTIFIE" else "",
                        "academic_year_id": active_year.get("id", ""),
                        "recorded_by": self.recorded_by,
                        "is_deleted": False,
                        "created_at": _now(),
                        "updated_at": _now(),
                    },
                )
        self.stdout.write(f"  attendance created this run: {self.counts.get('attendance', 0)}")


def _with_id(document: dict) -> dict:
    document = to_dict(document)
    result = dict(document)
    result["id"] = document.get("$id", document.get("id"))
    return result
