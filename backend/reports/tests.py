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
