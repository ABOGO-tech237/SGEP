from __future__ import annotations

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
        normalized = dict(document)
        normalized["id"] = document.get("$id", document.get("id"))
        return normalized

    @staticmethod
    def get_by_email(email: str) -> dict | None:
        try:
            response = databases.list_documents(
                DB_ID,
                USERS_COLLECTION_ID,
                [Query.equal("email", [email.lower()])],
            )
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
