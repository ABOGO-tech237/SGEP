from __future__ import annotations

from celery import shared_task


@shared_task(bind=True, max_retries=3)
def send_parent_credentials_task(self, parent_id: str, email: str, temp_password: str) -> None:
    return None


@shared_task(bind=True, max_retries=3)
def send_account_suspended_notification_task(self, student_id: str) -> None:
    return None


@shared_task(bind=True, max_retries=3)
def send_account_reactivated_notification_task(self, student_id: str) -> None:
    return None


@shared_task(bind=True, max_retries=3)
def suspend_parent_accounts_for_new_year_task(self) -> list[dict]:
    return []