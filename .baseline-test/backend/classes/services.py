from __future__ import annotations

from datetime import datetime, timezone

from core.exceptions import NotFoundError

from .repository import ClassRepository, SubjectRepository


class ClassService:
	@staticmethod
	def _now() -> str:
		return datetime.now(timezone.utc).isoformat()

	@staticmethod
	def list(academic_year_id: str | None = None, level_id: str | None = None) -> list[dict]:
		return ClassRepository.list(academic_year_id=academic_year_id, level_id=level_id)

	@staticmethod
	def get(class_id: str) -> dict:
		doc = ClassRepository.get(class_id)
		if not doc:
			raise NotFoundError(f"Classe {class_id} introuvable.")
		return doc

	@staticmethod
	def create(validated_data: dict) -> dict:
		payload = {
			**validated_data,
			"is_active": True,
			"is_deleted": False,
			"created_at": ClassService._now(),
			"updated_at": ClassService._now(),
		}
		return ClassRepository.create(payload)

	@staticmethod
	def update(class_id: str, validated_data: dict) -> dict:
		ClassService.get(class_id)
		return ClassRepository.update(class_id, {**validated_data, "updated_at": ClassService._now()})


class SubjectService:
	@staticmethod
	def _now() -> str:
		return datetime.now(timezone.utc).isoformat()

	@staticmethod
	def list(class_id: str | None = None) -> list[dict]:
		return SubjectRepository.list(class_id=class_id)

	@staticmethod
	def get(subject_id: str) -> dict:
		doc = SubjectRepository.get(subject_id)
		if not doc:
			raise NotFoundError(f"Matière {subject_id} introuvable.")
		return doc

	@staticmethod
	def create(validated_data: dict) -> dict:
		payload = {
			**validated_data,
			"defined_by_admin": True,
			"is_active": True,
			"is_deleted": False,
			"created_at": SubjectService._now(),
			"updated_at": SubjectService._now(),
		}
		return SubjectRepository.create(payload)

	@staticmethod
	def update(subject_id: str, validated_data: dict) -> dict:
		SubjectService.get(subject_id)
		return SubjectRepository.update(subject_id, {**validated_data, "updated_at": SubjectService._now()})
