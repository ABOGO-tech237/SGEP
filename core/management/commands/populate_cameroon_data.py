"""
Django management command to populate Appwrite with Cameroon-specific data.
Runs after setup_appwrite.py to initialize levels, subjects, and fee types.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import json

from core.services.appwrite_service import AppwriteService
from config.cameroon_config import (
    CAMEROON_PRIMARY_LEVELS,
    CAMEROON_FEE_TYPES,
    CAMEROON_SUBJECTS,
    SEQUENCES,
)


class Command(BaseCommand):
    """Populate Appwrite with Cameroon-specific configuration data."""

    help = "Populate Appwrite collections with Cameroon primary school data"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = AppwriteService()
        self.db_id = settings.APPWRITE_DB_ID

    def handle(self, *args, **options):
        """Execute the population command."""
        self.stdout.write(self.style.SUCCESS("🇨🇲 Populating Cameroon-specific data..."))
        
        # Populate levels (SIL, CP, CE1, etc.)
        self._populate_levels()
        
        # Populate subjects
        self._populate_subjects()
        
        # Populate fee types
        self._populate_fee_types()
        
        # Populate sequences
        self._populate_sequences()
        
        self.stdout.write(self.style.SUCCESS("✅ Data population completed!"))

    def _populate_levels(self):
        """Populate school levels (SIL, CP, CM2, Class 1-6)."""
        self.stdout.write("  📚 Populating school levels...")
        
        try:
            for level_code, level_data in CAMEROON_PRIMARY_LEVELS.items():
                try:
                    doc = self.service.databases.create_document(
                        database_id=self.db_id,
                        collection_id="levels",
                        document_id="unique()",
                        data={
                            "code": level_data["code"],
                            "name": level_data["name"],
                            "cycle": level_data["cycle"],
                            "age": level_data["age"],
                            "language": level_data.get("lang", ""),
                            "is_active": True,
                        },
                    )
                    self.stdout.write(self.style.SUCCESS(f"    ✅ {level_data['code']} - {level_data['name']}"))
                except Exception as e:
                    if "already exists" not in str(e):
                        self.stdout.write(self.style.WARNING(f"    ⚠️  {level_data['code']}: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error populating levels: {e}"))

    def _populate_subjects(self):
        """Populate school subjects (template subjects for classes)."""
        self.stdout.write("  📖 Populating subjects...")
        
        try:
            for subject_code, subject_data in CAMEROON_SUBJECTS.items():
                try:
                    doc = self.service.databases.create_document(
                        database_id=self.db_id,
                        collection_id="subjects",
                        document_id="unique()",
                        data={
                            "name": subject_data["name"],
                            "code": subject_data["code"],
                            "coefficient": subject_data["coefficient"],
                            "defined_by_admin": True,
                            "is_active": True,
                        },
                    )
                    self.stdout.write(self.style.SUCCESS(f"    ✅ {subject_data['code']} - {subject_data['name']}"))
                except Exception as e:
                    if "already exists" not in str(e):
                        self.stdout.write(self.style.WARNING(f"    ⚠️  {subject_data['code']}: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error populating subjects: {e}"))

    def _populate_fee_types(self):
        """Populate fee types."""
        self.stdout.write("  💰 Populating fee types...")
        
        try:
            for fee_code, fee_data in CAMEROON_FEE_TYPES.items():
                try:
                    doc = self.service.databases.create_document(
                        database_id=self.db_id,
                        collection_id="fee_types",
                        document_id="unique()",
                        data={
                            "name": fee_data["name"],
                            "code": fee_data["code"],
                            "amount": 0.0,  # Will be set by school
                            "is_active": True,
                        },
                    )
                    self.stdout.write(self.style.SUCCESS(f"    ✅ {fee_data['code']} - {fee_data['name']}"))
                except Exception as e:
                    if "already exists" not in str(e):
                        self.stdout.write(self.style.WARNING(f"    ⚠️  {fee_data['code']}: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error populating fee types: {e}"))

    def _populate_sequences(self):
        """Populate sequences (admin can set dates later per academic year)."""
        self.stdout.write("  🔄 Populating sequences...")
        
        try:
            for seq_key, seq_data in SEQUENCES.items():
                try:
                    doc = self.service.databases.create_document(
                        database_id=self.db_id,
                        collection_id="sequences",
                        document_id="unique()",
                        data={
                            "number": seq_data["number"],
                            "name": seq_data["name"],
                            "trimester": seq_data["trimester"],
                            "start_date": None,  # Admin sets per academic year
                            "end_date": None,    # Admin sets per academic year
                            "is_active": True,
                        },
                    )
                    self.stdout.write(self.style.SUCCESS(f"    ✅ {seq_data['name']} (Trimestre {seq_data['trimester']})"))
                except Exception as e:
                    if "already exists" not in str(e):
                        self.stdout.write(self.style.WARNING(f"    ⚠️  {seq_data['name']}: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error populating sequences: {e}"))
