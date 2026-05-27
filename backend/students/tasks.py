from __future__ import annotations

import json
import tempfile

import pandas as pd
from celery import shared_task
from weasyprint import HTML

from students.repository import ReportJobRepository, StudentRepository


def _load_params(raw_params: str | dict | None) -> dict:
    if raw_params is None:
        return {}
    if isinstance(raw_params, dict):
        return raw_params
    try:
        return json.loads(raw_params)
    except json.JSONDecodeError:
        return {}


def _fetch_students(params: dict) -> list[dict]:
    is_active = params.get("is_active")
    if isinstance(is_active, str):
        lowered = is_active.lower()
        if lowered in ("true", "1", "yes"):
            is_active = True
        elif lowered in ("false", "0", "no"):
            is_active = False
        else:
            is_active = None

    students: list[dict] = []
    offset = 0
    limit = 100

    while True:
        response = StudentRepository.list(
            class_id=params.get("class_id"),
            academic_year_id=params.get("academic_year_id"),
            is_active=is_active,
            search=params.get("search"),
            limit=limit,
            offset=offset,
        )
        batch = response.get("documents", [])
        students.extend(batch)

        total = int(response.get("total", len(students)))
        offset += limit
        if not batch or offset >= total:
            break

    return students


def _html_table(students: list[dict], title: str) -> str:
    rows = "".join(
        f"<tr><td>{student.get('matricule', '')}</td><td>{student.get('last_name', '')}</td><td>{student.get('first_name', '')}</td><td>{student.get('class_id', '') or ''}</td><td>{student.get('academic_year_id', '') or ''}</td></tr>"
        for student in students
    )
    return f"""
    <html>
        <head>
            <meta charset="utf-8" />
            <style>
                body {{ font-family: sans-serif; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; }}
                th {{ background: #f4f4f4; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <table>
                <thead>
                    <tr><th>Matricule</th><th>Nom</th><th>Prénom</th><th>Classe</th><th>Année scolaire</th></tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </body>
    </html>
    """


@shared_task(bind=True, max_retries=3)
def generate_students_pdf_export_task(self, job_id: str, params: dict | str | None) -> str:
    try:
        ReportJobRepository.update(job_id, {"status": "processing"})
        students = _fetch_students(_load_params(params))
        html = _html_table(students, "Export élèves PDF")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            HTML(string=html).write_pdf(tmp.name)
            file_path = tmp.name
        ReportJobRepository.update(job_id, {"status": "done", "file_path": file_path})
        return file_path
    except Exception as exc:
        ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_students_excel_export_task(self, job_id: str, params: dict | str | None) -> str:
    try:
        ReportJobRepository.update(job_id, {"status": "processing"})
        students = _fetch_students(_load_params(params))
        frame = pd.DataFrame(
            students,
            columns=["matricule", "last_name", "first_name", "birth_date", "class_id", "academic_year_id"],
        )
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            frame.to_excel(tmp.name, index=False, engine="openpyxl")
            file_path = tmp.name
        ReportJobRepository.update(job_id, {"status": "done", "file_path": file_path})
        return file_path
    except Exception as exc:
        ReportJobRepository.update(job_id, {"status": "failed", "error": str(exc)})
        raise self.retry(exc=exc, countdown=60)