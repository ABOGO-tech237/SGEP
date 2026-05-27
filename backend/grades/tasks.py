from __future__ import annotations

from celery import shared_task
from django.conf import settings

from students.repository import StudentRepository, ReportJobRepository
from grades.repository import GradeRepository, ReportCardRepository
from grades.services import GradeService
from grades.pdf import generate_report_card_pdf
from config.appwrite_client import databases


@shared_task(bind=True, max_retries=3)
def generate_class_report_cards_task(self, class_id: str, period_id: str, job_id: str) -> str:
    try:
        ReportJobRepository.update(job_id, {"status": "processing"})

        students = StudentRepository.list(class_id=class_id).get("documents", [])

        # compute averages/ranks once for the class
        averages = GradeService.calculate_averages(class_id=class_id, period_id=period_id)

        total = len(students)
        done = 0
        for student in students:
            student_id = student.get("id")
            # fetch grades for student and period
            grades_resp = GradeRepository.list(student_id=student_id, period_id=period_id)
            grades = grades_resp.get("documents", [])

            # enrich with subject name if possible
            for g in grades:
                subj_id = g.get("subject_id")
                try:
                    subj = databases.get_document(settings.APPWRITE_DB_ID, "subjects", subj_id)
                    g["subject_name"] = subj.get("name")
                except Exception:
                    g["subject_name"] = subj_id

            # attach computed average/rank if available
            info = averages.get(student_id, {})
            student["average"] = info.get("average")
            student["rank"] = info.get("rank")

            # school info from settings
            school = {"name": getattr(settings, "SCHOOL_NAME", ""), "address": getattr(settings, "SCHOOL_ADDRESS", "")}

            file_path = generate_report_card_pdf(student, grades, period_id, school)

            # create report_card document
            ReportCardRepository.create({
                "student_id": student_id,
                "class_id": class_id,
                "period_id": period_id,
                "file_path": file_path,
                "parent_user_id": student.get("parent_user_id"),
                "created_by": "system",
            })

            done += 1
            ReportJobRepository.update(job_id, {"status": "processing", "progress": int(done * 100 / total)})

        ReportJobRepository.update(job_id, {"status": "done", "progress": 100})
        return "done"
    except Exception as exc:
        ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
        raise self.retry(exc=exc, countdown=60)
