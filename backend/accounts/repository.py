from __future__ import annotations

from typing import Any

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID
USERS_COLLECTION_ID = "users"
REFRESH_TOKEN_BLACKLIST_COLLECTION_ID = "refresh_token_blacklist"


class UserRepository:
    @staticmethod
    def _normalize_user(document: dict) -> dict:
        # Appwrite Document objects have custom fields in .data attribute
        if hasattr(document, "data"):
            raw_document = dict(document.data or {})
        elif hasattr(document, "model_dump"):
            raw_document = document.model_dump()
        elif isinstance(document, dict):
            raw_document = dict(document)
        else:
            raw_document = dict(document)

        normalized = dict(raw_document)

        # Ensure we have an 'id' field for consistency
        if "id" not in normalized:
            if isinstance(document, dict):
                normalized["id"] = document.get("$id")
            else:
                normalized["id"] = getattr(document, "id", None)
        return normalized
    @staticmethod
    def list(
        filters: list[Any] | None = None,
        limit: int = 50,
        offset: int = 0,
        order_desc: str | None = "created_at",
    ) -> dict:
        queries: list[Any] = list(filters or [])
        queries.append(Query.limit(limit))
        queries.append(Query.offset(offset))
        if order_desc:
            queries.append(Query.order_desc(order_desc))

        try:
            response = databases.list_documents(DB_ID, USERS_COLLECTION_ID, queries)

            # Newer Appwrite SDKs return a DocumentList-like object; older SDKs return dict.
            if hasattr(response, "documents"):
                documents = list(response.documents or [])
                total = int(getattr(response, "total", 0) or 0)
            else:
                documents = response.get("documents", [])
                total = int(response.get("total", 0) or 0)

            normalized_docs = [
                UserRepository._normalize_user(document)
                for document in documents
            ]

            return {"documents": normalized_docs, "total": total}
        except AppwriteException:
            raise

    @staticmethod
    def count(filters: list[Any] | None = None) -> int:
        try:
            response = databases.list_documents(DB_ID, USERS_COLLECTION_ID, filters or [])
            if hasattr(response, "total"):
                return int(getattr(response, "total", 0) or 0)
            return int(response.get("total", 0) or 0)
        except AppwriteException:
            raise

    @staticmethod
    def get_by_email(email: str) -> dict | None:
        try:
            response = databases.list_documents(
                DB_ID,
                USERS_COLLECTION_ID,
                [Query.equal("email", [email.lower()])],
            )

            if hasattr(response, "documents"):
                documents = list(response.documents or [])
            else:
                documents = response.get("documents", [])

            if not documents:
                return None

            return UserRepository._normalize_user(documents[0])
        except AppwriteException:
            raise

    @staticmethod
    def get_by_id(user_id: str) -> dict | None:
        try:
            document = databases.get_document(DB_ID, USERS_COLLECTION_ID, user_id)
            return UserRepository._normalize_user(document)
        except AppwriteException as exc:
            # 404 from Appwrite should be treated as not found by callers.
            if getattr(exc, "code", None) == 404:
                return None
            raise

    @staticmethod
    def create(data: dict) -> dict:
        try:
            document = databases.create_document(
                DB_ID,
                USERS_COLLECTION_ID,
                "unique()",
                data,
            )
            return UserRepository._normalize_user(document)
        except AppwriteException:
            raise

    @staticmethod
    def update(user_id: str, data: dict) -> dict:
        try:
            document = databases.update_document(DB_ID, USERS_COLLECTION_ID, user_id, data)
            return UserRepository._normalize_user(document)
        except AppwriteException:
            raise

    @staticmethod
    def list_by_student_id(student_id: str) -> list[dict]:
        try:
            response = databases.list_documents(
                DB_ID,
                USERS_COLLECTION_ID,
                [
                    Query.equal("student_id", [student_id]),
                    Query.equal("role", ["parent"]),
                    Query.equal("is_deleted", [False]),
                ],
            )
            return [UserRepository._normalize_user(document) for document in response.get("documents", [])]
        except AppwriteException:
            raise


class RefreshTokenBlacklistRepository:
    @staticmethod
    def is_blacklisted(jti: str) -> bool:
        try:
            response = databases.list_documents(
                DB_ID,
                REFRESH_TOKEN_BLACKLIST_COLLECTION_ID,
                [Query.equal("jti", [jti])],
            )
            return bool(response.get("documents", []))
        except AppwriteException:
            raise

    @staticmethod
    def add(jti: str, token: str, user_id: str, expires_at: int) -> dict:
        payload = {
            "jti": jti,
            "token": token,
            "user_id": user_id,
            "expires_at": expires_at,
        }
        try:
            return databases.create_document(
                DB_ID,
                REFRESH_TOKEN_BLACKLIST_COLLECTION_ID,
                "unique()",
                payload,
            )
        except AppwriteException:
            raise
