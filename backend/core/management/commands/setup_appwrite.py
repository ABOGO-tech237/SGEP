"""
Django management command to initialize Appwrite collections and schemas.
Idempotent: safely handles existing collections, attributes, and indexes.
Configured to run against Appwrite Cloud through the server API key stored
in environment variables.
"""

from django.core.management.base import BaseCommand
from django.conf import settings

from core.services.appwrite_service import AppwriteService
from config.cameroon_config import (
    CAMEROON_PRIMARY_LEVELS,
    CAMEROON_FEE_TYPES,
    CAMEROON_SUBJECTS,
    CAMEROON_ROLES,
)


# Fallback exception class for type checking
class AppwriteException(Exception):
    """Generic Appwrite exception."""
    pass


class Command(BaseCommand):
    """Initialize Appwrite collections with schemas and indexes."""

    help = "Initialize Appwrite collections with schemas and indexes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = AppwriteService()
        self.db_id = settings.APPWRITE_DB_ID

    def handle(self, *args, **options):
        """Execute the setup command."""
        self.stdout.write(self.style.SUCCESS("🚀 Initializing Appwrite collections for Cameroon SGEP..."))
        
        # Define all collections
        collections_config = {
            # Infrastructure collections
            "schools": self._get_schools_schema(),
            "academic_years": self._get_academic_years_schema(),
            
            # Cameroon-specific: Levels/Classes
            "levels": self._get_levels_schema(),
            "classes": self._get_classes_schema(),
            
            # Personnel
            "students": self._get_students_schema(),
            "parents": self._get_parents_schema(),
            "users": self._get_users_schema(),
            
            # Pedagogy
            # Subjects are defined by the administrator per class/level.
            "subjects": self._get_subjects_schema(),
            "sequences": self._get_sequences_schema(),
            "grades": self._get_grades_schema(),
            "attendance": self._get_attendance_schema(),
            
            # Finance
            "fee_types": self._get_fee_types_schema(),
            "invoices": self._get_invoices_schema(),
            "payments": self._get_payments_schema(),
            
            # Communication & Reports
            "report_cards": self._get_report_cards_schema(),
            "messages": self._get_messages_schema(),
            "notifications": self._get_notifications_schema(),
            "report_jobs": self._get_report_jobs_schema(),
            "audit_logs": self._get_audit_logs_schema(),
        }

        # Create collections
        for collection_id, config in collections_config.items():
            self._create_collection(collection_id, config)

        self.stdout.write(self.style.SUCCESS("✅ Appwrite initialization completed!"))

    def _create_collection(self, collection_id: str, config: dict):
        """Create a collection with attributes and indexes."""
        try:
            # Try to create the collection
            self.service.create_collection(
                db_id=self.db_id,
                collection_id=collection_id,
                name=config["name"],
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Collection '{collection_id}' created"))
        except Exception as e:
            if "already exists" in str(e):
                self.stdout.write(self.style.WARNING(f"⏭️  Collection '{collection_id}' already exists"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Error creating collection '{collection_id}': {e}"))
                return

        # Create attributes
        self.stdout.write(f"  📝 Creating {len(config['attributes'])} attributes...")
        for attr in config["attributes"]:
            self._create_attribute(collection_id, attr)

        # Create indexes
        if config.get("indexes"):
            self.stdout.write(f"  🔍 Creating {len(config['indexes'])} indexes...")
            for index in config["indexes"]:
                self._create_index(collection_id, index)

    def _create_attribute(self, collection_id: str, attr: dict):
        """Create an attribute in a collection."""
        try:
            attr_type = attr.pop("type")
            self.service.create_attribute(
                db_id=self.db_id,
                collection_id=collection_id,
                key=attr["key"],
                type=attr_type,
                **attr,
            )
        except Exception as e:
            if "already exists" in str(e):
                pass  # Silently skip
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Could not create attribute {attr.get('key')}: {e}"))

    def _create_index(self, collection_id: str, index: dict):
        """Create an index on a collection."""
        try:
            self.service.create_index(
                db_id=self.db_id,
                collection_id=collection_id,
                **index,
            )
        except Exception as e:
            if "already exists" in str(e):
                pass  # Silently skip
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Could not create index {index.get('key')}: {e}"))

    # Collection Schema Definitions
    
    def _get_levels_schema(self) -> dict:
        """School levels/grades for Cameroon (SIL, CP, CE1, CM2, Class 1-6)."""
        return {
            "name": "Levels",
            "attributes": [
                {"key": "code", "type": "string", "size": 20, "required": True},
                {"key": "name", "type": "string", "size": 100, "required": True},
                {"key": "cycle", "type": "string", "size": 50, "required": True},  # maternelle/primaire
                {"key": "age", "type": "integer", "required": True},
                {"key": "language", "type": "string", "size": 10, "required": False},  # fr/en
                {"key": "is_active", "type": "boolean", "required": True, "default": True},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_code", "type": "key", "attributes": ["code"]},
                {"key": "idx_cycle", "type": "key", "attributes": ["cycle"]},
            ],
        }
    
    def _get_schools_schema(self) -> dict:
        """Schools collection schema."""
        return {
            "name": "Schools",
            "attributes": [
                {"key": "name", "type": "string", "size": 255, "required": True},
                {"key": "code", "type": "string", "size": 50, "required": True},
                {"key": "address", "type": "string", "size": 500, "required": False},
                {"key": "phone", "type": "string", "size": 20, "required": False},
                {"key": "email", "type": "email", "required": False},
                {"key": "is_active", "type": "boolean", "required": True, "default": True},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "deleted_at", "type": "datetime", "required": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_is_active", "type": "key", "attributes": ["is_active"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_academic_years_schema(self) -> dict:
        """Academic years collection schema."""
        return {
            "name": "Academic Years",
            "attributes": [
                {"key": "name", "type": "string", "size": 100, "required": True},
                {"key": "start_date", "type": "datetime", "required": True},
                {"key": "end_date", "type": "datetime", "required": True},
                {"key": "school_id", "type": "string", "size": 36, "required": False},
                {"key": "is_active", "type": "boolean", "required": True, "default": False},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_school_id", "type": "key", "attributes": ["school_id"]},
                {"key": "idx_is_active", "type": "key", "attributes": ["is_active"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_classes_schema(self) -> dict:
        """Classes collection schema (Cameroon system with levels)."""
        return {
            "name": "Classes",
            "attributes": [
                {"key": "name", "type": "string", "size": 100, "required": True},  # e.g., "SIL-A", "CP-B"
                {"key": "level_id", "type": "string", "size": 36, "required": True},  # Reference to levels
                {"key": "academic_year_id", "type": "string", "size": 36, "required": True},
                {"key": "school_id", "type": "string", "size": 36, "required": False},
                {"key": "capacity", "type": "integer", "required": False},
                {"key": "teacher_id", "type": "string", "size": 36, "required": False},  # Main teacher
                {"key": "is_active", "type": "boolean", "required": True, "default": True},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_level_id", "type": "key", "attributes": ["level_id"]},
                {"key": "idx_academic_year_id", "type": "key", "attributes": ["academic_year_id"]},
                {"key": "idx_school_id", "type": "key", "attributes": ["school_id"]},
                {"key": "idx_is_active", "type": "key", "attributes": ["is_active"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_students_schema(self) -> dict:
        """Students collection schema (Cameroon specific)."""
        return {
            "name": "Students",
            "attributes": [
                {"key": "first_name", "type": "string", "size": 100, "required": True},
                {"key": "last_name", "type": "string", "size": 100, "required": True},
                {"key": "matricule", "type": "string", "size": 50, "required": True},  # School registration number
                {"key": "birth_date", "type": "datetime", "required": True},
                {"key": "birth_place", "type": "string", "size": 100, "required": True},
                {"key": "gender", "type": "string", "size": 10, "required": True},  # M/F
                {"key": "id_number", "type": "string", "size": 50, "required": False},  # National ID or passport (children age 6 typically don't have one)
                {"key": "medical", "type": "string", "size": 4000, "required": False, "encrypt": True},  # Encrypted JSON payload
                {"key": "history", "type": "text", "required": False},  # Enrollment and promotion audit trail
                {"key": "search_index", "type": "text", "required": False},  # Denormalized search helper
                {"key": "school_id", "type": "string", "size": 36, "required": False},
                {"key": "class_id", "type": "string", "size": 36, "required": False},
                {"key": "academic_year_id", "type": "string", "size": 36, "required": False},
                {"key": "is_active", "type": "boolean", "required": True, "default": True},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "deleted_at", "type": "datetime", "required": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_school_id", "type": "key", "attributes": ["school_id"]},
                {"key": "idx_matricule", "type": "key", "attributes": ["matricule"]},
                {"key": "idx_class_id", "type": "key", "attributes": ["class_id"]},
                {"key": "idx_academic_year_id", "type": "key", "attributes": ["academic_year_id"]},
                {"key": "idx_is_active", "type": "key", "attributes": ["is_active"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
                {"key": "idx_search_index", "type": "fulltext", "attributes": ["search_index"]},
            ],
        }

    def _get_parents_schema(self) -> dict:
        """Parents collection schema (Cameroon: Tuteurs/Tutrices)."""
        return {
            "name": "Parents",
            "attributes": [
                {"key": "first_name", "type": "string", "size": 100, "required": True},
                {"key": "last_name", "type": "string", "size": 100, "required": True},
                {"key": "relationship", "type": "string", "size": 50, "required": True},  # Père/Mère/Tuteur/Tante/Oncle...
                {"key": "phone", "type": "string", "size": 20, "required": True},
                {"key": "phone2", "type": "string", "size": 20, "required": False},  # Second phone number
                {"key": "email", "type": "email", "required": True},
                {"key": "user_id", "type": "string", "size": 36, "required": False},  # Link to user account
                {"key": "account_status", "type": "string", "size": 20, "required": True, "default": "ACTIVE"},
                {"key": "last_renewal_date", "type": "datetime", "required": False},
                {"key": "school_id", "type": "string", "size": 36, "required": False},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_email", "type": "key", "attributes": ["email"]},
                {"key": "idx_phone", "type": "key", "attributes": ["phone"]},
                {"key": "idx_account_status", "type": "key", "attributes": ["account_status"]},
                {"key": "idx_school_id", "type": "key", "attributes": ["school_id"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_users_schema(self) -> dict:
        """Users collection schema (Cameroon roles: SuperAdmin, Comptable, Directeur, Parent)."""
        return {
            "name": "Users",
            "attributes": [
                {"key": "email", "type": "email", "required": True},
                {"key": "first_name", "type": "string", "size": 100, "required": True},
                {"key": "last_name", "type": "string", "size": 100, "required": True},
                {"key": "role", "type": "string", "size": 30, "required": True},  # SUPER_ADMIN/COMPTABLE/DIRECTEUR/PARENT
                {"key": "school_id", "type": "string", "size": 36, "required": False},
                {"key": "phone", "type": "string", "size": 20, "required": False},
                {"key": "account_status", "type": "string", "size": 20, "required": True, "default": "ACTIVE"},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_email", "type": "key", "attributes": ["email"]},
                {"key": "idx_role", "type": "key", "attributes": ["role"]},
                {"key": "idx_school_id", "type": "key", "attributes": ["school_id"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_subjects_schema(self) -> dict:
        """Subjects collection schema."""
        return {
            "name": "Subjects",
            "attributes": [
                {"key": "name", "type": "string", "size": 100, "required": True},
                {"key": "code", "type": "string", "size": 50, "required": True},
                {"key": "coefficient", "type": "integer", "required": True},
                # Subjects may be defined per level/class by the administrator.
                {"key": "level_id", "type": "string", "size": 36, "required": False},
                {"key": "class_id", "type": "string", "size": 36, "required": False},
                {"key": "defined_by_admin", "type": "boolean", "required": True, "default": True},
                {"key": "is_active", "type": "boolean", "required": True, "default": True},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_school_id", "type": "key", "attributes": ["school_id"]},
                {"key": "idx_is_active", "type": "key", "attributes": ["is_active"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_grades_schema(self) -> dict:
        """Grades collection schema (Cameroon system: 0-20, Séquences)."""
        return {
            "name": "Grades",
            "attributes": [
                {"key": "student_id", "type": "string", "size": 36, "required": True},
                {"key": "subject_id", "type": "string", "size": 36, "required": True},
                {"key": "sequence", "type": "string", "size": 50, "required": True},  # Séquence 1-4
                {"key": "value", "type": "double", "required": True},  # 0-20
                {"key": "coefficient", "type": "double", "required": True},
                {"key": "academic_year_id", "type": "string", "size": 36, "required": True},
                {"key": "recorded_by", "type": "string", "size": 36, "required": True},
                {"key": "comments", "type": "string", "size": 500, "required": False},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_student_id", "type": "key", "attributes": ["student_id"]},
                {"key": "idx_academic_year_id", "type": "key", "attributes": ["academic_year_id"]},
                {"key": "idx_sequence", "type": "key", "attributes": ["sequence"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_attendance_schema(self) -> dict:
        """Attendance collection schema (Cameroon: PRESENT, ABSENT, RETARD, ABSENT_JUSTIFIE)."""
        return {
            "name": "Attendance",
            "attributes": [
                {"key": "student_id", "type": "string", "size": 36, "required": True},
                {"key": "class_id", "type": "string", "size": 36, "required": True},
                {"key": "date", "type": "datetime", "required": True},
                {"key": "status", "type": "string", "size": 30, "required": True},  # PRESENT/ABSENT/RETARD/ABSENT_JUSTIFIE
                {"key": "reason", "type": "string", "size": 500, "required": False},
                {"key": "academic_year_id", "type": "string", "size": 36, "required": True},
                {"key": "recorded_by", "type": "string", "size": 36, "required": True},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_student_id", "type": "key", "attributes": ["student_id"]},
                {"key": "idx_class_id", "type": "key", "attributes": ["class_id"]},
                {"key": "idx_academic_year_id", "type": "key", "attributes": ["academic_year_id"]},
                {"key": "idx_date", "type": "key", "attributes": ["date"]},
                {"key": "idx_status", "type": "key", "attributes": ["status"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_fee_types_schema(self) -> dict:
        """Fee types collection schema."""
        return {
            "name": "Fee Types",
            "attributes": [
                {"key": "name", "type": "string", "size": 100, "required": True},
                {"key": "code", "type": "string", "size": 50, "required": True},
                {"key": "amount", "type": "double", "required": True},
                {"key": "school_id", "type": "string", "size": 36, "required": True},
                {"key": "is_active", "type": "boolean", "required": True, "default": True},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_school_id", "type": "key", "attributes": ["school_id"]},
                {"key": "idx_is_active", "type": "key", "attributes": ["is_active"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_invoices_schema(self) -> dict:
        """Invoices collection schema."""
        return {
            "name": "Invoices",
            "attributes": [
                {"key": "number", "type": "string", "size": 50, "required": True},
                {"key": "student_id", "type": "string", "size": 36, "required": True},
                {"key": "academic_year_id", "type": "string", "size": 36, "required": True},
                {"key": "fee_type_id", "type": "string", "size": 36, "required": False},
                {"key": "amount", "type": "double", "required": True},
                {"key": "status", "type": "string", "size": 20, "required": True},
                {"key": "due_date", "type": "datetime", "required": True},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_student_id", "type": "key", "attributes": ["student_id"]},
                {"key": "idx_academic_year_id", "type": "key", "attributes": ["academic_year_id"]},
                {"key": "idx_status", "type": "key", "attributes": ["status"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_payments_schema(self) -> dict:
        """Payments collection schema."""
        return {
            "name": "Payments",
            "attributes": [
                {"key": "invoice_id", "type": "string", "size": 36, "required": True},
                {"key": "amount", "type": "double", "required": True},
                {"key": "method", "type": "string", "size": 50, "required": True},
                {"key": "reference", "type": "string", "size": 100, "required": False},
                {"key": "receipt_path", "type": "string", "size": 500, "required": False},
                {"key": "status", "type": "string", "size": 20, "required": True},
                {"key": "recorded_by", "type": "string", "size": 36, "required": True},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_invoice_id", "type": "key", "attributes": ["invoice_id"]},
                {"key": "idx_status", "type": "key", "attributes": ["status"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_report_cards_schema(self) -> dict:
        """Report cards collection schema (Cameroon Séquences)."""
        return {
            "name": "Report Cards",
            "attributes": [
                {"key": "student_id", "type": "string", "size": 36, "required": True},
                {"key": "academic_year_id", "type": "string", "size": 36, "required": True},
                {"key": "sequence", "type": "string", "size": 50, "required": True},  # Séquence 1-4
                {"key": "file_path", "type": "string", "size": 500, "required": False},
                {"key": "status", "type": "string", "size": 20, "required": True},  # draft/published
                {"key": "generated_at", "type": "datetime", "required": False},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_student_id", "type": "key", "attributes": ["student_id"]},
                {"key": "idx_academic_year_id", "type": "key", "attributes": ["academic_year_id"]},
                {"key": "idx_sequence", "type": "key", "attributes": ["sequence"]},
                {"key": "idx_status", "type": "key", "attributes": ["status"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_messages_schema(self) -> dict:
        """Messages collection schema."""
        return {
            "name": "Messages",
            "attributes": [
                {"key": "sender_id", "type": "string", "size": 36, "required": True},
                {"key": "recipient_id", "type": "string", "size": 36, "required": True},
                {"key": "subject", "type": "string", "size": 255, "required": True},
                {"key": "body", "type": "string", "size": 5000, "required": True},
                {"key": "is_read", "type": "boolean", "required": True, "default": False},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_recipient_id", "type": "key", "attributes": ["recipient_id"]},
                {"key": "idx_sender_id", "type": "key", "attributes": ["sender_id"]},
                {"key": "idx_is_read", "type": "key", "attributes": ["is_read"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_notifications_schema(self) -> dict:
        """Notifications collection schema."""
        return {
            "name": "Notifications",
            "attributes": [
                {"key": "user_id", "type": "string", "size": 36, "required": True},
                {"key": "title", "type": "string", "size": 255, "required": True},
                {"key": "message", "type": "string", "size": 1000, "required": True},
                {"key": "type", "type": "string", "size": 20, "required": True},
                {"key": "status", "type": "string", "size": 20, "required": False, "default": "pending"},
                {"key": "sent_at", "type": "datetime", "required": False},
                {"key": "error", "type": "string", "size": 1000, "required": False},
                {"key": "is_read", "type": "boolean", "required": True, "default": False},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_user_id", "type": "key", "attributes": ["user_id"]},
                {"key": "idx_is_read", "type": "key", "attributes": ["is_read"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_report_jobs_schema(self) -> dict:
        """Report jobs collection schema."""
        return {
            "name": "Report Jobs",
            "attributes": [
                {"key": "type", "type": "string", "size": 20, "required": True},
                {"key": "status", "type": "string", "size": 20, "required": True},
                {"key": "requested_by", "type": "string", "size": 36, "required": True},
                {"key": "file_path", "type": "string", "size": 500, "required": False},
                {"key": "error", "type": "string", "size": 1000, "required": False},
                {"key": "params", "type": "string", "size": 2000, "required": False},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_status", "type": "key", "attributes": ["status"]},
                {"key": "idx_requested_by", "type": "key", "attributes": ["requested_by"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_audit_logs_schema(self) -> dict:
        """Audit logs collection schema."""
        return {
            "name": "Audit Logs",
            "attributes": [
                {"key": "user_id", "type": "string", "size": 36, "required": True},
                {"key": "action", "type": "string", "size": 100, "required": True},
                {"key": "resource_type", "type": "string", "size": 100, "required": True},
                {"key": "resource_id", "type": "string", "size": 36, "required": False},
                {"key": "details", "type": "string", "size": 2000, "required": False},
                {"key": "ip_address", "type": "string", "size": 45, "required": False},
                {"key": "is_deleted", "type": "boolean", "required": True, "default": False},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_user_id", "type": "key", "attributes": ["user_id"]},
                {"key": "idx_action", "type": "key", "attributes": ["action"]},
                {"key": "idx_resource_type", "type": "key", "attributes": ["resource_type"]},
                {"key": "idx_is_deleted", "type": "key", "attributes": ["is_deleted"]},
            ],
        }

    def _get_sequences_schema(self) -> dict:
        """Sequences collection schema: 6 sequences across 3 trimesters, dates set by admin per academic year."""
        return {
            "name": "Sequences",
            "attributes": [
                {"key": "number", "type": "integer", "required": True},
                {"key": "name", "type": "string", "size": 50, "required": True},
                {"key": "trimester", "type": "integer", "required": True},
                {"key": "start_date", "type": "datetime", "required": False},
                {"key": "end_date", "type": "datetime", "required": False},
                {"key": "academic_year_id", "type": "string", "size": 36, "required": True},
                {"key": "is_active", "type": "boolean", "required": True, "default": True},
                {"key": "created_at", "type": "datetime", "required": True},
                {"key": "updated_at", "type": "datetime", "required": True},
            ],
            "indexes": [
                {"key": "idx_academic_year_id", "type": "key", "attributes": ["academic_year_id"]},
                {"key": "idx_number", "type": "key", "attributes": ["number"]},
            ],
        }
