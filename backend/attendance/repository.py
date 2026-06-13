from __future__ import annotations

from datetime import datetime, timezone

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID
COLLECTION_ID = "attendance"

STATUS_ABSENT = "ABSENT"
STATUS_RETARD = "RETARD"
STATUS_ABSENT_JUSTIFIE = "ABSENT_JUSTIFIE"

TYPE_TO_STATUS = {
	"absence": STATUS_ABSENT,
	"retard": STATUS_RETARD,
}


def _normalize_document(document: dict) -> dict:
	normalized = dict(document)
	normalized["id"] = document.get("$id", document.get("id"))
	return normalized


class AttendanceRepository:
	@staticmethod
	def list(
		class_id: str | None = None,
		student_id: str | None = None,
		date_from: str | None = None,
		date_to: str | None = None,
	) -> list[dict]:
		queries: list = [Query.equal("is_deleted", [False]), Query.order_desc("date")]

		if class_id:
			queries.append(Query.equal("class_id", [class_id]))
		if student_id:
			queries.append(Query.equal("student_id", [student_id]))
		if date_from:
			queries.append(Query.greater_than_equal("date", date_from))
		if date_to:
			queries.append(Query.less_than_equal("date", date_to))

		try:
			response = databases.list_documents(DB_ID, COLLECTION_ID, queries)
			return [_normalize_document(document) for document in response.get("documents", [])]
		except AppwriteException:
			raise

	@staticmethod
	def get(record_id: str) -> dict | None:
		try:
			document = databases.get_document(DB_ID, COLLECTION_ID, record_id)
			return _normalize_document(document)
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def create(data: dict) -> dict:
		try:
			document = databases.create_document(DB_ID, COLLECTION_ID, "unique()", data)
			return _normalize_document(document)
		except AppwriteException:
			raise

	@staticmethod
	def update(record_id: str, data: dict) -> dict:
		try:
			document = databases.update_document(DB_ID, COLLECTION_ID, record_id, data)
			return _normalize_document(document)
		except AppwriteException:
			raise

	@staticmethod
	def get_stats(class_id: str, date_from: str, date_to: str) -> list[dict]:
		records = AttendanceRepository.list(class_id=class_id, date_from=date_from, date_to=date_to)
		stats: dict[str, dict] = {}

		for record in records:
			student_id = record.get("student_id", "")
			if student_id not in stats:
				stats[student_id] = {
					"student_id": student_id,
					"absences": 0,
					"retards": 0,
					"justified": 0,
				}

			status = record.get("status", "")
			if status == STATUS_ABSENT:
				stats[student_id]["absences"] += 1
			elif status == STATUS_RETARD:
				stats[student_id]["retards"] += 1
			elif status == STATUS_ABSENT_JUSTIFIE:
				stats[student_id]["justified"] += 1

		return list(stats.values())
