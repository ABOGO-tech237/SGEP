from __future__ import annotations

from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ROLE_SUPERADMIN, User
from core.audit import log_action
from core.exceptions import NotFoundError
from core.school_services import AcademicYearService, SchoolService


class AuditTests(SimpleTestCase):
	def test_log_action_creates_document(self):
		with patch("core.audit.databases.create_document") as create_mock:
			log_action("user-1", "CREATE", "students", "stu-1", {"matricule": "MAT-001"}, "127.0.0.1")

		create_mock.assert_called_once()
		payload = create_mock.call_args[0][3]
		self.assertEqual(payload["user_id"], "user-1")
		self.assertEqual(payload["action"], "CREATE")
		self.assertEqual(payload["resource_type"], "students")


class SchoolServiceTests(SimpleTestCase):
	def test_get_raises_when_missing(self):
		with patch("core.school_services.SchoolRepository.get", return_value=None):
			with self.assertRaises(NotFoundError):
				SchoolService.get("missing")

	def test_create_sets_timestamps(self):
		with patch("core.school_services.SchoolRepository.create", return_value={"id": "sch-1", "name": "École A"}) as create_mock:
			SchoolService.create({"name": "École A", "code": "ECA"})

		payload = create_mock.call_args[0][0]
		self.assertIn("created_at", payload)
		self.assertFalse(payload["is_deleted"])


class AcademicYearServiceTests(SimpleTestCase):
	def test_list_filters_by_school(self):
		with patch("core.school_services.AcademicYearRepository.list", return_value=[]) as list_mock:
			AcademicYearService.list(school_id="sch-1")

		list_mock.assert_called_once_with(school_id="sch-1")


class SchoolApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User(id="admin-1", email="admin@example.com", role=ROLE_SUPERADMIN, account_status="active")
		self.client.force_authenticate(user=self.user)

	def test_list_schools(self):
		with patch("core.views.SchoolService.list", return_value=[{"id": "sch-1", "name": "École A", "code": "ECA"}]):
			response = self.client.get("/api/v1/schools/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data[0]["name"], "École A")
