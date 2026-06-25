from __future__ import annotations

import uuid
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_COMPTABLE, ROLE_PARENT, ROLE_SUPERADMIN, User


class PermissionsMatrixTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()

	def test_comptable_can_access_finance_dashboard(self):
		user = User(
			id=uuid.uuid4(),
			email="comptable@example.com",
			role=ROLE_COMPTABLE,
			account_status=ACCOUNT_STATUS_ACTIVE,
		)
		self.client.force_authenticate(user=user)
		with patch(
			"finance.views.InvoiceService.dashboard",
			return_value={"total_billed": 0, "total_collected": 0, "recovery_rate": 0.0, "overdue_count": 0},
		):
			response = self.client.get("/api/v1/finance/dashboard/")

		self.assertEqual(response.status_code, 200)

	def test_comptable_cannot_access_students_list(self):
		user = User(
			id=uuid.uuid4(),
			email="comptable@example.com",
			role=ROLE_COMPTABLE,
			account_status=ACCOUNT_STATUS_ACTIVE,
		)
		self.client.force_authenticate(user=user)
		response = self.client.get("/api/v1/students/")
		self.assertEqual(response.status_code, 403)

	def test_parent_cannot_access_admin_dashboard(self):
		user = User(
			id=uuid.uuid4(),
			email="parent@example.com",
			role=ROLE_PARENT,
			account_status=ACCOUNT_STATUS_ACTIVE,
			student_id="stu-1",
		)
		self.client.force_authenticate(user=user)
		response = self.client.get("/api/v1/admin/dashboard/")
		self.assertEqual(response.status_code, 403)

	def test_superadmin_can_access_students_list(self):
		user = User(
			id=uuid.uuid4(),
			email="admin@example.com",
			role=ROLE_SUPERADMIN,
			account_status=ACCOUNT_STATUS_ACTIVE,
		)
		self.client.force_authenticate(user=user)
		with patch(
			"students.views.StudentService.list",
			return_value={"items": [], "total": 0, "page": 1, "page_size": 20},
		):
			response = self.client.get("/api/v1/students/")

		self.assertEqual(response.status_code, 200)
