from __future__ import annotations

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID
PARENTS_COLLECTION_ID = "parents"
PARENT_STUDENT_COLLECTION_ID = "parent_student"


class ParentRepository:
    @staticmethod
    def _normalize(document: dict) -> dict:
        normalized = dict(document)
        normalized["id"] = document.get("$id", document.get("id"))
        return normalized

    @staticmethod
    def get_by_email(email: str) -> dict | None:
        try:
            response = databases.list_documents(DB_ID, PARENTS_COLLECTION_ID, [Query.equal("email", [email.lower()])])
            documents = response.get("documents", [])
            if not documents:
                return None
            return ParentRepository._normalize(documents[0])
        except AppwriteException:
            raise

    @staticmethod
    def create(data: dict) -> dict:
        try:
            document = databases.create_document(DB_ID, PARENTS_COLLECTION_ID, "unique()", data)
            return ParentRepository._normalize(document)
        except AppwriteException:
            raise


class ParentStudentRepository:
    @staticmethod
    def _normalize(document: dict) -> dict:
        normalized = dict(document)
        normalized["id"] = document.get("$id", document.get("id"))
        return normalized

    @staticmethod
    def list_by_student_id(student_id: str) -> list[dict]:
        try:
            response = databases.list_documents(
                DB_ID,
                PARENT_STUDENT_COLLECTION_ID,
                [Query.equal("student_id", [student_id]), Query.equal("is_deleted", [False])],
            )
            return [ParentStudentRepository._normalize(document) for document in response.get("documents", [])]
        except AppwriteException:
            raise

    @staticmethod
    def find_link(student_id: str, email: str) -> dict | None:
        try:
            response = databases.list_documents(
                DB_ID,
                PARENT_STUDENT_COLLECTION_ID,
                [
                    Query.equal("student_id", [student_id]),
                    Query.equal("email", [email.lower()]),
                    Query.equal("is_deleted", [False]),
                ],
            )
            documents = response.get("documents", [])
            if not documents:
                return None
            return ParentStudentRepository._normalize(documents[0])
        except AppwriteException:
            raise

    @staticmethod
    def create(data: dict) -> dict:
        try:
            document = databases.create_document(DB_ID, PARENT_STUDENT_COLLECTION_ID, "unique()", data)
            return ParentStudentRepository._normalize(document)
        except AppwriteException:
            raise