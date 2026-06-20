from __future__ import annotations

from datetime import datetime, timezone

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases
from core.appwrite_utils import documents_of, to_dict

DB_ID = settings.APPWRITE_DB_ID


def _normalize(document: dict) -> dict:
	document = to_dict(document)
	result = dict(document)
	result["id"] = document.get("$id", document.get("id"))
	return result


def _now() -> str:
	return datetime.now(timezone.utc).isoformat()


class ClassRepository:
	COLLECTION_ID = "classes"

	@staticmethod
	def list(academic_year_id: str | None = None, level_id: str | None = None) -> list[dict]:
		queries: list = [Query.equal("is_deleted", [False]), Query.equal("is_active", [True])]
		if academic_year_id:
			queries.append(Query.equal("academic_year_id", [academic_year_id]))
		if level_id:
			queries.append(Query.equal("level_id", [level_id]))
		try:
			response = databases.list_documents(DB_ID, ClassRepository.COLLECTION_ID, queries)
			return [_normalize(doc) for doc in documents_of(response)]
		except AppwriteException:
			raise

	@staticmethod
	def get(class_id: str) -> dict | None:
		try:
			return _normalize(databases.get_document(DB_ID, ClassRepository.COLLECTION_ID, class_id))
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def create(data: dict) -> dict:
		try:
			return _normalize(databases.create_document(DB_ID, ClassRepository.COLLECTION_ID, "unique()", data))
		except AppwriteException:
			raise

	@staticmethod
	def update(class_id: str, data: dict) -> dict:
		try:
			return _normalize(databases.update_document(DB_ID, ClassRepository.COLLECTION_ID, class_id, data))
		except AppwriteException:
			raise


class SubjectRepository:
	COLLECTION_ID = "subjects"

	@staticmethod
	def list(class_id: str | None = None) -> list[dict]:
		queries: list = [Query.equal("is_deleted", [False]), Query.equal("is_active", [True])]
		if class_id:
			queries.append(Query.equal("class_id", [class_id]))
		try:
			response = databases.list_documents(DB_ID, SubjectRepository.COLLECTION_ID, queries)
			return [_normalize(doc) for doc in documents_of(response)]
		except AppwriteException:
			raise

	@staticmethod
	def get(subject_id: str) -> dict | None:
		try:
			return _normalize(databases.get_document(DB_ID, SubjectRepository.COLLECTION_ID, subject_id))
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def create(data: dict) -> dict:
		try:
			return _normalize(databases.create_document(DB_ID, SubjectRepository.COLLECTION_ID, "unique()", data))
		except AppwriteException:
			raise

	@staticmethod
	def update(subject_id: str, data: dict) -> dict:
		try:
			return _normalize(databases.update_document(DB_ID, SubjectRepository.COLLECTION_ID, subject_id, data))
		except AppwriteException:
			raise
