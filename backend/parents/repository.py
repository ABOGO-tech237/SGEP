from __future__ import annotations

from datetime import datetime, timezone

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases
from core.appwrite_utils import documents_of, to_dict

DB_ID = settings.APPWRITE_DB_ID
COLLECTION_ID = "messages"


def _normalize(document: dict) -> dict:
	document = to_dict(document)
	result = dict(document)
	result["id"] = document.get("$id", document.get("id"))
	return result


def _now() -> str:
	return datetime.now(timezone.utc).isoformat()


class MessageRepository:
	@staticmethod
	def list_for_user(user_id: str) -> list[dict]:
		try:
			response = databases.list_documents(
				DB_ID,
				COLLECTION_ID,
				[
					Query.equal("recipient_id", [user_id]),
					Query.equal("is_deleted", [False]),
					Query.order_desc("created_at"),
				],
			)
			return [_normalize(doc) for doc in documents_of(response)]
		except AppwriteException:
			raise

	@staticmethod
	def create(data: dict) -> dict:
		payload = {
			**data,
			"is_read": False,
			"is_deleted": False,
			"created_at": _now(),
			"updated_at": _now(),
		}
		try:
			return _normalize(databases.create_document(DB_ID, COLLECTION_ID, "unique()", payload))
		except AppwriteException:
			raise
