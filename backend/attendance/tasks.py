from __future__ import annotations

import tempfile

import pandas as pd
from celery import shared_task
from weasyprint import HTML

from attendance.repository import AttendanceRepository
from students.repository import ReportJobRepository


@shared_task(bind=True, max_retries=3)
def notify_parent_absence_task(self, student_id: str, date: str, absence_type: str):
    # Placeholder task to keep workflow async and testable.
    return f"notification queued for {student_id} ({absence_type}) on {date}"


@shared_task(bind=True, max_retries=3)
def export_attendance_pdf_task(self, job_id: str, class_id: str, date_from: str, date_to: str) -> str:
    try:
        ReportJobRepository.update(job_id, {"status": "processing"})
        response = AttendanceRepository.list(class_id=class_id, date_from=date_from, date_to=date_to)
        rows = "".join(
            f"<tr><td>{r.get('student_id','')}</td><td>{r.get('date','')}</td><td>{r.get('type','')}</td><td>{r.get('motif','')}</td><td>{'Oui' if r.get('is_justified') else 'Non'}</td></tr>"
            for r in response.get("documents", [])
        )
        html = f"""
        <html><head><meta charset='utf-8'/></head>
        <body>
            <h2>Export présence</h2>
            <p>Classe: {class_id} | Du {date_from} au {date_to}</p>
            <table border='1' cellspacing='0' cellpadding='4'>
                <thead><tr><th>Élève</th><th>Date</th><th>Type</th><th>Motif</th><th>Justifiée</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </body></html>
        """
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            HTML(string=html).write_pdf(tmp.name)
            file_path = tmp.name
        ReportJobRepository.update(job_id, {"status": "done", "file_path": file_path})
        return file_path
    except Exception as exc:
        ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def export_attendance_excel_task(self, job_id: str, class_id: str, date_from: str, date_to: str) -> str:
    try:
        ReportJobRepository.update(job_id, {"status": "processing"})
        response = AttendanceRepository.list(class_id=class_id, date_from=date_from, date_to=date_to)
        data = response.get("documents", [])
        frame = pd.DataFrame(data, columns=["student_id", "date", "type", "motif", "is_justified"])
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            frame.to_excel(tmp.name, index=False, engine="openpyxl")
            file_path = tmp.name
        ReportJobRepository.update(job_id, {"status": "done", "file_path": file_path})
        return file_path
    except Exception as exc:
        ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
        raise self.retry(exc=exc, countdown=60)
