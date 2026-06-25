from __future__ import annotations

from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ROLE_SUPERADMIN, User
from classes.services import ClassService, SubjectService
from core.exceptions import NotFoundError


class ClassServiceTests(SimpleTestCase):
	def test_list_returns_classes(self):
		with patch("classes.services.ClassRepository.list", return_value=[{"id": "cls-1", "name": "CM2 A"}]):
			result = ClassService.list(academic_year_id="year-1")

		self.assertEqual(len(result), 1)
		self.assertEqual(result[0]["name"], "CM2 A")

	def test_get_raises_when_missing(self):
		with patch("classes.services.ClassRepository.get", return_value=None):
			with self.assertRaises(NotFoundError):
				ClassService.get("missing")


class SubjectServiceTests(SimpleTestCase):
	def test_create_sets_defaults(self):
		with patch("classes.services.SubjectRepository.create", return_value={"id": "sub-1", "name": "Maths"}) as create_mock:
			SubjectService.create({"name": "Maths", "code": "MAT", "coefficient": 2})

		payload = create_mock.call_args[0][0]
		self.assertTrue(payload["defined_by_admin"])
		self.assertTrue(payload["is_active"])


class ClassApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User(id="admin-1", email="admin@example.com", role=ROLE_SUPERADMIN, account_status="active")
		self.client.force_authenticate(user=self.user)

	def test_list_classes(self):
		with patch("classes.views.ClassService.list", return_value=[{"id": "cls-1", "name": "CM2 A", "level_id": "l1", "academic_year_id": "y1"}]):
			response = self.client.get("/api/v1/classes/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)

	def test_create_class(self):
		payload = {"name": "CM2 B", "level_id": "l1", "academic_year_id": "y1"}
		with patch("classes.views.ClassService.create", return_value={"id": "cls-2", **payload}):
			response = self.client.post("/api/v1/classes/", payload, format="json")

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["name"], "CM2 B")

	def test_get_class_detail(self):
		with patch(
			"classes.views.ClassService.get",
			return_value={"id": "cls-1", "name": "CM2 A", "level_id": "l1", "academic_year_id": "y1"},
		):
			response = self.client.get("/api/v1/classes/cls-1/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["id"], "cls-1")

	def test_patch_class(self):
		with patch(
			"classes.views.ClassService.update",
			return_value={"id": "cls-1", "name": "CM2 A+", "level_id": "l1", "academic_year_id": "y1"},
		) as update_mock:
			response = self.client.patch("/api/v1/classes/cls-1/", {"name": "CM2 A+"}, format="json")

		self.assertEqual(response.status_code, 200)
		update_mock.assert_called_once()

	def test_create_subject(self):
		payload = {"name": "Français", "code": "FR", "coefficient": 2, "class_id": "cls-1"}
		with patch("classes.views.SubjectService.create", return_value={"id": "sub-1", **payload}):
			response = self.client.post("/api/v1/subjects/", payload, format="json")

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["code"], "FR")
