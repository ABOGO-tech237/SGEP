from __future__ import annotations

import uuid
from datetime import datetime, timezone

from django.test import SimpleTestCase

from core.admin_dashboard_service import AdminDashboardService
from core.appwrite_test_utils import skip_unless_appwrite
from students.repository import StudentRepository


@skip_unless_appwrite()
class AppwriteIntegrationTests(SimpleTestCase):
	"""Tests live contre Appwrite Cloud. Ignorés si .env contient des placeholders."""

	def test_list_students_collection(self):
		response = StudentRepository.list(page=1, page_size=5)
		self.assertIn("documents", response)
		self.assertIn("total", response)

	def test_student_crud_cycle(self):
		matricule = f"TEST-{uuid.uuid4().hex[:8].upper()}"
		now = datetime.now(timezone.utc).isoformat()
		payload = {
			"matricule": matricule,
			"first_name": "Integration",
			"last_name": "Test",
			"birth_date": "2015-01-01",
			"birth_place": "Douala",
			"gender": "M",
			"class_id": "",
			"academic_year_id": "",
			"school_id": "",
			"id_number": "",
			"current_level_id": "",
			"parent_user_id": "",
			"medical_notes": "",
			"is_active": True,
			"is_deleted": False,
			"created_at": now,
			"updated_at": now,
		}

		created = StudentRepository.create(payload)
		self.assertEqual(created["matricule"], matricule)

		fetched = StudentRepository.get(created["id"])
		self.assertIsNotNone(fetched)
		self.assertEqual(fetched["first_name"], "Integration")

		updated = StudentRepository.update(
			created["id"],
			{"first_name": "Updated", "updated_at": datetime.now(timezone.utc).isoformat()},
		)
		self.assertEqual(updated["first_name"], "Updated")

		deleted = StudentRepository.soft_delete(created["id"])
		self.assertTrue(deleted.get("is_deleted"))

	def test_admin_dashboard_live(self):
		dashboard = AdminDashboardService.build()
		self.assertIn("stats", dashboard)
		self.assertGreaterEqual(len(dashboard["stats"]), 4)
		self.assertIn("finance", dashboard)
