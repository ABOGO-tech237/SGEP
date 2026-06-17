from __future__ import annotations

from celery import shared_task

from reports import excel as excel_export
from reports.repository import ReportJobRepository


@shared_task(bind=True, max_retries=3)
def generate_students_export_task(self, job_id: str, export_format: str, params: dict | None = None) -> None:
	try:
		ReportJobRepository.update(job_id, {"status": "processing"})
		params = params or {}
		if export_format == "excel":
			file_path = excel_export.export_students(
				params.get("academic_year_id", ""),
				params.get("class_id"),
			)
		else:
			file_path = f"/srv/sgep/media/exports/students/{job_id}.{export_format}"
		ReportJobRepository.update(job_id, {"status": "done", "file_path": file_path})
	except Exception as exc:
		try:
			ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
		except Exception:
			pass
		raise self.retry(exc=exc, countdown=60)
