from __future__ import annotations

from datetime import datetime, timedelta

from students.repository import ReportJobRepository

from attendance.repository import AttendanceRepository
from attendance.tasks import (
    export_attendance_excel_task,
    export_attendance_pdf_task,
    notify_parent_absence_task,
)


class AttendanceService:
    @staticmethod
    def list(
        class_id: str | None = None,
        student_id: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict:
        response = AttendanceRepository.list(
            class_id=class_id,
            student_id=student_id,
            date_from=date_from,
            date_to=date_to,
        )
        return {"count": response.get("total", 0), "results": response.get("documents", [])}

    @staticmethod
    def record_absence(student_id: str, class_id: str, date: str, absence_type: str, motif: str | None) -> dict:
        payload = {
            "student_id": student_id,
            "class_id": class_id,
            "date": date,
            "type": absence_type,
            "motif": motif or "",
            "is_justified": False,
            "is_deleted": False,
        }
        record = AttendanceRepository.create(payload)
        notify_parent_absence_task.delay(student_id, date, absence_type)
        return record

    @staticmethod
    def update(record_id: str, validated_data: dict) -> dict:
        return AttendanceRepository.update(record_id, validated_data)

    @staticmethod
    def justify(record_id: str, motif: str, justification_doc: str | None = None) -> dict:
        payload = {
            "is_justified": True,
            "justification_motif": motif,
        }
        if justification_doc is not None:
            payload["justification_doc"] = justification_doc
        return AttendanceRepository.update(record_id, payload)

    @staticmethod
    def get_stats(class_id: str, date_from: str, date_to: str) -> dict:
        response = AttendanceRepository.list(class_id=class_id, date_from=date_from, date_to=date_to)
        records = response.get("documents", [])

        start = datetime.fromisoformat(date_from).date()
        end = datetime.fromisoformat(date_to).date()
        working_days = 0
        cursor = start
        while cursor <= end:
            if cursor.weekday() < 5:
                working_days += 1
            cursor += timedelta(days=1)

        per_student: dict[str, dict] = {}
        for r in records:
            sid = r.get("student_id")
            if not sid:
                continue
            item = per_student.setdefault(
                sid,
                {
                    "student_id": sid,
                    "absences": 0,
                    "retards": 0,
                    "justified_absences": 0,
                    "absence_rate": 0.0,
                },
            )
            if str(r.get("type", "absence")) == "retard":
                item["retards"] += 1
            else:
                item["absences"] += 1
                if bool(r.get("is_justified", False)):
                    item["justified_absences"] += 1

        for sid, item in per_student.items():
            if working_days > 0:
                item["absence_rate"] = round((item["absences"] / working_days) * 100, 2)
            else:
                item["absence_rate"] = 0.0

        return {
            "class_id": class_id,
            "date_from": date_from,
            "date_to": date_to,
            "working_days": working_days,
            "results": list(per_student.values()),
        }

    @staticmethod
    def export(class_id: str, date_from: str, date_to: str, export_format: str, requested_by: str) -> str:
        job = ReportJobRepository.create(
            {
                "type": f"attendance_{export_format}",
                "status": "pending",
                "requested_by": requested_by,
                "params": {
                    "class_id": class_id,
                    "date_from": date_from,
                    "date_to": date_to,
                },
            }
        )

        if export_format == "excel":
            export_attendance_excel_task.delay(job["id"], class_id, date_from, date_to)
        else:
            export_attendance_pdf_task.delay(job["id"], class_id, date_from, date_to)

        return job["id"]
