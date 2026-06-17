from __future__ import annotations

from datetime import datetime, timezone

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID


def _normalize(document: dict) -> dict:
	result = dict(document)
	result["id"] = document.get("$id", document.get("id"))
	return result


def _now() -> str:
	return datetime.now(timezone.utc).isoformat()


class SchoolRepository:
	COLLECTION_ID = "schools"

	@staticmethod
	def list() -> list[dict]:
		try:
			response = databases.list_documents(
				DB_ID,
				SchoolRepository.COLLECTION_ID,
				[Query.equal("is_deleted", [False]), Query.order_desc("created_at")],
			)
			return [_normalize(doc) for doc in response.get("documents", [])]
		except AppwriteException:
			raise

	@staticmethod
	def get(school_id: str) -> dict | None:
		try:
			return _normalize(databases.get_document(DB_ID, SchoolRepository.COLLECTION_ID, school_id))
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def create(data: dict) -> dict:
		try:
			return _normalize(databases.create_document(DB_ID, SchoolRepository.COLLECTION_ID, "unique()", data))
		except AppwriteException:
			raise

	@staticmethod
	def update(school_id: str, data: dict) -> dict:
		try:
			return _normalize(databases.update_document(DB_ID, SchoolRepository.COLLECTION_ID, school_id, data))
		except AppwriteException:
			raise


class AcademicYearRepository:
	COLLECTION_ID = "academic_years"

	@staticmethod
	def list(school_id: str | None = None) -> list[dict]:
		queries: list = [Query.equal("is_deleted", [False]), Query.order_desc("start_date")]
		if school_id:
			queries.append(Query.equal("school_id", [school_id]))
		try:
			response = databases.list_documents(DB_ID, AcademicYearRepository.COLLECTION_ID, queries)
			return [_normalize(doc) for doc in response.get("documents", [])]
		except AppwriteException:
			raise

	@staticmethod
	def get(year_id: str) -> dict | None:
		try:
			return _normalize(databases.get_document(DB_ID, AcademicYearRepository.COLLECTION_ID, year_id))
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def create(data: dict) -> dict:
		try:
			return _normalize(databases.create_document(DB_ID, AcademicYearRepository.COLLECTION_ID, "unique()", data))
		except AppwriteException:
			raise

	@staticmethod
	def update(year_id: str, data: dict) -> dict:
		try:
			return _normalize(databases.update_document(DB_ID, AcademicYearRepository.COLLECTION_ID, year_id, data))
		except AppwriteException:
			raise

	@staticmethod
	def get_active() -> dict | None:
		try:
			response = databases.list_documents(
				DB_ID,
				AcademicYearRepository.COLLECTION_ID,
				[Query.equal("is_active", [True]), Query.equal("is_deleted", [False]), Query.limit(1)],
			)
			docs = response.get("documents", [])
			return _normalize(docs[0]) if docs else None
		except AppwriteException:
			raise
