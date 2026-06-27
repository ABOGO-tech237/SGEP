from __future__ import annotations

import json
import secrets
import string
from datetime import datetime, timezone

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from core.exceptions import ConflictError, NotFoundError
from parents.services import ParentAccountService

from .repository import ReportJobRepository, StudentRepository


class StudentService:
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _fernet() -> Fernet:
        key = settings.MEDICAL_ENCRYPTION_KEY.strip()
        if not key:
            raise ImproperlyConfigured("MEDICAL_ENCRYPTION_KEY is required to encrypt student medical data.")
        return Fernet(key.encode())

    @staticmethod
    def _serialize_medical(medical: dict | None) -> str:
        if medical is None:
            return ""
        payload = json.dumps(medical, ensure_ascii=True, separators=(",", ":"))
        return StudentService._fernet().encrypt(payload.encode()).decode()

    @staticmethod
    def _build_search_index(payload: dict) -> str:
        parts = [
            payload.get("first_name", ""),
            payload.get("last_name", ""),
            payload.get("matricule", ""),
            payload.get("class_id", ""),
            payload.get("academic_year_id", ""),
        ]
        return " ".join(part.strip().lower() for part in parts if part)

    @staticmethod
    def _append_history(existing_history: str | list | None, event: dict) -> str:
        if isinstance(existing_history, str):
            try:
                history = json.loads(existing_history)
            except json.JSONDecodeError:
                history = []
        elif isinstance(existing_history, list):
            history = existing_history
        else:
            history = []

        history.append(event)
        return json.dumps(history, ensure_ascii=True)

    @staticmethod
    def list(**kwargs) -> dict:
        page = int(kwargs.get("page", 1) or 1)
        page_size = int(kwargs.get("page_size", 20) or 20)
        result = StudentRepository.list(
            class_id=kwargs.get("class_id"),
            academic_year_id=kwargs.get("academic_year_id"),
            is_active=kwargs.get("is_active"),
            search=kwargs.get("search"),
            page=page,
            page_size=page_size,
        )
        result["page"] = page
        result["page_size"] = page_size
        result["items"] = result.pop("documents", [])
        return result

    @staticmethod
    def get(student_id: str) -> dict:
        student = StudentRepository.get(student_id)
        if not student:
            raise NotFoundError(f"Student {student_id} introuvable.")
        return student

    @staticmethod
    def create(validated_data: dict, user_id: str = "system", ip_address: str = "") -> dict:
        payload = dict(validated_data)
        guardians = payload.pop("guardians", [])
        medical = payload.pop("medical", None)

        # class_id and academic_year_id are optional at registration; assigned via /enroll/
        for optional_field in ("class_id", "academic_year_id"):
            if payload.get(optional_field) is None:
                payload.pop(optional_field, None)

        # Auto-generate matricule when not provided
        if not payload.get("matricule"):
            year = datetime.now(timezone.utc).strftime("%y")
            payload["matricule"] = f"STU-{year}-{StudentService.generate_temp_code(6).upper()}"

        existing = StudentRepository.find_by_matricule(payload["matricule"])
        if existing:
            raise ConflictError("Le matricule existe deja.")

        payload["medical"] = StudentService._serialize_medical(medical)
        payload["history"] = StudentService._append_history(
            payload.get("history"),
            {
                "event": "create",
                "at": StudentService._now(),
            },
        )
        payload["search_index"] = StudentService._build_search_index(payload)
        payload.setdefault("is_active", True)
        payload.setdefault("is_deleted", False)
        payload.setdefault("created_at", StudentService._now())
        payload.setdefault("updated_at", StudentService._now())

        student = StudentRepository.create(payload)
        if guardians:
            ParentAccountService.create_from_student(student["id"], guardians)
        from core.audit import log_action

        log_action(user_id, "CREATE", "students", student["id"], {"matricule": student.get("matricule", "")}, ip_address)
        return student

    @staticmethod
    def update(student_id: str, validated_data: dict, user_id: str = "system", ip_address: str = "") -> dict:
        existing = StudentService.get(student_id)
        payload = dict(validated_data)

        if "matricule" in payload:
            duplicate = StudentRepository.find_by_matricule(payload["matricule"])
            if duplicate and duplicate.get("id") != student_id:
                raise ConflictError("Le matricule existe deja.")

        if "medical" in payload:
            payload["medical"] = StudentService._serialize_medical(payload.pop("medical"))
        elif "medical" not in payload and existing.get("medical"):
            payload["medical"] = existing["medical"]

        payload["search_index"] = StudentService._build_search_index({**existing, **payload})
        payload["updated_at"] = StudentService._now()
        updated = StudentRepository.update(student_id, payload)
        from core.audit import log_action

        log_action(user_id, "UPDATE", "students", student_id, validated_data, ip_address)
        return updated

    @staticmethod
    def soft_delete(student_id: str) -> dict:
        return StudentRepository.soft_delete(student_id)

    @staticmethod
    def enroll(student_id: str, class_id: str, academic_year_id: str) -> dict:
        student = StudentService.get(student_id)
        history_entry = {
            "event": "enroll",
            "class_id": class_id,
            "academic_year_id": academic_year_id,
            "at": StudentService._now(),
        }
        payload = {
            "class_id": class_id,
            "academic_year_id": academic_year_id,
            "history": StudentService._append_history(student.get("history"), history_entry),
            "search_index": StudentService._build_search_index({**student, "class_id": class_id, "academic_year_id": academic_year_id}),
            "updated_at": StudentService._now(),
        }
        updated = StudentRepository.update(student_id, payload)
        ParentAccountService.reactivate(student_id)
        from finance.services import InvoiceService

        InvoiceService.ensure_inscription_invoice(student_id, academic_year_id)
        return updated

    @staticmethod
    def promote(student_id: str, target_class_id: str) -> dict:
        student = StudentService.get(student_id)
        history_entry = {
            "event": "promote",
            "from_class_id": student.get("class_id"),
            "to_class_id": target_class_id,
            "at": StudentService._now(),
        }
        payload = {
            "class_id": target_class_id,
            "history": StudentService._append_history(student.get("history"), history_entry),
            "search_index": StudentService._build_search_index({**student, "class_id": target_class_id}),
            "updated_at": StudentService._now(),
        }
        return StudentRepository.update(student_id, payload)

    @staticmethod
    def history(student_id: str) -> list[dict]:
        student = StudentService.get(student_id)
        raw_history = student.get("history", [])
        if isinstance(raw_history, str):
            try:
                return json.loads(raw_history)
            except json.JSONDecodeError:
                return []
        if isinstance(raw_history, list):
            return raw_history
        return []

    @staticmethod
    def create_export_job(export_format: str, requested_by: str, params: dict | None = None) -> dict:
        job = ReportJobRepository.create(
            {
                "type": f"students_{export_format}",
                "status": "pending",
                "requested_by": requested_by,
                "file_path": "",
                "error": "",
                "params": json.dumps(params or {}, ensure_ascii=True),
                "is_deleted": False,
                "created_at": StudentService._now(),
                "updated_at": StudentService._now(),
            }
        )
        return job

    @staticmethod
    def generate_temp_code(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))