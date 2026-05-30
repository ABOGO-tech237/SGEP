from __future__ import annotations

from datetime import datetime, timezone

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID
COLLECTION_ID = "students"
REPORT_JOBS_COLLECTION_ID = "report_jobs"


def _normalize_document(document: dict) -> dict:
    normalized = dict(document)
    normalized["id"] = document.get("$id", document.get("id"))
    return normalized


class StudentRepository:
    @staticmethod
    def list(
        class_id: str | None = None,
        academic_year_id: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        queries: list = [Query.order_desc("created_at")]

        if class_id:
            queries.append(Query.equal("class_id", [class_id]))
        if academic_year_id:
            queries.append(Query.equal("academic_year_id", [academic_year_id]))
        if is_active is not None:
            queries.append(Query.equal("is_active", [is_active]))
        if search:
            queries.append(Query.search("search_index", search.lower()))

        queries.append(Query.limit(page_size))
        queries.append(Query.offset(max(page - 1, 0) * page_size))

        try:
            response = databases.list_documents(DB_ID, COLLECTION_ID, queries)
            response["documents"] = [_normalize_document(document) for document in response.get("documents", [])]
            return response
        except AppwriteException:
            raise

    @staticmethod
    def get(student_id: str) -> dict | None:
        try:
            document = databases.get_document(DB_ID, COLLECTION_ID, student_id)
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
    def update(student_id: str, data: dict) -> dict:
        try:
            document = databases.update_document(DB_ID, COLLECTION_ID, student_id, data)
            return _normalize_document(document)
        except AppwriteException:
            raise

    @staticmethod
    def soft_delete(student_id: str) -> dict:
        try:
            document = databases.update_document(
                DB_ID,
                COLLECTION_ID,
                student_id,
                {
                    "is_active": False,
                    "is_deleted": True,
                    "deleted_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            return _normalize_document(document)
        except AppwriteException:
            raise

    @staticmethod
    def find_by_matricule(matricule: str) -> dict | None:
        try:
            response = databases.list_documents(
                DB_ID,
                COLLECTION_ID,
                [Query.equal("matricule", [matricule])],
            )
            documents = response.get("documents", [])
            if not documents:
                return None
            return _normalize_document(documents[0])
        except AppwriteException:
            raise


class ReportJobRepository:
    @staticmethod
    def create(data: dict) -> dict:
        try:
            document = databases.create_document(DB_ID, REPORT_JOBS_COLLECTION_ID, "unique()", data)
            return _normalize_document(document)
        except AppwriteException:
            raise

    @staticmethod
    def update(job_id: str, data: dict) -> dict:
        try:
            document = databases.update_document(DB_ID, REPORT_JOBS_COLLECTION_ID, job_id, data)
            return _normalize_document(document)
        except AppwriteException:
            raise

    @staticmethod
    def get(job_id: str) -> dict | None:
        try:
            document = databases.get_document(DB_ID, REPORT_JOBS_COLLECTION_ID, job_id)
            return _normalize_document(document)
        except AppwriteException as exc:
            if getattr(exc, "code", None) == 404:
                return None
            raise