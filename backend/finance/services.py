from __future__ import annotations

from datetime import datetime, timezone

from core.exceptions import ConflictError, NotFoundError
from students.repository import StudentRepository

from .repository import FeeTypeRepository, InvoiceRepository, PaymentRepository


class InvoiceService:
	@staticmethod
	def _now() -> str:
		return datetime.now(timezone.utc).isoformat()

	@staticmethod
	def list(student_id: str | None = None, status: str | None = None) -> list[dict]:
		return InvoiceRepository.list(student_id=student_id, status=status)

	@staticmethod
	def get(invoice_id: str) -> dict:
		invoice = InvoiceRepository.get(invoice_id)
		if not invoice:
			raise NotFoundError(f"Facture {invoice_id} introuvable.")
		return invoice

	@staticmethod
	def _generate_for_students(students: list[dict], fee_type_id: str, academic_year_id: str) -> int:
		fee_type = FeeTypeRepository.get(fee_type_id)
		if not fee_type:
			raise NotFoundError(f"Type de frais {fee_type_id} introuvable.")

		created_count = 0
		for student in students:
			if InvoiceRepository.find_existing(student["id"], fee_type_id, academic_year_id):
				continue
			InvoiceRepository.create(
				{
					"number": f"INV-{student['id'][:8]}-{fee_type_id[:4]}",
					"student_id": student["id"],
					"academic_year_id": academic_year_id,
					"fee_type_id": fee_type_id,
					"amount": float(fee_type.get("amount", 0)),
					"status": "pending",
					"due_date": InvoiceService._now(),
					"is_deleted": False,
					"created_at": InvoiceService._now(),
					"updated_at": InvoiceService._now(),
				}
			)
			created_count += 1
		return created_count

	@staticmethod
	def generate_for_class(class_id: str, fee_type_id: str, academic_year_id: str) -> int:
		response = StudentRepository.list(class_id=class_id, is_active=True, page_size=500)
		return InvoiceService._generate_for_students(response.get("documents", []), fee_type_id, academic_year_id)

	@staticmethod
	def generate_bulk(academic_year_id: str, fee_type_id: str) -> int:
		response = StudentRepository.list(academic_year_id=academic_year_id, is_active=True, page_size=500)
		return InvoiceService._generate_for_students(response.get("documents", []), fee_type_id, academic_year_id)

	@staticmethod
	def overdue() -> list[dict]:
		return InvoiceRepository.list(status="pending")

	@staticmethod
	def dashboard() -> dict:
		invoices = InvoiceRepository.list()
		payments = PaymentRepository.list()
		total_billed = sum(float(inv.get("amount", 0)) for inv in invoices)
		total_collected = sum(float(p.get("amount", 0)) for p in payments)
		overdue_count = len([inv for inv in invoices if inv.get("status") == "pending"])
		recovery_rate = round((total_collected / total_billed) * 100, 2) if total_billed else 0.0
		return {
			"total_billed": total_billed,
			"total_collected": total_collected,
			"recovery_rate": recovery_rate,
			"overdue_count": overdue_count,
		}


class PaymentService:
	@staticmethod
	def _now() -> str:
		return datetime.now(timezone.utc).isoformat()

	@staticmethod
	def record(invoice_id: str, amount: float, method: str, reference: str, recorded_by: str) -> dict:
		from finance.tasks import generate_receipt_task

		invoice = InvoiceService.get(invoice_id)
		if invoice.get("status") == "paid":
			raise ConflictError("La facture est déjà soldée.")

		payment = PaymentRepository.create(
			{
				"invoice_id": invoice_id,
				"amount": amount,
				"method": method,
				"reference": reference,
				"status": "completed",
				"recorded_by": recorded_by,
				"receipt_path": "",
				"is_deleted": False,
				"created_at": PaymentService._now(),
				"updated_at": PaymentService._now(),
			}
		)

		total_paid = PaymentRepository.total_for_invoice(invoice_id)
		if total_paid >= float(invoice.get("amount", 0)):
			InvoiceRepository.update(invoice_id, {"status": "paid", "updated_at": PaymentService._now()})

		generate_receipt_task.delay(payment["id"])
		from core.audit import log_action

		log_action(recorded_by, "CREATE", "payments", payment["id"], {"invoice_id": invoice_id, "amount": amount}, "")
		return payment

	@staticmethod
	def get(payment_id: str) -> dict:
		payment = PaymentRepository.get(payment_id)
		if not payment:
			raise NotFoundError(f"Paiement {payment_id} introuvable.")
		return payment
