from __future__ import annotations

import uuid
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_COMPTABLE, User
from finance.services import InvoiceService, PaymentService
from core.exceptions import ConflictError


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
