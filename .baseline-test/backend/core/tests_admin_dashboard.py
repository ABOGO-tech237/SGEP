from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_SUPERADMIN, User
from core.admin_dashboard_service import AdminDashboardService


class AdminDashboardServiceTests(SimpleTestCase):
	def test_build_returns_stats_and_activity(self):
		now = datetime(2026, 6, 2, 12, 0, tzinfo=timezone.utc)
		students = [
			{
				"id": "stu-1",
				"first_name": "Ada",
				"last_name": "Mbia",
				"class_id": "CM2-A",
				"is_active": True,
				"is_deleted": False,
				"created_at": "2026-06-01T08:00:00+00:00",
				"updated_at": "2026-06-01T08:00:00+00:00",
			},
			{
				"id": "stu-2",
				"first_name": "Ben",
				"last_name": "Tchamda",
				"class_id": "CM2-A",
				"is_active": False,
				"is_deleted": False,
				"created_at": "2026-05-20T08:00:00+00:00",
				"updated_at": "2026-05-30T08:00:00+00:00",
			},
		]

		with patch(
			"core.admin_dashboard_service.StudentRepository.list",
			return_value={"documents": students, "total": 2},
		), patch("core.admin_dashboard_service.ClassRepository.list", return_value=[{"id": "cls-1"}]), patch(
			"core.admin_dashboard_service.InvoiceService.dashboard",
			return_value={
				"total_billed": 1000,
				"total_collected": 600,
				"recovery_rate": 60.0,
				"overdue_count": 1,
			},
		), patch("core.admin_dashboard_service.AcademicYearRepository.get_active", return_value={"id": "y1", "name": "2025-2026"}):
			dashboard = AdminDashboardService.build(now=now)

		self.assertEqual(len(dashboard["stats"]), 6)
		self.assertEqual(dashboard["stats"][0]["label"], "Total élèves")
		self.assertEqual(dashboard["stats"][0]["value"], "2")
		self.assertEqual(dashboard["academic_year"]["name"], "2025-2026")
		self.assertEqual(len(dashboard["recent_activity"]), 2)
		self.assertEqual(dashboard["recent_activity"][1]["action"], "Suspendu")


class AdminDashboardApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User(
			id="admin-1",
			email="admin@example.com",
			role=ROLE_SUPERADMIN,
			account_status=ACCOUNT_STATUS_ACTIVE,
		)
		self.client.force_authenticate(user=self.user)

	def test_dashboard_endpoint(self):
		with patch(
			"core.views.AdminDashboardService.build",
			return_value={
				"generated_at": "2026-06-02T12:00:00+00:00",
				"academic_year": None,
				"stats": [],
				"finance": {},
				"recent_activity": [],
			},
		):
			response = self.client.get("/api/v1/admin/dashboard/")

		self.assertEqual(response.status_code, 200)
		self.assertIn("generated_at", response.data)
