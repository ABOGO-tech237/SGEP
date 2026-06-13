from __future__ import annotations

from celery import shared_task

from parents.services import ParentAccountService


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def suspend_inactive_parents_task(self) -> dict:
	"""Suspend parent accounts at the start of a new academic year."""
	# Placeholder: actual student/year filtering will be wired when enrollments module is complete.
	return {"suspended": 0, "message": "Annual parent suspension task executed."}
