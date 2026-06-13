from __future__ import annotations

from celery import shared_task

from reports import excel as excel_export
from students.repository import ReportJobRepository


@shared_task(bind=True, max_retries=3)
def generate_finance_export_task(self, job_id: str, params: dict | None = None) -> None:
	try:
		ReportJobRepository.update(job_id, {"status": "processing"})
		params = params or {}
		file_path = excel_export.export_finance(params.get("academic_year_id", ""))
		ReportJobRepository.update(job_id, {"status": "done", "file_path": file_path})
	except Exception as exc:
		ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
		raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_students_excel_task(self, job_id: str, params: dict | None = None) -> None:
	try:
		ReportJobRepository.update(job_id, {"status": "processing"})
		params = params or {}
		file_path = excel_export.export_students(
			params.get("academic_year_id", ""),
			params.get("class_id"),
		)
		ReportJobRepository.update(job_id, {"status": "done", "file_path": file_path})
	except Exception as exc:
		ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
		raise self.retry(exc=exc, countdown=60)
