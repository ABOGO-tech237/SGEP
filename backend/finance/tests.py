from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_COMPTABLE, User
from core.exceptions import ConflictError
from finance.services import (
	InvoiceService,
	PaymentService,
	reminder_days_since_start,
	should_send_overdue_reminder,
)


class FinanceServiceTests(SimpleTestCase):
	def test_generate_for_class_skips_duplicates(self):
		students = [{"id": "stu-1"}, {"id": "stu-2"}]
		with patch("finance.services.StudentRepository.list", return_value={"documents": students}), patch(
			"finance.services.FeeTypeRepository.get",
			return_value={"id": "fee-1", "amount": 50000},
		), patch("finance.services.InvoiceRepository.find_existing", return_value={"id": "exists"}), patch(
			"finance.services.InvoiceRepository.create"
		) as create_mock:
			count = InvoiceService.generate_for_class("class-a", "fee-1", "ay-1")

		self.assertEqual(count, 0)
		create_mock.assert_not_called()

	def test_record_payment_marks_invoice_paid(self):
		with patch(
			"finance.services.InvoiceService.get",
			return_value={"id": "inv-1", "amount": 100, "status": "pending"},
		), patch("finance.services.PaymentRepository.create", return_value={"id": "pay-1"}), patch(
			"finance.services.PaymentRepository.total_for_invoice",
			return_value=100.0,
		), patch("finance.services.InvoiceRepository.update") as update_mock, patch(
			"finance.tasks.generate_receipt_task.delay"
		), patch("core.audit.log_action"):
			payment = PaymentService.record("inv-1", 100, "cash", "REF-1", "comptable-1")

		self.assertEqual(payment["id"], "pay-1")
		update_mock.assert_called_once()

	def test_record_payment_rejects_paid_invoice(self):
		with patch(
			"finance.services.InvoiceService.get",
			return_value={"id": "inv-1", "amount": 100, "status": "paid"},
		):
			with self.assertRaises(ConflictError):
				PaymentService.record("inv-1", 50, "cash", "", "comptable-1")


class InvoiceReminderLogicTests(SimpleTestCase):
	def test_should_not_remind_before_planned_payment_date(self):
		now = datetime(2026, 10, 10, tzinfo=timezone.utc)
		invoice = {
			"status": "pending",
			"due_date": "2026-10-31T00:00:00+00:00",
			"planned_payment_date": "2026-10-15T00:00:00+00:00",
		}
		self.assertFalse(should_send_overdue_reminder(invoice, now=now))
		self.assertEqual(reminder_days_since_start(invoice, now=now), 0)

	def test_should_remind_after_planned_payment_date(self):
		now = datetime(2026, 10, 22, tzinfo=timezone.utc)
		invoice = {
			"status": "pending",
			"due_date": "2026-10-31T00:00:00+00:00",
			"planned_payment_date": "2026-10-15T00:00:00+00:00",
		}
		self.assertTrue(should_send_overdue_reminder(invoice, now=now))
		self.assertEqual(reminder_days_since_start(invoice, now=now), 7)

	def test_set_planned_payment_date_updates_invoice(self):
		with patch(
			"finance.services.InvoiceService.get",
			return_value={"id": "inv-1", "student_id": "stu-1", "status": "pending"},
		), patch(
			"finance.services.InvoiceRepository.update",
			return_value={"id": "inv-1", "planned_payment_date": "2026-10-15T00:00:00+00:00"},
		) as update_mock:
			invoice = InvoiceService.set_planned_payment_date("inv-1", "stu-1", "2026-10-15T00:00:00+00:00")

		update_mock.assert_called_once()
		self.assertEqual(invoice["planned_payment_date"], "2026-10-15T00:00:00+00:00")

	def test_generate_for_class_uses_due_date(self):
		students = [{"id": "stu-1"}]
		with patch("finance.services.StudentRepository.list", return_value={"documents": students}), patch(
			"finance.services.FeeTypeRepository.get",
			return_value={"id": "fee-1", "amount": 50000},
		), patch("finance.services.InvoiceRepository.find_existing", return_value=None), patch(
			"finance.services.InvoiceRepository.create"
		) as create_mock:
			InvoiceService.generate_for_class("class-a", "fee-1", "ay-1", due_date="2026-10-31T00:00:00+00:00")

		create_mock.assert_called_once()
		self.assertEqual(create_mock.call_args[0][0]["due_date"], "2026-10-31T00:00:00+00:00")

	def test_generate_for_student_creates_invoice(self):
		with patch(
			"finance.services.StudentRepository.get",
			return_value={"id": "stu-1"},
		), patch(
			"finance.services.FeeTypeRepository.get",
			return_value={"id": "fee-insc", "amount": 15000},
		), patch("finance.services.InvoiceRepository.find_existing", return_value=None), patch(
			"finance.services.InvoiceRepository.create"
		) as create_mock:
			count = InvoiceService.generate_for_student("stu-1", "fee-insc", "ay-1")

		self.assertEqual(count, 1)
		create_mock.assert_called_once()
		payload = create_mock.call_args[0][0]
		self.assertEqual(payload["student_id"], "stu-1")
		self.assertEqual(payload["academic_year_id"], "ay-1")
		self.assertEqual(payload["fee_type_id"], "fee-insc")

	def test_generate_for_student_skips_existing_invoice(self):
		with patch(
			"finance.services.StudentRepository.get",
			return_value={"id": "stu-1"},
		), patch(
			"finance.services.FeeTypeRepository.get",
			return_value={"id": "fee-insc", "amount": 15000},
		), patch("finance.services.InvoiceRepository.find_existing", return_value={"id": "inv-1"}), patch(
			"finance.services.InvoiceRepository.create"
		) as create_mock:
			count = InvoiceService.generate_for_student("stu-1", "fee-insc", "ay-1")

		self.assertEqual(count, 0)
		create_mock.assert_not_called()

	def test_ensure_inscription_invoice_uses_insc_fee_type(self):
		with patch(
			"finance.services.FeeTypeRepository.find_by_code",
			return_value={"id": "fee-insc", "code": "INSC", "amount": 15000},
		) as find_mock, patch(
			"finance.services.InvoiceService.generate_for_student",
			return_value=1,
		) as generate_mock:
			count = InvoiceService.ensure_inscription_invoice("stu-1", "ay-1")

		find_mock.assert_called_once_with("INSC")
		generate_mock.assert_called_once_with("stu-1", "fee-insc", "ay-1")
		self.assertEqual(count, 1)

	def test_ensure_inscription_invoice_skips_when_fee_type_missing(self):
		with patch("finance.services.FeeTypeRepository.find_by_code", return_value=None), patch(
			"finance.services.InvoiceService.generate_for_student"
		) as generate_mock:
			count = InvoiceService.ensure_inscription_invoice("stu-1", "ay-1")

		self.assertEqual(count, 0)
		generate_mock.assert_not_called()


class FinanceApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User(
			id=uuid.uuid4(),
			email="comptable@example.com",
			role=ROLE_COMPTABLE,
			account_status=ACCOUNT_STATUS_ACTIVE,
		)
		self.client.force_authenticate(user=self.user)

	def test_dashboard_endpoint(self):
		with patch(
			"finance.views.InvoiceService.dashboard",
			return_value={"total_billed": 1000, "total_collected": 500, "recovery_rate": 50.0, "overdue_count": 2},
		):
			response = self.client.get("/api/v1/finance/dashboard/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["recovery_rate"], 50.0)

	def test_payment_create(self):
		with patch(
			"finance.views.PaymentService.record",
			return_value={"id": "pay-1", "invoice_id": "inv-1", "amount": 100, "method": "cash", "status": "completed"},
		):
			response = self.client.post(
				"/api/v1/finance/payments/",
				{"invoice_id": "inv-1", "amount": 100, "method": "cash"},
				format="json",
			)

		self.assertEqual(response.status_code, 201)
