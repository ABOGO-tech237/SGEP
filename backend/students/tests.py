from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from students.serializers import StudentCreateSerializer
from students.services import StudentService
from students.views import (
	StudentDetailView,
	StudentEnrollView,
	StudentHistoryView,
	StudentListView,
	StudentPromoteView,
	StudentSwaggerView,
)


def _superadmin_user():
	user_model = get_user_model()
	user = user_model(
		email="admin@example.com",
		role="superadmin",
		account_status="active",
		is_staff=True,
		is_superuser=True,
		is_active=True,
	)
	user.id = "00000000-0000-0000-0000-000000000001"
	return user


class StudentFlowTests(APITestCase):
	def setUp(self) -> None:
		self.factory = APIRequestFactory()
		self.user = _superadmin_user()

	def test_student_create_serializer_rejects_duplicate_matricule(self) -> None:
		payload = {
			"first_name": "Jean",
			"last_name": "Dupont",
			"matricule": "MAT-001",
			"birth_date": "2026-05-15T08:00:00Z",
			"birth_place": "Yaounde",
			"gender": "M",
			"parent": {
				"first_name": "Marie",
				"last_name": "Dupont",
				"relationship": "Mere",
				"phone": "+237600000000",
				"email": "parent@example.com",
			},
		}

		with patch("students.repository.StudentRepository.find_by_matricule", return_value={"id": "existing"}):
			serializer = StudentCreateSerializer(data=payload)
			self.assertFalse(serializer.is_valid())
			self.assertIn("matricule", serializer.errors)

	@patch("students.services.ParentAccountService.create_from_student")
	@patch("students.repository.StudentHistoryRepository.create")
	@patch("students.repository.StudentRepository.create")
	@patch("students.repository.StudentRepository.update")
	def test_student_service_create_triggers_parent_account(
		self,
		mock_update,
		mock_create,
		mock_history,
		mock_parent_service,
	) -> None:
		mock_create.return_value = {
			"id": "student-1",
			"first_name": "Jean",
			"last_name": "Dupont",
			"matricule": "MAT-001",
			"class_id": "class-1",
			"academic_year_id": "ay-1",
			"school_id": "school-1",
			"medical": {"allergies": ["pollen"]},
			"is_active": True,
		}
		mock_update.return_value = {**mock_create.return_value, "parent_user_id": "user-1"}
		mock_parent_service.return_value = [{"id": "link-1", "user_id": "user-1"}]

		result = StudentService.create(
			{
				"first_name": "Jean",
				"last_name": "Dupont",
				"matricule": "MAT-001",
				"birth_date": "2026-05-15T08:00:00Z",
				"birth_place": "Yaounde",
				"gender": "M",
				"school_id": "school-1",
				"class_id": "class-1",
				"academic_year_id": "ay-1",
				"medical": {"allergies": ["pollen"]},
				"parent": {
					"first_name": "Marie",
					"last_name": "Dupont",
					"relationship": "Mere",
					"phone": "+237600000000",
					"email": "parent@example.com",
				},
			}
		)

		self.assertEqual(result["parent_user_id"], "user-1")
		mock_parent_service.assert_called_once()
		mock_history.assert_called()

	@patch("students.repository.StudentRepository.list")
	def test_student_list_view_returns_paginated_results(self, mock_list) -> None:
		mock_list.return_value = {
			"documents": [
				{
					"id": "student-1",
					"matricule": "MAT-001",
					"first_name": "Jean",
					"last_name": "Dupont",
					"class_id": "class-1",
					"academic_year_id": "ay-1",
					"current_level_id": "level-1",
					"is_active": True,
				}
			],
			"total": 1,
		}

		request = self.factory.get("/api/v1/students/?page=1&page_size=10")
		force_authenticate(request, user=self.user)
		response = StudentListView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["count"], 1)
		self.assertEqual(response.data["results"][0]["matricule"], "MAT-001")

	@patch("students.repository.StudentRepository.get")
	@patch("students.repository.StudentHistoryRepository.list")
	def test_student_history_view_returns_history(self, mock_history_list, mock_get) -> None:
		mock_get.return_value = {
			"id": "student-1",
			"matricule": "MAT-001",
			"first_name": "Jean",
			"last_name": "Dupont",
			"is_active": True,
		}
		mock_history_list.return_value = [
			{"id": "history-1", "student_id": "student-1", "action": "create"}
		]

		request = self.factory.get("/api/v1/students/student-1/history/")
		force_authenticate(request, user=self.user)
		response = StudentHistoryView.as_view()(request, student_id="student-1")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data[0]["action"], "create")

	@patch("students.repository.StudentRepository.get")
	@patch("students.repository.StudentRepository.get_class")
	@patch("students.repository.StudentRepository.update")
	@patch("students.repository.StudentHistoryRepository.create")
	def test_student_enroll_view_updates_class_and_history(
		self,
		mock_history_create,
		mock_update,
		mock_get_class,
		mock_get_student,
	) -> None:
		mock_get_student.return_value = {
			"id": "student-1",
			"matricule": "MAT-001",
			"first_name": "Jean",
			"last_name": "Dupont",
			"class_id": "class-old",
			"birth_date": "2014-01-01T00:00:00Z",
			"birth_place": "Yaounde",
			"gender": "M",
			"medical": {},
			"academic_year_id": "ay-1",
			"is_active": True,
		}
		mock_get_class.return_value = {"id": "class-new", "level_id": "level-2"}
		mock_update.return_value = {
			"id": "student-1",
			"matricule": "MAT-001",
			"first_name": "Jean",
			"last_name": "Dupont",
			"class_id": "class-new",
			"birth_date": "2014-01-01T00:00:00Z",
			"birth_place": "Yaounde",
			"gender": "M",
			"medical": {},
			"academic_year_id": "ay-1",
			"current_level_id": "level-2",
			"is_active": True,
		}

		request = self.factory.post(
			"/api/v1/students/student-1/enroll/",
			{"class_id": "class-new", "academic_year_id": "ay-1"},
			format="json",
		)
		force_authenticate(request, user=self.user)
		response = StudentEnrollView.as_view()(request, student_id="student-1")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["class_id"], "class-new")
		mock_history_create.assert_called_once()

	@patch("students.repository.StudentRepository.get")
	@patch("students.repository.StudentRepository.get_class")
	@patch("students.repository.StudentRepository.update")
	@patch("students.repository.StudentHistoryRepository.create")
	def test_student_promote_view_moves_to_target_class(
		self,
		mock_history_create,
		mock_update,
		mock_get_class,
		mock_get_student,
	) -> None:
		mock_get_student.return_value = {
			"id": "student-1",
			"matricule": "MAT-001",
			"first_name": "Jean",
			"last_name": "Dupont",
			"class_id": "class-old",
			"birth_date": "2014-01-01T00:00:00Z",
			"birth_place": "Yaounde",
			"gender": "M",
			"medical": {},
			"academic_year_id": "ay-1",
			"is_active": True,
		}
		mock_get_class.return_value = {"id": "class-up", "level_id": "level-3", "academic_year_id": "ay-2"}
		mock_update.return_value = {
			"id": "student-1",
			"matricule": "MAT-001",
			"first_name": "Jean",
			"last_name": "Dupont",
			"class_id": "class-up",
			"birth_date": "2014-01-01T00:00:00Z",
			"birth_place": "Yaounde",
			"gender": "M",
			"medical": {},
			"academic_year_id": "ay-2",
			"current_level_id": "level-3",
			"is_active": True,
		}

		request = self.factory.post(
			"/api/v1/students/student-1/promote/",
			{"target_class_id": "class-up"},
			format="json",
		)
		force_authenticate(request, user=self.user)
		response = StudentPromoteView.as_view()(request, student_id="student-1")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["class_id"], "class-up")
		self.assertEqual(response.data["academic_year_id"], "ay-2")
		mock_history_create.assert_called_once()


class StudentSerializerMedicalTests(APITestCase):
	@patch("students.repository.StudentRepository.find_by_matricule", return_value=None)
	def test_student_create_serializer_accepts_medical_json(self, _mock_find) -> None:
		serializer = StudentCreateSerializer(
			data={
				"first_name": "Jean",
				"last_name": "Dupont",
				"matricule": "MAT-002",
				"birth_date": "2026-05-15T08:00:00Z",
				"birth_place": "Yaounde",
				"gender": "M",
				"medical": {"allergies": ["arachides"], "notes": "Porte des lunettes"},
				"parent": {
					"first_name": "Marie",
					"last_name": "Dupont",
					"relationship": "Mere",
					"phone": "+237600000000",
					"email": "parent@example.com",
				},
			}
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)


class StudentSwaggerTests(APITestCase):
	def setUp(self) -> None:
		self.factory = APIRequestFactory()
		self.user = _superadmin_user()

	def test_student_swagger_view_exposes_student_paths(self) -> None:
		request = self.factory.get("/api/v1/students/swagger/")
		force_authenticate(request, user=self.user)
		response = StudentSwaggerView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("/api/v1/students/", response.data["paths"])
		self.assertIn("/api/v1/students/{student_id}/enroll/", response.data["paths"])
		self.assertIn("/api/v1/students/{student_id}/promote/", response.data["paths"])
		self.assertIn("bearerAuth", response.data["components"]["securitySchemes"])
		self.assertIn("Student", response.data["components"]["schemas"])
		self.assertIn("ExportJobResponse", response.data["components"]["schemas"])

from django.test import TestCase

# Create your tests here.
