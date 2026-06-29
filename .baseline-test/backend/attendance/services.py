from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from core.exceptions import NotFoundError
from notifications.tasks import notify_parent_absence_task
from students.repository import ReportJobRepository

from .repository import TYPE_TO_STATUS, AttendanceRepository, STATUS_ABSENT_JUSTIFIE


class AttendanceService:
	@staticmethod
	def _now() -> str:
		return datetime.now(timezone.utc).isoformat()

	@staticmethod
	def _count_working_days(date_from: str, date_to: str) -> int:
		start = datetime.fromisoformat(date_from.replace("Z", "+00:00")).date()
		end = datetime.fromisoformat(date_to.replace("Z", "+00:00")).date()
		count = 0
		current = start
		while current <= end:
			if current.weekday() < 5:
				count += 1
			current += timedelta(days=1)
		return max(count, 1)

	@staticmethod
	def list(
		class_id: str | None = None,
		student_id: str | None = None,
		date_from: str | None = None,
		date_to: str | None = None,
	) -> list[dict]:
		return AttendanceRepository.list(
			class_id=class_id,
			student_id=student_id,
			date_from=date_from,
			date_to=date_to,
		)

	@staticmethod
	def get(record_id: str) -> dict:
		record = AttendanceRepository.get(record_id)
		if not record:
			raise NotFoundError(f"Enregistrement {record_id} introuvable.")
		return record

	@staticmethod
	def record_absence(
		student_id: str,
		class_id: str,
		date_value: str,
		absence_type: str,
		motif: str,
		recorded_by: str,
		academic_year_id: str,
	) -> dict:
		status = TYPE_TO_STATUS.get(absence_type, absence_type.upper())
		payload = {
			"student_id": student_id,
			"class_id": class_id,
			"date": date_value,
			"status": status,
			"reason": motif,
			"academic_year_id": academic_year_id,
			"recorded_by": recorded_by,
			"is_deleted": False,
			"created_at": AttendanceService._now(),
			"updated_at": AttendanceService._now(),
		}
		record = AttendanceRepository.create(payload)
		notify_parent_absence_task.delay(student_id, date_value, absence_type)
		return record

	@staticmethod
	def update(record_id: str, validated_data: dict) -> dict:
		AttendanceService.get(record_id)
		payload = {"updated_at": AttendanceService._now()}

		if "type" in validated_data:
			payload["status"] = TYPE_TO_STATUS.get(validated_data["type"], validated_data["type"].upper())
		if "motif" in validated_data:
			payload["reason"] = validated_data["motif"]
		if "date" in validated_data:
			payload["date"] = validated_data["date"]
		if "class_id" in validated_data:
			payload["class_id"] = validated_data["class_id"]
		if "student_id" in validated_data:
			payload["student_id"] = validated_data["student_id"]
		if "academic_year_id" in validated_data:
			payload["academic_year_id"] = validated_data["academic_year_id"]

		return AttendanceRepository.update(record_id, payload)

	@staticmethod
	def justify(record_id: str, motif: str) -> dict:
		AttendanceService.get(record_id)
		return AttendanceRepository.update(
			record_id,
			{
				"status": STATUS_ABSENT_JUSTIFIE,
				"reason": motif,
				"updated_at": AttendanceService._now(),
			},
		)

	@staticmethod
	def get_stats(class_id: str, date_from: str, date_to: str) -> list[dict]:
		raw_stats = AttendanceRepository.get_stats(class_id, date_from, date_to)
		working_days = AttendanceService._count_working_days(date_from, date_to)

		for entry in raw_stats:
			absences = entry.get("absences", 0)
			entry["rate"] = round((absences / working_days) * 100, 2)

		return raw_stats

	@staticmethod
	def create_export_job(export_format: str, requested_by: str, params: dict | None = None) -> dict:
		return ReportJobRepository.create(
			{
				"type": f"attendance_{export_format}",
				"status": "pending",
				"requested_by": requested_by,
				"file_path": "",
				"error": "",
				"params": json.dumps(params or {}, ensure_ascii=True),
				"is_deleted": False,
				"created_at": AttendanceService._now(),
				"updated_at": AttendanceService._now(),
			}
		)
