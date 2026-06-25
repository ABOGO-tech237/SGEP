from __future__ import annotations

from datetime import datetime, timezone

from appwrite.exception import AppwriteException
from django.conf import settings

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID
COLLECTION_ID = "audit_logs"


def log_action(
	user_id: str,
	action: str,
	collection: str,
	document_id: str,
	diff: dict,
	ip_address: str,
) -> None:
	payload = {
		"user_id": user_id,
		"action": action,
		"resource_type": collection,
		"resource_id": document_id,
		"details": str(diff),
		"ip_address": ip_address,
		"is_deleted": False,
		"created_at": datetime.now(timezone.utc).isoformat(),
		"updated_at": datetime.now(timezone.utc).isoformat(),
	}
	try:
		databases.create_document(DB_ID, COLLECTION_ID, "unique()", payload)
	except AppwriteException:
		pass
