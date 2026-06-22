from __future__ import annotations

import uuid
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_SUPERADMIN, User
from grades.serializers import BulkGradeCreateSerializer, GradeCreateSerializer
from grades.services import GradeService


class GradeServiceTests(SimpleTestCase):
	def test_calculate_averages_with_ex_aequo_ranks(self):
		grades = [
			{"student_id": "stu-1", "subject_id": "math", "value": 15, "coefficient": 2},
			{"student_id": "stu-1", "subject_id": "fr", "value": 13, "coefficient": 1},
			{"student_id": "stu-2", "subject_id": "math", "value": 14, "coefficient": 2},
			{"student_id": "stu-2", "subject_id": "fr", "value": 14, "coefficient": 1},
			{"student_id": "stu-3", "subject_id": "math", "value": 10, "coefficient": 2},
		]

		with patch("grades.services.GradeService._student_ids_for_class", return_value=["stu-1", "stu-2", "stu-3"]), patch(
			"grades.services.GradeRepository.list",
			return_value=grades,
		):
			results = GradeService.calculate_averages("class-a", "seq-1")

		self.assertEqual(results["stu-1"]["average"], 14.33)
		self.assertEqual(results["stu-2"]["average"], 14.0)
		self.assertEqual(results["stu-1"]["rank"], 1)
		self.assertEqual(results["stu-2"]["rank"], 2)

	def test_bulk_input_creates_grades(self):
		data = [
			{
				"student_id": "stu-1",
				"subject_id": "math",
				"period_id": "seq-1",
				"value": 12,
				"academic_year_id": "ay-1",
			}
		]

		with patch("grades.services.SubjectRepository.get", return_value={"coefficient": 2}), patch(
			"grades.services.GradeRepository.bulk_create",
			return_value=[{"id": "gr-1", "student_id": "stu-1", "subject_id": "math", "sequence": "seq-1", "value": 12, "coefficient": 2}],
		) as bulk_mock:
			created = GradeService.bulk_input(data, "admin-1")

		self.assertEqual(len(created), 1)
		self.assertEqual(created[0]["period_id"], "seq-1")
		bulk_mock.assert_called_once()


class GradeSerializerTests(SimpleTestCase):
	def test_grade_create_validates_value_range(self):
		payload = {
			"student_id": "stu-1",
			"subject_id": "math",
			"period_id": "seq-1",
			"value": 25,
		}
		serializer = GradeCreateSerializer(data=payload)
		self.assertFalse(serializer.is_valid())

	def test_bulk_serializer_accepts_list(self):
		payload = {
			"grades": [
				{"student_id": "stu-1", "subject_id": "math", "period_id": "seq-1", "value": 14},
			]
		}
		serializer = BulkGradeCreateSerializer(data=payload)
		self.assertTrue(serializer.is_valid())


class GradeApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User(
			id=uuid.uuid4(),
			email="admin@example.com",
			role=ROLE_SUPERADMIN,
			account_status=ACCOUNT_STATUS_ACTIVE,
		)
		self.client.force_authenticate(user=self.user)

	def test_get_grades_list(self):
		with patch(
			"grades.views.GradeService.list",
			return_value=[{"id": "gr-1", "student_id": "stu-1", "subject_id": "math", "period_id": "seq-1", "value": 14, "coefficient": 2}],
		):
			response = self.client.get("/api/v1/grades/?class_id=class-a&period_id=seq-1")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)

	def test_post_bulk_grades(self):
		payload = {
			"grades": [
				{"student_id": "stu-1", "subject_id": "math", "period_id": "seq-1", "value": 14},
			]
		}
		with patch(
			"grades.views.GradeService.bulk_input",
			return_value=[{"id": "gr-1", "student_id": "stu-1", "subject_id": "math", "period_id": "seq-1", "value": 14, "coefficient": 2}],
		):
			response = self.client.post("/api/v1/grades/bulk/", payload, format="json")

		self.assertEqual(response.status_code, 201)

	def test_report_cards_generate(self):
		with patch("grades.views.ReportCardService.create_generation_job", return_value={"id": "job-1"}), patch(
			"grades.views.generate_class_report_cards_task.delay"
		) as delay_mock:
			response = self.client.post(
				"/api/v1/report-cards/generate/",
				{"class_id": "class-a", "period_id": "seq-1"},
				format="json",
			)

		self.assertEqual(response.status_code, 202)
		self.assertEqual(response.data["job_id"], "job-1")
		delay_mock.assert_called_once()

	def test_report_card_status(self):
		with patch(
			"grades.views.ReportCardService.get_job_status",
			return_value={"status": "processing", "progress": 50, "file_path": ""},
		):
			response = self.client.get("/api/v1/report-cards/job-1/status/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["progress"], 50)

	def test_report_card_publish(self):
		with patch(
			"grades.views.ReportCardService.publish",
			return_value={
				"id": "rc-1",
				"student_id": "stu-1",
				"academic_year_id": "ay-1",
				"sequence": "seq-1",
				"period_id": "seq-1",
				"status": "published",
				"file_path": "/tmp/bulletin.pdf",
				"generated_at": "2026-06-01T00:00:00+00:00",
			},
		) as publish_mock:
			response = self.client.post("/api/v1/report-cards/rc-1/publish/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["status"], "published")
		publish_mock.assert_called_once_with("rc-1")

	def test_report_card_download(self):
		import os
		import tempfile

		with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
			tmp.write(b"pdf-content")
			tmp_path = tmp.name

		try:
			with patch(
				"grades.views.ReportCardService.get",
				return_value={
					"id": "rc-1",
					"student_id": "stu-1",
					"sequence": "seq-1",
					"period_id": "seq-1",
					"status": "published",
					"file_path": tmp_path,
				},
			):
				response = self.client.get("/api/v1/report-cards/rc-1/download/")

			self.assertEqual(response.status_code, 200)
		finally:
			os.unlink(tmp_path)
