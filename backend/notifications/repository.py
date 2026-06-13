from __future__ import annotations

from datetime import datetime, timezone

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID
COLLECTION_ID = "notifications"


def _normalize_document(document: dict) -> dict:
	normalized = dict(document)
	normalized["id"] = document.get("$id", document.get("id"))
	return normalized


def _now() -> str:
	return datetime.now(timezone.utc).isoformat()


class NotificationRepository:
	@staticmethod
	def create(data: dict) -> dict:
		payload = {
			"is_deleted": False,
			"is_read": False,
			"created_at": _now(),
			"updated_at": _now(),
			**data,
		}
		try:
			document = databases.create_document(DB_ID, COLLECTION_ID, "unique()", payload)
			return _normalize_document(document)
		except AppwriteException:
			raise

	@staticmethod
	def update(notification_id: str, data: dict) -> dict:
		payload = {"updated_at": _now(), **data}
		try:
			document = databases.update_document(DB_ID, COLLECTION_ID, notification_id, payload)
			return _normalize_document(document)
		except AppwriteException:
			raise

	@staticmethod
	def list_by_user(user_id: str) -> list[dict]:
		try:
			response = databases.list_documents(
				DB_ID,
				COLLECTION_ID,
				[
					Query.equal("user_id", [user_id]),
					Query.equal("is_deleted", [False]),
					Query.order_desc("created_at"),
				],
			)
			return [_normalize_document(document) for document in response.get("documents", [])]
		except AppwriteException:
			raise
