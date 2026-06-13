from __future__ import annotations

from datetime import datetime, timezone

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID


def _normalize(document: dict) -> dict:
	result = dict(document)
	result["id"] = document.get("$id", document.get("id"))
	return result


class FeeTypeRepository:
	COLLECTION_ID = "fee_types"

	@staticmethod
	def get(fee_type_id: str) -> dict | None:
		try:
			return _normalize(databases.get_document(DB_ID, FeeTypeRepository.COLLECTION_ID, fee_type_id))
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def list() -> list[dict]:
		try:
			response = databases.list_documents(
				DB_ID,
				FeeTypeRepository.COLLECTION_ID,
				[Query.equal("is_deleted", [False]), Query.equal("is_active", [True])],
			)
			return [_normalize(doc) for doc in response.get("documents", [])]
		except AppwriteException:
			raise


class InvoiceRepository:
	COLLECTION_ID = "invoices"

	@staticmethod
	def list(student_id: str | None = None, status: str | None = None) -> list[dict]:
		queries: list = [Query.equal("is_deleted", [False]), Query.order_desc("created_at")]
		if student_id:
			queries.append(Query.equal("student_id", [student_id]))
		if status:
			queries.append(Query.equal("status", [status]))
		try:
			response = databases.list_documents(DB_ID, InvoiceRepository.COLLECTION_ID, queries)
			return [_normalize(doc) for doc in response.get("documents", [])]
		except AppwriteException:
			raise

	@staticmethod
	def get(invoice_id: str) -> dict | None:
		try:
			return _normalize(databases.get_document(DB_ID, InvoiceRepository.COLLECTION_ID, invoice_id))
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def find_existing(student_id: str, fee_type_id: str, academic_year_id: str) -> dict | None:
		try:
			response = databases.list_documents(
				DB_ID,
				InvoiceRepository.COLLECTION_ID,
				[
					Query.equal("student_id", [student_id]),
					Query.equal("fee_type_id", [fee_type_id]),
					Query.equal("academic_year_id", [academic_year_id]),
					Query.equal("is_deleted", [False]),
				],
			)
			docs = response.get("documents", [])
			return _normalize(docs[0]) if docs else None
		except AppwriteException:
			raise

	@staticmethod
	def create(data: dict) -> dict:
		try:
			return _normalize(databases.create_document(DB_ID, InvoiceRepository.COLLECTION_ID, "unique()", data))
		except AppwriteException:
			raise

	@staticmethod
	def update(invoice_id: str, data: dict) -> dict:
		try:
			return _normalize(databases.update_document(DB_ID, InvoiceRepository.COLLECTION_ID, invoice_id, data))
		except AppwriteException:
			raise


class PaymentRepository:
	COLLECTION_ID = "payments"

	@staticmethod
	def list(invoice_id: str | None = None) -> list[dict]:
		queries: list = [Query.equal("is_deleted", [False])]
		if invoice_id:
			queries.append(Query.equal("invoice_id", [invoice_id]))
		try:
			response = databases.list_documents(DB_ID, PaymentRepository.COLLECTION_ID, queries)
			return [_normalize(doc) for doc in response.get("documents", [])]
		except AppwriteException:
			raise

	@staticmethod
	def get(payment_id: str) -> dict | None:
		try:
			return _normalize(databases.get_document(DB_ID, PaymentRepository.COLLECTION_ID, payment_id))
		except AppwriteException as exc:
			if getattr(exc, "code", None) == 404:
				return None
			raise

	@staticmethod
	def create(data: dict) -> dict:
		try:
			return _normalize(databases.create_document(DB_ID, PaymentRepository.COLLECTION_ID, "unique()", data))
		except AppwriteException:
			raise

	@staticmethod
	def update(payment_id: str, data: dict) -> dict:
		try:
			return _normalize(databases.update_document(DB_ID, PaymentRepository.COLLECTION_ID, payment_id, data))
		except AppwriteException:
			raise

	@staticmethod
	def total_for_invoice(invoice_id: str) -> float:
		payments = PaymentRepository.list(invoice_id=invoice_id)
		return sum(float(p.get("amount", 0)) for p in payments)
