from __future__ import annotations

from datetime import datetime, timezone

from celery import shared_task

from grades.pdf import generate_report_card_pdf
from grades.repository import ReportCardRepository
from grades.services import GradeService, ReportCardService
from students.repository import ReportJobRepository, StudentRepository


@shared_task(bind=True, max_retries=3)
def generate_class_report_cards_task(self, class_id: str, period_id: str, job_id: str, academic_year_id: str = "") -> None:
	try:
		ReportJobRepository.update(job_id, {"status": "processing"})
		averages = GradeService.calculate_averages(class_id, period_id)
		students_response = StudentRepository.list(class_id=class_id, is_active=True, page_size=500)
		students = students_response.get("documents", [])
		generated_paths: list[str] = []

		for student in students:
			student_id = student["id"]
			grades = GradeService.grades_for_student(student_id, period_id)
			student_with_rank = dict(student)
			student_with_rank["rank"] = averages.get(student_id, {}).get("rank", "-")
			file_path = generate_report_card_pdf(student_with_rank, grades, period_id)
			ReportCardRepository.create(
				{
					"student_id": student_id,
					"academic_year_id": academic_year_id or student.get("academic_year_id", ""),
					"sequence": period_id,
					"file_path": file_path,
					"status": "draft",
					"generated_at": datetime.now(timezone.utc).isoformat(),
					"is_deleted": False,
					"created_at": datetime.now(timezone.utc).isoformat(),
					"updated_at": datetime.now(timezone.utc).isoformat(),
				}
			)
			generated_paths.append(file_path)

		ReportJobRepository.update(
			job_id,
			{
				"status": "done",
				"file_path": generated_paths[0] if generated_paths else "",
			},
		)
	except Exception as exc:
		try:
			ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
		except Exception:
			pass
		raise self.retry(exc=exc, countdown=60)
