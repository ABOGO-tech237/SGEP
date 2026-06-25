from __future__ import annotations

import os
from pathlib import Path

from django.template.loader import render_to_string

BULLETINS_DIR = Path("/srv/sgep/media/bulletins")


def _appreciation(value: float) -> str:
	if value >= 16:
		return "Excellent"
	if value >= 14:
		return "Très bien"
	if value >= 12:
		return "Bien"
	if value >= 10:
		return "Assez bien"
	if value >= 8:
		return "Passable"
	return "Insuffisant"


def generate_report_card_pdf(student: dict, grades: list[dict], period: str, school: dict | None = None) -> str:
	BULLETINS_DIR.mkdir(parents=True, exist_ok=True)

	subjects_data = []
	total_weighted = 0.0
	total_coef = 0.0
	for grade in grades:
		value = float(grade.get("value", 0))
		coef = float(grade.get("coefficient", 1))
		subjects_data.append(
			{
				"subject_id": grade.get("subject_id", ""),
				"value": value,
				"coefficient": coef,
				"weighted": round(value * coef / coef, 2) if coef else value,
				"appreciation": _appreciation(value),
			}
		)
		total_weighted += value * coef
		total_coef += coef

	general_average = round(total_weighted / total_coef, 2) if total_coef else 0.0
	context = {
		"school": school or {"name": "École Primaire SGEP"},
		"student": student,
		"grades": subjects_data,
		"period": period,
		"general_average": general_average,
		"general_appreciation": _appreciation(general_average),
		"rank": student.get("rank", "-"),
	}

	html_content = render_to_string("pdf/report_card.html", context)

	try:
		from weasyprint import HTML
	except ImportError:  # pragma: no cover
		file_path = BULLETINS_DIR / f"report_{student.get('id', 'unknown')}_{period}.html"
		file_path.write_text(html_content, encoding="utf-8")
		return str(file_path)

	file_name = f"report_{student.get('id', 'unknown')}_{period}.pdf"
	file_path = BULLETINS_DIR / file_name
	HTML(string=html_content).write_pdf(str(file_path))
	return str(file_path)
