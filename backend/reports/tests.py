from __future__ import annotations

from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ROLE_SUPERADMIN, User
from core.exceptions import NotFoundError
from reports.services import ReportJobService


class ReportJobServiceTests(SimpleTestCase):
	def test_get_status_returns_progress(self):
		with patch(
			"reports.services.ReportJobRepository.get",
			return_value={"id": "job-1", "status": "done", "file_path": "/tmp/export.xlsx", "type": "students_excel"},
		):
			result = ReportJobService.get_status("job-1")

		self.assertEqual(result["status"], "done")
		self.assertEqual(result["progress"], 100)

	def test_get_download_path_requires_done_status(self):
		with patch("reports.services.ReportJobRepository.get", return_value={"id": "job-1", "status": "pending"}):
			with self.assertRaises(NotFoundError):
				ReportJobService.get_download_path("job-1")


class ReportJobApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User(id="admin-1", email="admin@example.com", role=ROLE_SUPERADMIN, account_status="active")
		self.client.force_authenticate(user=self.user)

	def test_status_endpoint(self):
		with patch(
			"reports.views.ReportJobService.get_status",
			return_value={"job_id": "job-1", "status": "processing", "progress": 50},
		):
			response = self.client.get("/api/v1/reports/job-1/status/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["status"], "processing")


class ReportTaskTests(SimpleTestCase):
	def test_generate_finance_export_task_marks_job_done(self):
		from reports.tasks import generate_finance_export_task

		with patch("reports.tasks.ReportJobRepository.update") as update_mock, patch(
			"reports.tasks.excel_export.export_finance",
			return_value="/tmp/finance.xlsx",
		):
			generate_finance_export_task("job-1", {"academic_year_id": "ay-1"})

		self.assertEqual(update_mock.call_count, 2)
		self.assertEqual(update_mock.call_args_list[-1][0][1]["status"], "done")

	def test_generate_students_excel_task_marks_job_done(self):
		from reports.tasks import generate_students_excel_task

		with patch("reports.tasks.ReportJobRepository.update") as update_mock, patch(
			"reports.tasks.excel_export.export_students",
			return_value="/tmp/students.xlsx",
		):
			generate_students_excel_task("job-2", {"academic_year_id": "ay-1", "class_id": "class-a"})

		self.assertEqual(update_mock.call_count, 2)
		self.assertEqual(update_mock.call_args_list[-1][0][1]["status"], "done")
