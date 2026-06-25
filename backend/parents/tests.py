from __future__ import annotations

import uuid
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ACCOUNT_STATUS_ACTIVE, ACCOUNT_STATUS_SUSPENDED, ROLE_PARENT, User
from parents.services import ParentAccountService
from students.services import StudentService


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

	def test_reactivate_updates_account_status_and_notifies(self):
		parents = [{"id": "parent-1", "email": "p1@example.com", "account_status": ACCOUNT_STATUS_SUSPENDED}]

		with patch("parents.services.UserRepository.list_by_student_id", return_value=parents), patch(
			"parents.services.UserRepository.update",
			return_value={"id": "parent-1", "account_status": ACCOUNT_STATUS_ACTIVE},
		), patch("parents.services.notify_account_reactivated_task.delay") as delay_mock:
			ParentAccountService.reactivate("stu-1")

		delay_mock.assert_called_once_with("parent-1")

	def test_enroll_reactivates_parent_accounts(self):
		student = {"id": "stu-1", "history": "[]", "first_name": "Awa", "last_name": "Nana", "matricule": "MAT-1"}

		with patch("students.services.StudentRepository.get", return_value=student), patch(
			"students.services.StudentRepository.update",
			return_value={"id": "stu-1", "class_id": "class-a", "academic_year_id": "ay-1"},
		), patch("students.services.ParentAccountService.reactivate") as reactivate_mock, patch(
			"finance.services.InvoiceService.ensure_inscription_invoice"
		):
			StudentService.enroll("stu-1", "class-a", "ay-1")

		reactivate_mock.assert_called_once_with("stu-1")


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
		with patch(
			"parents.views.InvoiceService.list",
			return_value=[
				{
					"id": "inv-1",
					"number": "INV-001",
					"student_id": "stu-1",
					"academic_year_id": "ay-1",
					"amount": 500,
					"status": "pending",
					"due_date": "2026-10-31T00:00:00+00:00",
				}
			],
		):
			response = self.client.get("/api/v1/parent/me/invoices/")

		self.assertEqual(response.status_code, 200)

	def test_parent_set_planned_payment_date(self):
		self.client.force_authenticate(user=self.user)
		with patch(
			"parents.views.InvoiceService.set_planned_payment_date",
			return_value={"id": "inv-1", "amount": 500, "planned_payment_date": "2026-10-15T00:00:00+00:00", "number": "INV-1", "student_id": "stu-1", "academic_year_id": "ay-1", "status": "pending", "due_date": "2026-10-31T00:00:00+00:00"},
		) as set_mock:
			response = self.client.patch(
				"/api/v1/parent/me/invoices/inv-1/planned-payment-date/",
				{"planned_payment_date": "2026-10-15T00:00:00+00:00"},
				format="json",
			)

		self.assertEqual(response.status_code, 200)
		set_mock.assert_called_once_with("inv-1", "stu-1", "2026-10-15T00:00:00+00:00")

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


class ParentTasksTests(SimpleTestCase):
	def test_suspend_inactive_parents_no_active_year(self):
		from parents.tasks import suspend_inactive_parents_task

		with patch("parents.tasks.AcademicYearRepository.get_active", return_value=None):
			result = suspend_inactive_parents_task()

		self.assertEqual(result["suspended"], 0)
		self.assertIn("Aucune année scolaire active", result["message"])

	def test_suspend_inactive_parents_wrong_year(self):
		from parents.tasks import suspend_inactive_parents_task

		parents = [{"id": "parent-1", "student_id": "stu-1", "account_status": ACCOUNT_STATUS_ACTIVE}]
		student = {"id": "stu-1", "academic_year_id": "ay-old", "is_active": True}

		with patch("parents.tasks.AcademicYearRepository.get_active", return_value={"id": "ay-active"}), patch(
			"parents.tasks.UserRepository.list_by_role",
			return_value=parents,
		), patch("parents.tasks.StudentRepository.get", return_value=student), patch(
			"parents.tasks.ParentAccountService.suspend_by_parent_id",
			return_value={"id": "parent-1", "account_status": ACCOUNT_STATUS_SUSPENDED},
		) as suspend_mock:
			result = suspend_inactive_parents_task()

		self.assertEqual(result["suspended"], 1)
		suspend_mock.assert_called_once_with("parent-1")

	def test_suspend_inactive_parents_keeps_enrolled(self):
		from parents.tasks import suspend_inactive_parents_task

		parents = [{"id": "parent-2", "student_id": "stu-2", "account_status": ACCOUNT_STATUS_ACTIVE}]
		student = {"id": "stu-2", "academic_year_id": "ay-active", "is_active": True}

		with patch("parents.tasks.AcademicYearRepository.get_active", return_value={"id": "ay-active"}), patch(
			"parents.tasks.UserRepository.list_by_role",
			return_value=parents,
		), patch("parents.tasks.StudentRepository.get", return_value=student), patch(
			"parents.tasks.ParentAccountService.suspend_by_parent_id"
		) as suspend_mock:
			result = suspend_inactive_parents_task()

		self.assertEqual(result["suspended"], 0)
		suspend_mock.assert_not_called()

	def test_suspend_inactive_parents_no_student_id(self):
		from parents.tasks import suspend_inactive_parents_task

		parents = [{"id": "parent-3", "student_id": None, "account_status": ACCOUNT_STATUS_ACTIVE}]

		with patch("parents.tasks.AcademicYearRepository.get_active", return_value={"id": "ay-active"}), patch(
			"parents.tasks.UserRepository.list_by_role",
			return_value=parents,
		), patch("parents.tasks.ParentAccountService.suspend_by_parent_id") as suspend_mock:
			result = suspend_inactive_parents_task()

		self.assertEqual(result["suspended"], 1)
		suspend_mock.assert_called_once_with("parent-3")
