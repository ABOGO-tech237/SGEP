from __future__ import annotations

import json
import uuid
from unittest.mock import patch

from cryptography.fernet import Fernet
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_SUPERADMIN, User
from core.exceptions import ConflictError
from students.serializers import StudentCreateSerializer, StudentSerializer
from students.services import StudentService


@override_settings(MEDICAL_ENCRYPTION_KEY=Fernet.generate_key().decode())
class StudentServiceTests(SimpleTestCase):
	def test_create_encrypts_medical_and_triggers_parent_creation(self):
		data = {
			"first_name": "Jean",
			"last_name": "Dupont",
			"matricule": "MAT-001",
			"birth_date": "2015-01-02T00:00:00+00:00",
			"birth_place": "Douala",
			"gender": "M",
			"class_id": "class-a",
			"academic_year_id": "ay-2026",
			"medical": {"allergies": ["arachide"]},
			"guardians": [{"email": "parent@example.com", "first_name": "Anne"}],
		}

		with patch("students.services.StudentRepository.find_by_matricule", return_value=None), patch(
			"students.services.StudentRepository.create",
			side_effect=lambda payload: {"id": "stu-1", **payload},
		) as create_mock, patch("students.services.ParentAccountService.create_from_student") as parent_mock:
			student = StudentService.create(data)

		created_payload = create_mock.call_args[0][0]
		self.assertNotEqual(created_payload["medical"], json.dumps(data["medical"]))
		decrypted_medical = json.loads(StudentService._fernet().decrypt(created_payload["medical"].encode()).decode())
		self.assertEqual(decrypted_medical, data["medical"])
		self.assertIn("create", created_payload["history"])
		self.assertIn("jean", created_payload["search_index"])
		self.assertEqual(student["id"], "stu-1")
		parent_mock.assert_called_once_with("stu-1", data["guardians"])

	def test_create_raises_conflict_on_duplicate_matricule(self):
		data = {
			"first_name": "Jean",
			"last_name": "Dupont",
			"matricule": "MAT-001",
			"birth_date": "2015-01-02T00:00:00+00:00",
			"birth_place": "Douala",
			"gender": "M",
			"class_id": "class-a",
			"academic_year_id": "ay-2026",
		}

		with patch("students.services.StudentRepository.find_by_matricule", return_value={"id": "exists"}):
			with self.assertRaises(ConflictError):
				StudentService.create(data)

	def test_list_wraps_items_and_pagination(self):
		with patch(
			"students.services.StudentRepository.list",
			return_value={"documents": [{"id": "stu-1"}], "total": 1},
		):
			response = StudentService.list(page=2, page_size=5)

		self.assertEqual(response["items"], [{"id": "stu-1"}])
		self.assertEqual(response["page"], 2)
		self.assertEqual(response["page_size"], 5)

	def test_enroll_creates_inscription_invoice(self):
		student = {
			"id": "stu-1",
			"history": "[]",
			"first_name": "Awa",
			"last_name": "Nana",
			"matricule": "MAT-1",
		}

		with patch("students.services.StudentRepository.get", return_value=student), patch(
			"students.services.StudentRepository.update",
			return_value={"id": "stu-1", "class_id": "class-a", "academic_year_id": "ay-1"},
		), patch("students.services.ParentAccountService.reactivate"), patch(
			"finance.services.InvoiceService.ensure_inscription_invoice"
		) as invoice_mock:
			StudentService.enroll("stu-1", "class-a", "ay-1")

		invoice_mock.assert_called_once_with("stu-1", "ay-1")


@override_settings(MEDICAL_ENCRYPTION_KEY=Fernet.generate_key().decode())
class StudentSerializerTests(SimpleTestCase):
	def test_student_serializer_decrypts_medical(self):
		fernet = StudentService._fernet()
		encrypted_medical = fernet.encrypt(json.dumps({"blood_group": "O+"}).encode()).decode()

		serializer = StudentSerializer(
			{
				"id": "stu-1",
				"first_name": "Awa",
				"last_name": "Nana",
				"matricule": "MAT-002",
				"birth_date": "2014-01-01T00:00:00+00:00",
				"birth_place": "Yaounde",
				"gender": "F",
				"medical": encrypted_medical,
				"history": json.dumps([{"event": "create"}]),
			}
		)

		self.assertEqual(serializer.data["medical"], {"blood_group": "O+"})
		self.assertEqual(serializer.data["history"], [{"event": "create"}])

	def test_student_create_serializer_rejects_duplicate_matricule(self):
		payload = {
			"first_name": "Awa",
			"last_name": "Nana",
			"matricule": "MAT-009",
			"birth_date": "2014-01-01T00:00:00+00:00",
			"birth_place": "Yaounde",
			"gender": "F",
			"class_id": "class-a",
			"academic_year_id": "ay-2026",
		}

		with patch("students.serializers.StudentRepository.find_by_matricule", return_value={"id": "other-id"}):
			serializer = StudentCreateSerializer(data=payload, context={"student_id": "stu-1"})
			self.assertFalse(serializer.is_valid())
			self.assertIn("matricule", serializer.errors)


@override_settings(MEDICAL_ENCRYPTION_KEY=Fernet.generate_key().decode())
class StudentApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User(
			id=uuid.uuid4(),
			email="admin@example.com",
			role=ROLE_SUPERADMIN,
			account_status=ACCOUNT_STATUS_ACTIVE,
		)
		self.client.force_authenticate(user=self.user)

	def test_get_students_list(self):
		with patch(
			"students.views.StudentService.list",
			return_value={
				"items": [
					{
						"id": "stu-1",
						"first_name": "Awa",
						"last_name": "Nana",
						"matricule": "MAT-001",
						"class_id": "class-a",
						"academic_year_id": "ay-2026",
						"is_active": True,
					}
				],
				"total": 1,
				"page": 1,
				"page_size": 20,
			},
		):
			response = self.client.get("/api/v1/students/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["total"], 1)
		self.assertEqual(response.data["items"][0]["matricule"], "MAT-001")

	def test_post_students_create(self):
		payload = {
			"first_name": "Awa",
			"last_name": "Nana",
			"matricule": "MAT-001",
			"birth_date": "2014-01-01T00:00:00+00:00",
			"birth_place": "Yaounde",
			"gender": "F",
			"class_id": "class-a",
			"academic_year_id": "ay-2026",
			"medical": {"allergies": ["lactose"]},
		}

		fernet = StudentService._fernet()
		encrypted_medical = fernet.encrypt(json.dumps(payload["medical"]).encode()).decode()

		with patch("students.serializers.StudentRepository.find_by_matricule", return_value=None), patch(
			"students.views.StudentService.create",
			return_value={
				"id": "stu-1",
				"first_name": "Awa",
				"last_name": "Nana",
				"matricule": "MAT-001",
				"birth_date": "2014-01-01T00:00:00+00:00",
				"birth_place": "Yaounde",
				"gender": "F",
				"class_id": "class-a",
				"academic_year_id": "ay-2026",
				"medical": encrypted_medical,
			},
		):
			response = self.client.post("/api/v1/students/", payload, format="json")

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["id"], "stu-1")
		self.assertEqual(response.data["medical"], payload["medical"])

	def test_promote_endpoint(self):
		with patch(
			"students.views.StudentService.promote",
			return_value={
				"id": "stu-1",
				"first_name": "Awa",
				"last_name": "Nana",
				"matricule": "MAT-001",
				"birth_date": "2014-01-01T00:00:00+00:00",
				"birth_place": "Yaounde",
				"gender": "F",
				"class_id": "class-b",
				"academic_year_id": "ay-2026",
				"medical": "",
			},
		) as promote_mock:
			response = self.client.post("/api/v1/students/stu-1/promote/", {"target_class_id": "class-b"}, format="json")

		self.assertEqual(response.status_code, 200)
		promote_mock.assert_called_once_with("stu-1", "class-b")

	def test_export_pdf_creates_job_and_dispatches_task(self):
		with patch("students.views.StudentService.create_export_job", return_value={"id": "job-1"}) as job_mock, patch(
			"students.views.generate_students_export_task.delay"
		) as delay_mock:
			response = self.client.get("/api/v1/students/export/pdf/")

		self.assertEqual(response.status_code, 202)
		self.assertEqual(response.data["job_id"], "job-1")
		job_mock.assert_called_once()
		delay_mock.assert_called_once()

	def test_export_excel_dispatches_task(self):
		with patch("students.views.StudentService.create_export_job", return_value={"id": "job-2"}) as job_mock, patch(
			"reports.tasks.generate_students_excel_task.delay"
		) as delay_mock:
			response = self.client.get("/api/v1/students/export/excel/")

		self.assertEqual(response.status_code, 202)
		self.assertEqual(response.data["job_id"], "job-2")
		job_mock.assert_called_once()
		delay_mock.assert_called_once()

	def test_get_student_detail(self):
		student = {
			"id": "stu-1",
			"first_name": "Awa",
			"last_name": "Nana",
			"matricule": "MAT-001",
			"birth_date": "2014-01-01T00:00:00+00:00",
			"birth_place": "Yaounde",
			"gender": "F",
			"class_id": "class-a",
			"academic_year_id": "ay-2026",
			"medical": "",
			"history": "[]",
		}
		with patch("students.views.StudentService.get", return_value=student):
			response = self.client.get("/api/v1/students/stu-1/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["matricule"], "MAT-001")

	def test_patch_student_update(self):
		student = {
			"id": "stu-1",
			"first_name": "Awa",
			"last_name": "Nana",
			"matricule": "MAT-001",
			"birth_date": "2014-01-01T00:00:00+00:00",
			"birth_place": "Yaounde",
			"gender": "F",
			"class_id": "class-b",
			"academic_year_id": "ay-2026",
			"medical": "",
		}
		with patch("students.serializers.StudentRepository.find_by_matricule", return_value=None), patch(
			"students.views.StudentService.update",
			return_value=student,
		) as update_mock:
			response = self.client.patch("/api/v1/students/stu-1/", {"class_id": "class-b"}, format="json")

		self.assertEqual(response.status_code, 200)
		update_mock.assert_called_once()

	def test_delete_student_soft_delete(self):
		with patch("students.views.StudentService.soft_delete") as delete_mock:
			response = self.client.delete("/api/v1/students/stu-1/")

		self.assertEqual(response.status_code, 204)
		delete_mock.assert_called_once_with("stu-1")

	def test_get_student_history(self):
		history = [{"event": "create", "at": "2026-01-01T00:00:00+00:00"}]
		with patch("students.views.StudentService.history", return_value=history):
			response = self.client.get("/api/v1/students/stu-1/history/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["history"], history)

	def test_enroll_endpoint_reactivates_and_creates_insc(self):
		student = {
			"id": "stu-1",
			"first_name": "Awa",
			"last_name": "Nana",
			"matricule": "MAT-001",
			"birth_date": "2014-01-01T00:00:00+00:00",
			"birth_place": "Yaounde",
			"gender": "F",
			"class_id": "class-a",
			"academic_year_id": "ay-2026",
			"medical": "",
		}
		with patch("students.views.StudentService.enroll", return_value=student) as enroll_mock:
			response = self.client.post(
				"/api/v1/students/stu-1/enroll/",
				{"class_id": "class-a", "academic_year_id": "ay-2026"},
				format="json",
			)

		self.assertEqual(response.status_code, 200)
		enroll_mock.assert_called_once_with("stu-1", "class-a", "ay-2026")

	def test_students_endpoints_reject_comptable(self):
		from accounts.models import ROLE_COMPTABLE

		comptable = User(
			id=uuid.uuid4(),
			email="comptable@example.com",
			role=ROLE_COMPTABLE,
			account_status=ACCOUNT_STATUS_ACTIVE,
		)
		self.client.force_authenticate(user=comptable)
		response = self.client.get("/api/v1/students/")
		self.assertEqual(response.status_code, 403)
