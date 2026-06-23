from __future__ import annotations

from datetime import datetime, timedelta, timezone

from classes.repository import ClassRepository
from core.repository import AcademicYearRepository
from finance.services import InvoiceService
from students.repository import StudentRepository

RECENT_ACTIVITY_LIMIT = 5
RECENT_ACTIVITY_WINDOW_DAYS = 7


def _parse_timestamp(value: str | None) -> float | None:
	if not value:
		return None
	try:
		parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
		if parsed.tzinfo is None:
			parsed = parsed.replace(tzinfo=timezone.utc)
		return parsed.timestamp()
	except ValueError:
		return None


def _format_count(value: int) -> str:
	return f"{value:,}"


def _format_percent(value: float) -> str:
	return f"{value:.1f}%"


def _format_relative_time(target: str | None, now: datetime) -> str:
	target_timestamp = _parse_timestamp(target)
	if target_timestamp is None:
		return "à l'instant"

	delta_minutes = round((now.timestamp() - target_timestamp) / 60)
	if delta_minutes <= 0:
		return "à l'instant"
	if delta_minutes < 60:
		return f"il y a {delta_minutes} min"
	delta_hours = round(delta_minutes / 60)
	if delta_hours < 24:
		return f"il y a {delta_hours} h"
	delta_days = round(delta_hours / 24)
	if delta_days == 1:
		return "hier"
	return f"il y a {delta_days} j"


def _is_within_days(target: str | None, now: datetime, days: int) -> bool:
	target_timestamp = _parse_timestamp(target)
	if target_timestamp is None:
		return False
	return now.timestamp() - target_timestamp <= days * 24 * 60 * 60


def _build_activity(student: dict, now: datetime) -> dict:
	created_at = _parse_timestamp(student.get("created_at"))
	updated_at = _parse_timestamp(student.get("updated_at"))
	deleted_at = _parse_timestamp(student.get("deleted_at"))

	action = "Dossier actif"
	status = "ACTIVE"
	time_source = student.get("updated_at") or student.get("created_at")

	if student.get("is_deleted") or deleted_at is not None:
		action = "Archivé"
		status = "SUSPENDED"
		time_source = student.get("deleted_at") or student.get("updated_at") or student.get("created_at")
	elif student.get("is_active") is False:
		action = "Suspendu"
		status = "SUSPENDED"
	elif not student.get("class_id"):
		action = "En attente d'affectation"
		status = "PENDING"
		time_source = student.get("created_at")
	elif _is_within_days(student.get("created_at"), now, RECENT_ACTIVITY_WINDOW_DAYS):
		action = "Inscrit"
		status = "PENDING"
		time_source = student.get("created_at")
	elif created_at is not None and updated_at is not None and updated_at > created_at:
		action = "Profil mis à jour"
		time_source = student.get("updated_at")

	return {
		"id": student.get("id", ""),
		"name": f"{student.get('first_name', '')} {student.get('last_name', '')}".strip(),
		"action": action,
		"grade": (student.get("class_id") or "").strip() or "Non affecté",
		"status": status,
		"time": _format_relative_time(time_source, now),
	}


class AdminDashboardService:
	@staticmethod
	def _fetch_students_sample(page_size: int = 100) -> tuple[list[dict], int]:
		response = StudentRepository.list(page=1, page_size=page_size)
		students = response.get("documents", [])
		total = int(response.get("total", len(students)))
		return students, total

	@staticmethod
	def build(now: datetime | None = None) -> dict:
		now = now or datetime.now(timezone.utc)
		students, total_students = AdminDashboardService._fetch_students_sample()

		active_students = sum(
			1 for student in students if student.get("is_active") is not False and not student.get("is_deleted")
		)
		inactive_students = max(total_students - active_students, 0)
		unique_classes = {
			(student.get("class_id") or "").strip()
			for student in students
			if (student.get("class_id") or "").strip()
		}
		recent_registrations = sum(
			1 for student in students if _is_within_days(student.get("created_at"), now, RECENT_ACTIVITY_WINDOW_DAYS)
		)

		classes = ClassRepository.list()
		finance = InvoiceService.dashboard()
		active_year = AcademicYearRepository.get_active()

		stats = [
			{
				"label": "Total élèves",
				"value": _format_count(total_students),
				"change": "Données Appwrite en direct",
				"positive": None,
			},
			{
				"label": "Élèves actifs",
				"value": _format_count(active_students),
				"change": (
					f"{_format_percent((active_students / total_students) * 100)} actifs"
					if total_students
					else "Aucun dossier actif"
				),
				"positive": active_students <= total_students,
			},
			{
				"label": "Élèves inactifs",
				"value": _format_count(inactive_students),
				"change": (
					"Aucun dossier suspendu"
					if inactive_students == 0
					else f"{_format_count(inactive_students)} dossiers à suivre"
				),
				"positive": inactive_students == 0,
			},
			{
				"label": "Classes",
				"value": _format_count(len(classes) or len(unique_classes)),
				"change": f"{_format_count(recent_registrations)} inscriptions récentes",
				"positive": None,
			},
			{
				"label": "Recouvrement",
				"value": _format_percent(float(finance.get("recovery_rate", 0))),
				"change": f"{_format_count(int(finance.get('overdue_count', 0)))} factures en retard",
				"positive": float(finance.get("recovery_rate", 0)) >= 50,
			},
			{
				"label": "Encaissements",
				"value": _format_count(int(float(finance.get("total_collected", 0)))),
				"change": f"Facturé : {_format_count(int(float(finance.get('total_billed', 0))))}",
				"positive": float(finance.get("total_collected", 0)) > 0,
			},
		]

		recent_activity = [
			_build_activity(student, now) for student in students[:RECENT_ACTIVITY_LIMIT]
		]

		return {
			"generated_at": now.isoformat(),
			"academic_year": (
				{"id": active_year["id"], "name": active_year.get("name", "")} if active_year else None
			),
			"stats": stats,
			"finance": finance,
			"recent_activity": recent_activity,
		}
