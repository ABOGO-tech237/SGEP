from __future__ import annotations

from datetime import datetime, timezone

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from accounts.repository import UserRepository
from notifications.repository import NotificationRepository

NOTIFICATION_STATUS_SENT = "sent"
NOTIFICATION_STATUS_FAILED = "failed"
NOTIFICATION_STATUS_PENDING = "pending"


def _now() -> str:
	return datetime.now(timezone.utc).isoformat()


def _create_notification_log(
	user_id: str,
	title: str,
	message: str,
	notification_type: str,
	status: str = NOTIFICATION_STATUS_PENDING,
	error: str = "",
) -> dict:
	return NotificationRepository.create(
		{
			"user_id": user_id,
			"title": title,
			"message": message,
			"type": notification_type,
			"status": status,
			"sent_at": _now() if status == NOTIFICATION_STATUS_SENT else "",
			"error": error,
		}
	)


def _send_email(subject: str, message: str, recipient: str, dry_run: bool) -> None:
	if dry_run:
		return
	send_mail(
		subject=subject,
		message=message,
		from_email=settings.DEFAULT_FROM_EMAIL,
		recipient_list=[recipient],
		fail_silently=False,
	)


def _get_parent_for_student(student_id: str) -> dict | None:
	parents = UserRepository.list_by_student_id(student_id)
	if not parents:
		return None
	return parents[0]


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def notify_parent_absence_task(self, student_id: str, date: str, absence_type: str, dry_run: bool = False) -> None:
	parent = _get_parent_for_student(student_id)
	if not parent:
		return

	title = "Absence enregistrée"
	message = f"Une {absence_type} a été enregistrée pour votre enfant le {date}."
	notification = _create_notification_log(parent["id"], title, message, "absence")

	try:
		_send_email(title, message, parent["email"], dry_run)
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_SENT, "sent_at": _now()})
	except Exception as exc:
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_FAILED, "error": str(exc)})
		raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def notify_bulletin_published_task(self, student_id: str, period_label: str, dry_run: bool = False) -> None:
	parent = _get_parent_for_student(student_id)
	if not parent:
		return

	title = "Bulletin disponible"
	message = f"Le bulletin de {period_label} est disponible."
	notification = _create_notification_log(parent["id"], title, message, "bulletin")

	try:
		_send_email(title, message, parent["email"], dry_run)
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_SENT, "sent_at": _now()})
	except Exception as exc:
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_FAILED, "error": str(exc)})
		raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def notify_payment_overdue_task(self, invoice_id: str, overdue_days: int, dry_run: bool = False) -> None:
	title = "Facture en retard"
	message = f"La facture {invoice_id} est en retard de {overdue_days} jours."
	notification = _create_notification_log(invoice_id, title, message, "payment_overdue")

	try:
		if not dry_run:
			_send_email(title, message, settings.DEFAULT_FROM_EMAIL, dry_run=False)
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_SENT, "sent_at": _now()})
	except Exception as exc:
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_FAILED, "error": str(exc)})
		raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def send_parent_credentials_task(
	self, parent_id: str, email: str, temp_password: str, dry_run: bool = False
) -> None:
	title = "Bienvenue sur SGEP"
	message = (
		f"Votre compte parent a été créé.\n"
		f"Email: {email}\n"
		f"Mot de passe temporaire: {temp_password}\n"
		f"Veuillez changer votre mot de passe à la première connexion."
	)
	notification = _create_notification_log(parent_id, title, message, "credentials")

	try:
		_send_email(title, message, email, dry_run)
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_SENT, "sent_at": _now()})
	except Exception as exc:
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_FAILED, "error": str(exc)})
		raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def notify_account_suspended_task(self, parent_id: str, dry_run: bool = False) -> None:
	parent = UserRepository.get_by_id(parent_id)
	if not parent:
		return

	title = "Compte suspendu"
	message = "Votre compte parent a été suspendu en attente de réinscription."
	notification = _create_notification_log(parent_id, title, message, "account_suspended")

	try:
		_send_email(title, message, parent["email"], dry_run)
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_SENT, "sent_at": _now()})
	except Exception as exc:
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_FAILED, "error": str(exc)})
		raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def notify_account_reactivated_task(self, parent_id: str, dry_run: bool = False) -> None:
	parent = UserRepository.get_by_id(parent_id)
	if not parent:
		return

	title = "Compte réactivé"
	message = "Votre compte parent a été réactivé."
	notification = _create_notification_log(parent_id, title, message, "account_reactivated")

	try:
		_send_email(title, message, parent["email"], dry_run)
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_SENT, "sent_at": _now()})
	except Exception as exc:
		NotificationRepository.update(notification["id"], {"status": NOTIFICATION_STATUS_FAILED, "error": str(exc)})
		raise self.retry(exc=exc, countdown=120)
