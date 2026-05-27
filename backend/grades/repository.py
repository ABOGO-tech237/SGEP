from __future__ import annotations

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID
GRADES_COLLECTION_ID = "grades"
REPORT_CARDS_COLLECTION_ID = "report_cards"


class GradeRepository:
    @staticmethod
    def _normalize(document: dict) -> dict:
        normalized = dict(document)
        normalized["id"] = document.get("$id", document.get("id"))
        return normalized

    @staticmethod
    def list(class_id: str | None = None, subject_id: str | None = None, period_id: str | None = None, student_id: str | None = None, limit: int = 100, offset: int = 0) -> dict:
        queries: list[object] = [Query.equal("is_deleted", [False]), Query.limit(limit), Query.offset(offset)]
        if subject_id:
            queries.append(Query.equal("subject_id", [subject_id]))
        if period_id:
            # grades store the period in the `sequence` attribute
            queries.append(Query.equal("sequence", [period_id]))
        if student_id:
            queries.append(Query.equal("student_id", [student_id]))

        # Note: filtering by class_id is not directly supported on grades collection
        # because class membership lives on the student record. Callers that need
        # class-level filtering should post-filter or provide student_id list.
        try:
            response = databases.list_documents(DB_ID, GRADES_COLLECTION_ID, queries)
        except AppwriteException:
            raise

        response["documents"] = [GradeRepository._normalize(d) for d in response.get("documents", [])]
        return response

    @staticmethod
    def bulk_create(grades: list[dict]) -> list[dict]:
        created: list[dict] = []
        try:
            for g in grades:
                # Ensure created_at/updated_at handled by caller if needed
                document = databases.create_document(DB_ID, GRADES_COLLECTION_ID, "unique()", g)
                created.append(GradeRepository._normalize(document))
        except AppwriteException:
            raise
        return created

    @staticmethod
    def update(grade_id: str, data: dict) -> dict:
        try:
            document = databases.update_document(DB_ID, GRADES_COLLECTION_ID, grade_id, data)
            return GradeRepository._normalize(document)
        except AppwriteException:
            raise


class ReportCardRepository:
    @staticmethod
    def _normalize(document: dict) -> dict:
        normalized = dict(document)
        normalized["id"] = document.get("$id", document.get("id"))
        return normalized

    @staticmethod
    def create(data: dict) -> dict:
        try:
            document = databases.create_document(DB_ID, REPORT_CARDS_COLLECTION_ID, "unique()", data)
            return ReportCardRepository._normalize(document)
        except AppwriteException:
            raise

    @staticmethod
    def update(card_id: str, data: dict) -> dict:
        try:
            document = databases.update_document(DB_ID, REPORT_CARDS_COLLECTION_ID, card_id, data)
            return ReportCardRepository._normalize(document)
        except AppwriteException:
            raise

    @staticmethod
    def get(card_id: str) -> dict | None:
        try:
            document = databases.get_document(DB_ID, REPORT_CARDS_COLLECTION_ID, card_id)
            return ReportCardRepository._normalize(document)
        except AppwriteException as exc:
            if getattr(exc, "code", None) == 404:
                return None
            raise
