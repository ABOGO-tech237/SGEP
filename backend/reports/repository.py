from __future__ import annotations

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases
from core.appwrite_utils import to_dict

DB_ID = settings.APPWRITE_DB_ID
COLLECTION_ID = "report_jobs"


def _normalize(document: dict) -> dict:
	document = to_dict(document)
	result = dict(document)
	result["id"] = document.get("$id", document.get("id"))
	return result


class ReportJobRepository:
	@staticmethod
	def create(data: dict) -> dict:
		try:
			document = databases.create_document(DB_ID, COLLECTION_ID, "unique()", data)
			return _normalize(document)
		except AppwriteException:
			raise

	@staticmethod
	def update(job_id: str, data: dict) -> dict:
		try:
			document = databases.update_document(DB_ID, COLLECTION_ID, job_id, data)
			return _normalize(document)
		except AppwriteException:
			raise

	@staticmethod
	def get(job_id: str) -> dict | None:
		try:
			document = databases.get_document(DB_ID, COLLECTION_ID, job_id)
			return _normalize(document)
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise
