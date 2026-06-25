from __future__ import annotations

from typing import Any

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases
from core.appwrite_utils import documents_of, to_dict, total_of

DB_ID = settings.APPWRITE_DB_ID
USERS_COLLECTION_ID = "users"
REFRESH_TOKEN_BLACKLIST_COLLECTION_ID = "refresh_token_blacklist"


class UserRepository:
    @staticmethod
    def _normalize_user(document: dict) -> dict:
        document = to_dict(document)
        normalized = dict(document)

        # Ensure we have an 'id' field for consistency
        if "id" not in normalized:
            normalized["id"] = document.get("$id")
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

            normalized_docs = [
                UserRepository._normalize_user(document)
                for document in documents_of(response)
            ]

            return {"documents": normalized_docs, "total": total_of(response)}
        except AppwriteException:
            raise

    @staticmethod
    def count(filters: list[Any] | None = None) -> int:
        try:
            response = databases.list_documents(DB_ID, USERS_COLLECTION_ID, filters or [])
            return total_of(response)
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

            documents = documents_of(response)
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
            return [UserRepository._normalize_user(document) for document in documents_of(response)]
        except AppwriteException:
            raise

    @staticmethod
    def list_by_role(role: str, account_status: str | None = None) -> list[dict]:
        queries: list = [
            Query.equal("role", [role]),
            Query.equal("is_deleted", [False]),
        ]
        if account_status:
            queries.append(Query.equal("account_status", [account_status]))
        try:
            response = databases.list_documents(DB_ID, USERS_COLLECTION_ID, queries)
            return [UserRepository._normalize_user(document) for document in documents_of(response)]
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
            return bool(documents_of(response))
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
