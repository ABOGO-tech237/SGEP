from __future__ import annotations

import uuid
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ACCOUNT_STATUS_ACTIVE, ACCOUNT_STATUS_SUSPENDED, ROLE_PARENT, User
from parents.services import ParentAccountService


class ParentAccountServiceTests(SimpleTestCase):
	def test_create_from_student_creates_account_and_dispatches_credentials(self):
		guardians = [{"email": "parent@example.com", "first_name": "Marie", "last_name": "Nana"}]

		with patch("parents.services.UserRepository.get_by_email", return_value=None), patch(
			"parents.services.UserRepository.create",
			return_value={"id": "parent-1", "email": "parent@example.com"},
		), patch("parents.services.send_parent_credentials_task.delay") as delay_mock:
			result = ParentAccountService.create_from_student("stu-1", guardians)

		self.assertTrue(result[0]["created"])
		delay_mock.assert_called_once()

	def test_suspend_updates_account_status_and_notifies(self):
		parents = [{"id": "parent-1", "email": "p1@example.com", "account_status": ACCOUNT_STATUS_ACTIVE}]

		with patch("parents.services.UserRepository.list_by_student_id", return_value=parents), patch(
			"parents.services.UserRepository.update",
			return_value={"id": "parent-1", "account_status": ACCOUNT_STATUS_SUSPENDED},
		), patch("parents.services.notify_account_suspended_task.delay") as delay_mock:
			ParentAccountService.suspend("stu-1")

		delay_mock.assert_called_once_with("parent-1")


class ParentPortalApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User(
			id=uuid.uuid4(),
			email="parent@example.com",
			role=ROLE_PARENT,
			account_status=ACCOUNT_STATUS_ACTIVE,
			student_id="stu-1",
		)

	def test_parent_me_any_status(self):
		self.client.force_authenticate(user=self.user)
		with patch(
			"parents.views.UserRepository.get_by_id",
			return_value={"id": str(self.user.id), "email": "parent@example.com", "account_status": "active", "student_id": "stu-1"},
		):
			response = self.client.get("/api/v1/parent/me/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["student_id"], "stu-1")

	def test_parent_grades_requires_active_account(self):
		suspended_user = User(
			id=uuid.uuid4(),
			email="parent@example.com",
			role=ROLE_PARENT,
			account_status=ACCOUNT_STATUS_SUSPENDED,
			student_id="stu-1",
		)
		self.client.force_authenticate(user=suspended_user)
		response = self.client.get("/api/v1/parent/me/grades/")
		self.assertEqual(response.status_code, 403)

	def test_parent_grades_returns_student_grades(self):
		self.client.force_authenticate(user=self.user)
		with patch(
			"parents.views.GradeService.grades_for_student",
			return_value=[{"id": "gr-1", "value": 14, "period_id": "seq-1"}],
		):
			response = self.client.get("/api/v1/parent/me/grades/?period_id=seq-1")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)

	def test_parent_invoices_accessible_when_suspended(self):
		suspended_user = User(
			id=uuid.uuid4(),
			email="parent@example.com",
			role=ROLE_PARENT,
			account_status=ACCOUNT_STATUS_SUSPENDED,
			student_id="stu-1",
		)
		self.client.force_authenticate(user=suspended_user)
		with patch("parents.views.InvoiceService.list", return_value=[{"id": "inv-1", "amount": 500}]):
			response = self.client.get("/api/v1/parent/me/invoices/")

		self.assertEqual(response.status_code, 200)

	def test_parent_attendance_returns_records(self):
		self.client.force_authenticate(user=self.user)
		with patch("parents.views.AttendanceService.list", return_value=[{"id": "att-1", "type": "absence"}]):
			response = self.client.get("/api/v1/parent/me/attendance/")

		self.assertEqual(response.status_code, 200)

	def test_parent_messages_list(self):
		self.client.force_authenticate(user=self.user)
		with patch(
			"parents.views.MessageService.list_for_parent",
			return_value=[{"id": "msg-1", "subject": "Question", "body": "Bonjour", "sender_id": "parent-1", "recipient_id": "admin", "is_read": False, "created_at": "2026-01-01"}],
		):
			response = self.client.get("/api/v1/parent/me/messages/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)

	def test_parent_messages_send(self):
		self.client.force_authenticate(user=self.user)
		with patch(
			"parents.views.MessageService.send_from_parent",
			return_value={"id": "msg-2", "subject": "Info", "body": "Merci", "sender_id": str(self.user.id), "recipient_id": "admin", "is_read": False, "created_at": "2026-01-02"},
		):
			response = self.client.post("/api/v1/parent/me/messages/", {"subject": "Info", "body": "Merci"}, format="json")

		self.assertEqual(response.status_code, 201)
