from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

EXPORTS_DIR = Path("/srv/sgep/media/exports")
HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF")


def _ensure_dir() -> Path:
	EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
	return EXPORTS_DIR


def _apply_excel_styles(writer: pd.ExcelWriter, sheet_name: str) -> None:
	worksheet = writer.sheets[sheet_name]
	for cell in worksheet[1]:
		cell.font = HEADER_FONT
		cell.fill = HEADER_FILL
		cell.alignment = Alignment(horizontal="center")
	for column_cells in worksheet.columns:
		max_length = max(len(str(cell.value or "")) for cell in column_cells)
		worksheet.column_dimensions[column_cells[0].column_letter].width = min(max_length + 2, 40)


def export_students(academic_year_id: str, class_id: str | None = None, students: list[dict] | None = None) -> str:
	from students.repository import StudentRepository

	if students is None:
		response = StudentRepository.list(academic_year_id=academic_year_id, class_id=class_id, page_size=500)
		students = response.get("documents", [])

	rows = []
	for student in sorted(students, key=lambda s: (s.get("class_id", ""), s.get("last_name", ""))):
		rows.append(
			{
				"Matricule": student.get("matricule", ""),
				"Nom": student.get("last_name", ""),
				"Prénom": student.get("first_name", ""),
				"Date naissance": student.get("birth_date", ""),
				"Classe": student.get("class_id", ""),
				"Niveau": student.get("level", ""),
				"Tuteur principal": student.get("guardian_name", ""),
				"Téléphone": student.get("guardian_phone", ""),
			}
		)

	df = pd.DataFrame(rows)
	file_path = _ensure_dir() / f"students_{academic_year_id}.xlsx"
	with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
		df.to_excel(writer, index=False, sheet_name="Élèves")
		_apply_excel_styles(writer, "Élèves")
	return str(file_path.resolve())


def export_results(class_id: str, period_id: str, averages: dict | None = None) -> str:
	from grades.services import GradeService
	from students.repository import StudentRepository

	if averages is None:
		averages = GradeService.calculate_averages(class_id, period_id)

	response = StudentRepository.list(class_id=class_id, page_size=500)
	students = {s["id"]: s for s in response.get("documents", [])}

	rows = []
	for student_id, data in averages.items():
		student = students.get(student_id, {})
		row = {
			"Matricule": student.get("matricule", ""),
			"Nom": student.get("last_name", ""),
			"Prénom": student.get("first_name", ""),
			"Moyenne générale": data.get("average", 0),
			"Rang": data.get("rank", 0),
		}
		for subject_id, avg in data.get("subject_averages", {}).items():
			row[subject_id] = avg
		rows.append(row)

	df = pd.DataFrame(rows)
	file_path = _ensure_dir() / f"results_{class_id}_{period_id}.xlsx"
	with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
		df.to_excel(writer, index=False, sheet_name="Résultats")
		_apply_excel_styles(writer, "Résultats")
	return str(file_path.resolve())


def export_finance(academic_year_id: str, invoices: list[dict] | None = None) -> str:
	from finance.repository import PaymentRepository

	if invoices is None:
		from finance.repository import InvoiceRepository

		invoices = InvoiceRepository.list()

	rows = []
	for invoice in invoices:
		if invoice.get("academic_year_id") != academic_year_id:
			continue
		paid = PaymentRepository.total_for_invoice(invoice["id"])
		rows.append(
			{
				"Élève": invoice.get("student_id", ""),
				"Type frais": invoice.get("fee_type_id", ""),
				"Montant facturé": invoice.get("amount", 0),
				"Montant payé": paid,
				"Solde": float(invoice.get("amount", 0)) - paid,
				"Statut": invoice.get("status", ""),
			}
		)

	df = pd.DataFrame(rows)
	file_path = _ensure_dir() / f"finance_{academic_year_id}.xlsx"
	with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
		df.to_excel(writer, index=False, sheet_name="Détail")
		_apply_excel_styles(writer, "Détail")
		if rows:
			summary = df.groupby("Type frais")[["Montant facturé", "Montant payé"]].sum().reset_index()
			summary.to_excel(writer, index=False, sheet_name="Récapitulatif")
			_apply_excel_styles(writer, "Récapitulatif")
	return str(file_path.resolve())


def export_attendance(class_id: str, date_from: str, date_to: str, stats: list[dict] | None = None) -> str:
	from attendance.services import AttendanceService
	from students.repository import StudentRepository

	if stats is None:
		stats = AttendanceService.get_stats(class_id, date_from, date_to)

	response = StudentRepository.list(class_id=class_id, page_size=500)
	students = {s["id"]: s for s in response.get("documents", [])}

	rows = []
	for entry in stats:
		student = students.get(entry["student_id"], {})
		rows.append(
			{
				"Nom élève": f"{student.get('last_name', '')} {student.get('first_name', '')}".strip(),
				"Nb absences": entry.get("absences", 0),
				"Nb retards": entry.get("retards", 0),
				"Nb absences justifiées": entry.get("justified", 0),
				"Taux absentéisme %": entry.get("rate", 0),
			}
		)

	df = pd.DataFrame(rows)
	file_path = _ensure_dir() / f"attendance_{class_id}.xlsx"
	with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
		df.to_excel(writer, index=False, sheet_name="Absences")
		_apply_excel_styles(writer, "Absences")
	return str(file_path.resolve())
