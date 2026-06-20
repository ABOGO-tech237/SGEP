from __future__ import annotations

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases
from core.appwrite_utils import documents_of, to_dict

DB_ID = settings.APPWRITE_DB_ID
GRADES_COLLECTION_ID = "grades"
REPORT_CARDS_COLLECTION_ID = "report_cards"
SUBJECTS_COLLECTION_ID = "subjects"


def _normalize_document(document: dict) -> dict:
	document = to_dict(document)
	normalized = dict(document)
	normalized["id"] = document.get("$id", document.get("id"))
	return normalized


class GradeRepository:
	@staticmethod
	def list(
		class_id: str | None = None,
		subject_id: str | None = None,
		period_id: str | None = None,
		student_id: str | None = None,
		student_ids: list[str] | None = None,
	) -> list[dict]:
		queries: list = [Query.equal("is_deleted", [False]), Query.limit(500)]

		if student_id:
			queries.append(Query.equal("student_id", [student_id]))
		if subject_id:
			queries.append(Query.equal("subject_id", [subject_id]))
		if period_id:
			queries.append(Query.equal("sequence", [period_id]))
		if student_ids:
			queries.append(Query.equal("student_id", student_ids))

		try:
			response = databases.list_documents(DB_ID, GRADES_COLLECTION_ID, queries)
			grades = [_normalize_document(document) for document in documents_of(response)]
			if class_id and not student_ids and not student_id:
				return grades
			return grades
		except AppwriteException:
			raise

	@staticmethod
	def get(grade_id: str) -> dict | None:
		try:
			document = databases.get_document(DB_ID, GRADES_COLLECTION_ID, grade_id)
			return _normalize_document(document)
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def create(data: dict) -> dict:
		try:
			document = databases.create_document(DB_ID, GRADES_COLLECTION_ID, "unique()", data)
			return _normalize_document(document)
		except AppwriteException:
			raise

	@staticmethod
	def bulk_create(grades: list[dict]) -> list[dict]:
		created: list[dict] = []
		for grade_data in grades:
			created.append(GradeRepository.create(grade_data))
		return created

	@staticmethod
	def update(grade_id: str, data: dict) -> dict:
		try:
			document = databases.update_document(DB_ID, GRADES_COLLECTION_ID, grade_id, data)
			return _normalize_document(document)
		except AppwriteException:
			raise


class SubjectRepository:
	@staticmethod
	def get(subject_id: str) -> dict | None:
		try:
			document = databases.get_document(DB_ID, SUBJECTS_COLLECTION_ID, subject_id)
			return _normalize_document(document)
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def list_by_class(class_id: str) -> list[dict]:
		try:
			response = databases.list_documents(
				DB_ID,
				SUBJECTS_COLLECTION_ID,
				[
					Query.equal("class_id", [class_id]),
					Query.equal("is_deleted", [False]),
					Query.equal("is_active", [True]),
					Query.limit(100),
				],
			)
			return [_normalize_document(document) for document in documents_of(response)]
		except AppwriteException:
			raise


class ReportCardRepository:
	@staticmethod
	def list(student_id: str | None = None, period_id: str | None = None) -> list[dict]:
		queries: list = [Query.equal("is_deleted", [False]), Query.order_desc("created_at")]
		if student_id:
			queries.append(Query.equal("student_id", [student_id]))
		if period_id:
			queries.append(Query.equal("sequence", [period_id]))
		try:
			response = databases.list_documents(DB_ID, REPORT_CARDS_COLLECTION_ID, queries)
			return [_normalize_document(document) for document in documents_of(response)]
		except AppwriteException:
			raise

	@staticmethod
	def get(report_card_id: str) -> dict | None:
		try:
			document = databases.get_document(DB_ID, REPORT_CARDS_COLLECTION_ID, report_card_id)
			return _normalize_document(document)
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def create(data: dict) -> dict:
		try:
			document = databases.create_document(DB_ID, REPORT_CARDS_COLLECTION_ID, "unique()", data)
			return _normalize_document(document)
		except AppwriteException:
			raise

	@staticmethod
	def update(report_card_id: str, data: dict) -> dict:
		try:
			document = databases.update_document(DB_ID, REPORT_CARDS_COLLECTION_ID, report_card_id, data)
			return _normalize_document(document)
		except AppwriteException:
			raise
