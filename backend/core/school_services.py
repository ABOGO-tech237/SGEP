from __future__ import annotations

from datetime import datetime, timezone

from core.exceptions import NotFoundError
from core.repository import AcademicYearRepository, SchoolRepository


class SchoolService:
	@staticmethod
	def _now() -> str:
		return datetime.now(timezone.utc).isoformat()

	@staticmethod
	def list() -> list[dict]:
		return SchoolRepository.list()

	@staticmethod
	def get(school_id: str) -> dict:
		school = SchoolRepository.get(school_id)
		if not school:
			raise NotFoundError(f"École {school_id} introuvable.")
		return school

	@staticmethod
	def create(validated_data: dict) -> dict:
		payload = {
			**validated_data,
			"is_active": validated_data.get("is_active", True),
			"is_deleted": False,
			"created_at": SchoolService._now(),
			"updated_at": SchoolService._now(),
		}
		return SchoolRepository.create(payload)

	@staticmethod
	def update(school_id: str, validated_data: dict) -> dict:
		SchoolService.get(school_id)
		payload = {**validated_data, "updated_at": SchoolService._now()}
		return SchoolRepository.update(school_id, payload)


class AcademicYearService:
	@staticmethod
	def _now() -> str:
		return datetime.now(timezone.utc).isoformat()

	@staticmethod
	def list(school_id: str | None = None) -> list[dict]:
		return AcademicYearRepository.list(school_id=school_id)

	@staticmethod
	def get(year_id: str) -> dict:
		year = AcademicYearRepository.get(year_id)
		if not year:
			raise NotFoundError(f"Année scolaire {year_id} introuvable.")
		return year

	@staticmethod
	def create(validated_data: dict) -> dict:
		payload = {
			**validated_data,
			"is_active": validated_data.get("is_active", False),
			"is_deleted": False,
			"created_at": AcademicYearService._now(),
			"updated_at": AcademicYearService._now(),
		}
		return AcademicYearRepository.create(payload)

	@staticmethod
	def update(year_id: str, validated_data: dict) -> dict:
		AcademicYearService.get(year_id)
		payload = {**validated_data, "updated_at": AcademicYearService._now()}
		return AcademicYearRepository.update(year_id, payload)

	@staticmethod
	def get_active() -> dict | None:
		return AcademicYearRepository.get_active()
