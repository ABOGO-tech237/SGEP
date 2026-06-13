from __future__ import annotations

import os
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from finance.repository import InvoiceRepository, PaymentRepository
from notifications.tasks import notify_payment_overdue_task

RECEIPTS_DIR = Path("/srv/sgep/media/receipts")


@shared_task(bind=True, max_retries=3)
def generate_receipt_task(self, payment_id: str) -> None:
	try:
		payment = PaymentRepository.get(payment_id)
		if not payment:
			return

		RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
		html_content = render_to_string(
			"pdf/receipt.html",
			{"payment": payment, "invoice": InvoiceRepository.get(payment.get("invoice_id", ""))},
		)
		file_path = RECEIPTS_DIR / f"receipt_{payment_id}.html"
		file_path.write_text(html_content, encoding="utf-8")

		try:
			from weasyprint import HTML

			pdf_path = RECEIPTS_DIR / f"receipt_{payment_id}.pdf"
			HTML(string=html_content).write_pdf(str(pdf_path))
			file_path = pdf_path
		except ImportError:  # pragma: no cover
			pass

		PaymentRepository.update(payment_id, {"receipt_path": str(file_path)})
	except Exception as exc:
		raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_overdue_reminders_task(self) -> dict:
	overdue_invoices = InvoiceRepository.list(status="pending")
	sent = 0
	for invoice in overdue_invoices:
		notify_payment_overdue_task.delay(invoice["id"], 7, dry_run=not settings.EMAIL_HOST)
		sent += 1
	return {"reminders_sent": sent}
