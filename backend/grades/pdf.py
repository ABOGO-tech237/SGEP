from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List

from weasyprint import HTML


def _appreciation_for(value: float) -> str:
    if value >= 16:
        return "Très bien"
    if value >= 14:
        return "Bien"
    if value >= 12:
        return "Assez bien"
    if value >= 10:
        return "Passable"
    return "Insuffisant"


def generate_report_card_pdf(student: dict, grades: List[dict], period: str, school: dict) -> str:
    """Generate a report card PDF and return the file path."""
    template_path = Path(__file__).resolve().parent / "templates" / "pdf" / "report_card.html"
    html_template = template_path.read_text(encoding="utf-8")

    # Build grades rows
    rows = []
    total_weighted = 0.0
    total_coeff = 0.0
    for g in grades:
        subject = g.get("subject_name") or g.get("subject_id")
        value = g.get("value") or 0.0
        coeff = g.get("coefficient") or 1.0
        try:
            v = float(value)
        except (TypeError, ValueError):
            v = 0.0
        try:
            c = float(coeff)
        except (TypeError, ValueError):
            c = 1.0

        weighted = v * c
        total_weighted += weighted
        total_coeff += c
        appreciation = _appreciation_for(v)
        rows.append(f"<tr><td>{subject}</td><td>{v:.2f}</td><td>{c:.2f}</td><td>{(weighted/c if c else 0):.2f}</td><td>{appreciation}</td></tr>")

    average = (total_weighted / total_coeff) if total_coeff else 0.0
    general_app = _appreciation_for(average)

    html = html_template.format(
        school_name=school.get("name", ""),
        school_address=school.get("address", ""),
        student_name=f"{student.get('last_name','')} {student.get('first_name','')}",
        matricule=student.get("matricule", ""),
        class_name=student.get("class_name", student.get("class_id", "")),
        period=period,
        grades_rows="\n".join(rows),
        average=f"{average:.2f}",
        rank=student.get("rank", ""),
        general_appreciation=general_app,
    )

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        HTML(string=html).write_pdf(tmp.name)
        return tmp.name
