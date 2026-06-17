from __future__ import annotations

from celery import shared_task

from accounts.models import ACCOUNT_STATUS_ACTIVE
from accounts.repository import UserRepository
from core.repository import AcademicYearRepository
from parents.services import ParentAccountService
from students.repository import StudentRepository


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def suspend_inactive_parents_task(self) -> dict:
	"""Suspend parent accounts whose child is not enrolled in the active academic year."""
	active_year = AcademicYearRepository.get_active()
	if not active_year:
		return {"suspended": 0, "message": "Aucune année scolaire active."}

	active_year_id = active_year["id"]
	parents = UserRepository.list_by_role("parent", account_status=ACCOUNT_STATUS_ACTIVE)
	suspended = 0

	for parent in parents:
		student_id = parent.get("student_id")
		if not student_id:
			ParentAccountService.suspend_by_parent_id(parent["id"])
			suspended += 1
			continue

		student = StudentRepository.get(student_id)
		if not student or not student.get("is_active", True):
			ParentAccountService.suspend_by_parent_id(parent["id"])
			suspended += 1
			continue

		if student.get("academic_year_id") != active_year_id:
			ParentAccountService.suspend_by_parent_id(parent["id"])
			suspended += 1

	return {"suspended": suspended, "academic_year_id": active_year_id}
