from __future__ import annotations

import json
from typing import Any

from appwrite.exception import AppwriteException
from appwrite.query import Query
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID
STUDENTS_COLLECTION_ID = "students"
STUDENT_HISTORIES_COLLECTION_ID = "student_histories"
REPORT_JOBS_COLLECTION_ID = "report_jobs"
CLASSES_COLLECTION_ID = "classes"


def _now() -> str:
    return timezone.now().isoformat()


def _get_fernet() -> Fernet:
    key = str(getattr(settings, "MEDICAL_ENCRYPTION_KEY", "") or "").strip()
    if not key:
        raise ImproperlyConfigured("MEDICAL_ENCRYPTION_KEY is required for medical encryption.")
    return Fernet(key.encode())


class StudentRepository:
    @staticmethod
    def _normalize(document: dict) -> dict:
        normalized = dict(document)
        normalized["id"] = document.get("$id", document.get("id"))
        medical_notes = normalized.pop("medical_notes", None)
        normalized["medical"] = StudentRepository._decode_medical(medical_notes)
        return normalized

    @staticmethod
    def _encode_medical(data: Any) -> str | None:
        if data in (None, ""):
            return None
        payload = json.dumps(data, ensure_ascii=True)
        return _get_fernet().encrypt(payload.encode("utf-8")).decode("utf-8")

    @staticmethod
    def _decode_medical(value: Any) -> dict | list | str | None:
        if value in (None, ""):
            return None
        raw_value = str(value)
        try:
            decrypted = _get_fernet().decrypt(raw_value.encode("utf-8")).decode("utf-8")
        except (InvalidToken, ValueError):
            decrypted = raw_value

        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return {"value": decrypted}

    @staticmethod
    def _prepare_payload(data: dict, include_created_at: bool = False) -> dict:
        payload = {key: value for key, value in data.items() if key != "parent"}
        medical = payload.pop("medical", None)
        if medical is not None:
            payload["medical_notes"] = StudentRepository._encode_medical(medical)
        if include_created_at:
            payload.setdefault("created_at", _now())
        payload.setdefault("updated_at", _now())
        payload.setdefault("is_active", True)
        payload.setdefault("is_deleted", False)
        return payload

    @staticmethod
    def list(
        class_id: str | None = None,
        academic_year_id: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        queries: list[Any] = [Query.equal("is_deleted", [False]), Query.limit(limit), Query.offset(offset)]
        if class_id:
            queries.append(Query.equal("class_id", [class_id]))
        if academic_year_id:
            queries.append(Query.equal("academic_year_id", [academic_year_id]))
        if is_active is not None:
            queries.append(Query.equal("is_active", [is_active]))
        if search:
            queries.append(
                Query.or_(
                    [
                        Query.search("first_name", search),
                        Query.search("last_name", search),
                        Query.search("matricule", search),
                    ]
                )
            )

        try:
            response = databases.list_documents(DB_ID, STUDENTS_COLLECTION_ID, queries)
        except AppwriteException:
            raise

        response["documents"] = [StudentRepository._normalize(document) for document in response.get("documents", [])]
        return response

    @staticmethod
    def get(student_id: str) -> dict | None:
        try:
            document = databases.get_document(DB_ID, STUDENTS_COLLECTION_ID, student_id)
            return StudentRepository._normalize(document)
        except AppwriteException as exc:
            if getattr(exc, "code", None) == 404:
                return None
            raise

    @staticmethod
    def find_by_matricule(matricule: str, exclude_student_id: str | None = None) -> dict | None:
        queries: list[Any] = [Query.equal("matricule", [matricule]), Query.equal("is_deleted", [False])]
        try:
            response = databases.list_documents(DB_ID, STUDENTS_COLLECTION_ID, queries)
        except AppwriteException:
            raise

        for document in response.get("documents", []):
            if exclude_student_id and document.get("$id") == exclude_student_id:
                continue
            return StudentRepository._normalize(document)
        return None

    @staticmethod
    def create(data: dict) -> dict:
        payload = StudentRepository._prepare_payload(data, include_created_at=True)
        try:
            document = databases.create_document(DB_ID, STUDENTS_COLLECTION_ID, "unique()", payload)
            return StudentRepository._normalize(document)
        except AppwriteException:
            raise

    @staticmethod
    def update(student_id: str, data: dict) -> dict:
        payload = StudentRepository._prepare_payload(data)
        try:
            document = databases.update_document(DB_ID, STUDENTS_COLLECTION_ID, student_id, payload)
            return StudentRepository._normalize(document)
        except AppwriteException:
            raise

    @staticmethod
    def soft_delete(student_id: str) -> dict:
        payload = {"is_active": False, "is_deleted": True, "updated_at": _now()}
        try:
            document = databases.update_document(DB_ID, STUDENTS_COLLECTION_ID, student_id, payload)
            return StudentRepository._normalize(document)
        except AppwriteException:
            raise

    @staticmethod
    def get_class(class_id: str) -> dict | None:
        try:
            document = databases.get_document(DB_ID, CLASSES_COLLECTION_ID, class_id)
            normalized = dict(document)
            normalized["id"] = document.get("$id", document.get("id"))
            return normalized
        except AppwriteException as exc:
            if getattr(exc, "code", None) == 404:
                return None
            raise


class StudentHistoryRepository:
    @staticmethod
    def list(student_id: str) -> list[dict]:
        queries: list[Any] = [
            Query.equal("student_id", [student_id]),
            Query.equal("is_deleted", [False]),
            Query.order_desc("created_at"),
        ]
        try:
            response = databases.list_documents(DB_ID, STUDENT_HISTORIES_COLLECTION_ID, queries)
        except AppwriteException:
            raise

        documents: list[dict] = []
        for document in response.get("documents", []):
            normalized = dict(document)
            normalized["id"] = document.get("$id", document.get("id"))
            documents.append(normalized)
        return documents

    @staticmethod
    def create(data: dict) -> dict:
        payload = dict(data)
        payload.setdefault("created_at", _now())
        payload.setdefault("updated_at", _now())
        payload.setdefault("is_deleted", False)
        try:
            document = databases.create_document(DB_ID, STUDENT_HISTORIES_COLLECTION_ID, "unique()", payload)
            normalized = dict(document)
            normalized["id"] = document.get("$id", document.get("id"))
            return normalized
        except AppwriteException:
            raise


class ReportJobRepository:
    @staticmethod
    def create(data: dict) -> dict:
        payload = dict(data)
        payload.setdefault("created_at", _now())
        payload.setdefault("updated_at", _now())
        payload.setdefault("is_deleted", False)
        try:
            document = databases.create_document(DB_ID, REPORT_JOBS_COLLECTION_ID, "unique()", payload)
            normalized = dict(document)
            normalized["id"] = document.get("$id", document.get("id"))
            return normalized
        except AppwriteException:
            raise

    @staticmethod
    def update(job_id: str, data: dict) -> dict:
        payload = dict(data)
        payload["updated_at"] = _now()
        try:
            document = databases.update_document(DB_ID, REPORT_JOBS_COLLECTION_ID, job_id, payload)
            normalized = dict(document)
            normalized["id"] = document.get("$id", document.get("id"))
            return normalized
        except AppwriteException:
            raise

    @staticmethod
    def get(job_id: str) -> dict | None:
        try:
            document = databases.get_document(DB_ID, REPORT_JOBS_COLLECTION_ID, job_id)
            normalized = dict(document)
            normalized["id"] = document.get("$id", document.get("id"))
            return normalized
        except AppwriteException as exc:
            if getattr(exc, "code", None) == 404:
                return None
            raise