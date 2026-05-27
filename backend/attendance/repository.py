from __future__ import annotations

from appwrite.exception import AppwriteException
from appwrite.query import Query
from django.conf import settings

from config.appwrite_client import databases

DB_ID = settings.APPWRITE_DB_ID
ATTENDANCE_COLLECTION_ID = "attendance"


class AttendanceRepository:
    @staticmethod
    def _normalize(document: dict) -> dict:
        normalized = dict(document)
        normalized["id"] = document.get("$id", document.get("id"))
        return normalized

    @staticmethod
    def list(
        class_id: str | None = None,
        student_id: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> dict:
        queries: list[object] = [Query.equal("is_deleted", [False]), Query.limit(limit), Query.offset(offset)]

        if class_id:
            queries.append(Query.equal("class_id", [class_id]))
        if student_id:
            queries.append(Query.equal("student_id", [student_id]))
        if date_from:
            queries.append(Query.greater_than_equal("date", date_from))
        if date_to:
            queries.append(Query.less_than_equal("date", date_to))

        try:
            response = databases.list_documents(DB_ID, ATTENDANCE_COLLECTION_ID, queries)
        except AppwriteException:
            raise

        response["documents"] = [AttendanceRepository._normalize(d) for d in response.get("documents", [])]
        return response

    @staticmethod
    def create(data: dict) -> dict:
        try:
            document = databases.create_document(DB_ID, ATTENDANCE_COLLECTION_ID, "unique()", data)
            return AttendanceRepository._normalize(document)
        except AppwriteException:
            raise

    @staticmethod
    def update(record_id: str, data: dict) -> dict:
        try:
            document = databases.update_document(DB_ID, ATTENDANCE_COLLECTION_ID, record_id, data)
            return AttendanceRepository._normalize(document)
        except AppwriteException:
            raise

    @staticmethod
    def get_stats(class_id: str, period: str) -> dict:
        """Aggregate attendance by student for a given class and period label."""
        response = AttendanceRepository.list(class_id=class_id)
        documents = response.get("documents", [])

        stats: dict[str, dict] = {}
        for record in documents:
            if period and str(record.get("period", "")) != str(period):
                continue
            student_id = record.get("student_id")
            if not student_id:
                continue

            item = stats.setdefault(
                student_id,
                {
                    "student_id": student_id,
                    "absences": 0,
                    "retards": 0,
                    "justified": 0,
                    "total": 0,
                },
            )
            item["total"] += 1
            kind = str(record.get("type", "absence"))
            if kind == "retard":
                item["retards"] += 1
            else:
                item["absences"] += 1
            if bool(record.get("is_justified", False)):
                item["justified"] += 1

        return {"results": list(stats.values())}
