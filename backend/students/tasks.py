from __future__ import annotations

from celery import shared_task

from .repository import ReportJobRepository


@shared_task(bind=True, max_retries=3)
def generate_students_export_task(self, job_id: str, export_format: str, params: dict | None = None) -> None:
    try:
        ReportJobRepository.update(job_id, {"status": "processing"})
        ReportJobRepository.update(
            job_id,
            {
                "status": "done",
                "file_path": f"/srv/sgep/media/exports/students/{job_id}.{export_format}",
            },
        )
    except Exception as exc:
        try:
            ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=60)