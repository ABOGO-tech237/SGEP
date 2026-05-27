from __future__ import annotations

import json

from rest_framework.exceptions import NotFound

from parents.services import ParentAccountService
from students.repository import ReportJobRepository, StudentHistoryRepository, StudentRepository
from students.tasks import generate_students_excel_export_task, generate_students_pdf_export_task


class StudentService:
    @staticmethod
    def list(
        class_id: str | None = None,
        academic_year_id: str | None = None,
        is_active: bool | str | None = None,
        search: str | None = None,
        page: int | str | None = 1,
        page_size: int | str | None = 20,
    ) -> dict:
        page_number = max(int(page or 1), 1)
        size = min(max(int(page_size or 20), 1), 100)

        if isinstance(is_active, str):
            lowered = is_active.lower()
            if lowered in ("true", "1", "yes"):
                active_filter: bool | None = True
            elif lowered in ("false", "0", "no"):
                active_filter = False
            else:
                active_filter = None
        else:
            active_filter = is_active

        offset = (page_number - 1) * size
        response = StudentRepository.list(
            class_id=class_id,
            academic_year_id=academic_year_id,
            is_active=active_filter,
            search=search,
            limit=size,
            offset=offset,
        )
        return {
            "count": response.get("total", len(response.get("documents", []))),
            "page": page_number,
            "page_size": size,
            "results": response.get("documents", []),
        }

    @staticmethod
    def get(student_id: str) -> dict:
        student = StudentRepository.get(student_id)
        if not student:
            raise NotFound("Eleve introuvable.")
        return student

    @staticmethod
    def create(validated_data: dict) -> dict:
        payload = dict(validated_data)
        parent_payload = payload.pop("parent", None)
        student = StudentRepository.create(payload)

        if parent_payload:
            parent_links = ParentAccountService.create_from_student(student["id"], [parent_payload])
            if parent_links:
                student = StudentRepository.update(student["id"], {"parent_user_id": parent_links[0].get("user_id")})

        StudentHistoryRepository.create(
            {
                "student_id": student["id"],
                "action": "create",
                "to_class_id": student.get("class_id"),
                "academic_year_id": student.get("academic_year_id"),
                "details": "Création du dossier élève.",
            }
        )
        return student

    @staticmethod
    def update(student_id: str, validated_data: dict) -> dict:
        payload = dict(validated_data)
        payload.pop("parent", None)
        student = StudentRepository.update(student_id, payload)
        StudentHistoryRepository.create(
            {
                "student_id": student_id,
                "action": "update",
                "to_class_id": student.get("class_id"),
                "academic_year_id": student.get("academic_year_id"),
                "details": "Mise à jour du dossier élève.",
            }
        )
        return student

    @staticmethod
    def soft_delete(student_id: str) -> dict:
        student = StudentRepository.soft_delete(student_id)
        StudentHistoryRepository.create(
            {
                "student_id": student_id,
                "action": "soft_delete",
                "to_class_id": student.get("class_id"),
                "academic_year_id": student.get("academic_year_id"),
                "details": "Suppression logique du dossier élève.",
            }
        )
        return student

    @staticmethod
    def enroll(student_id: str, class_id: str, academic_year_id: str) -> dict:
        current_student = StudentRepository.get(student_id)
        if not current_student:
            raise NotFound("Eleve introuvable.")

        class_document = StudentRepository.get_class(class_id)
        payload = {
            "class_id": class_id,
            "academic_year_id": academic_year_id,
        }
        if class_document and class_document.get("level_id"):
            payload["current_level_id"] = class_document["level_id"]

        student = StudentRepository.update(student_id, payload)
        StudentHistoryRepository.create(
            {
                "student_id": student_id,
                "action": "enroll",
                "from_class_id": current_student.get("class_id"),
                "to_class_id": class_id,
                "academic_year_id": academic_year_id,
                "details": "Inscription de l'élève dans une classe.",
            }
        )
        return student

    @staticmethod
    def promote(student_id: str, target_class_id: str) -> dict:
        current_student = StudentRepository.get(student_id)
        if not current_student:
            raise NotFound("Eleve introuvable.")

        class_document = StudentRepository.get_class(target_class_id)
        payload = {"class_id": target_class_id}
        if class_document:
            if class_document.get("level_id"):
                payload["current_level_id"] = class_document["level_id"]
            if class_document.get("academic_year_id"):
                payload["academic_year_id"] = class_document["academic_year_id"]

        student = StudentRepository.update(student_id, payload)
        StudentHistoryRepository.create(
            {
                "student_id": student_id,
                "action": "promote",
                "from_class_id": current_student.get("class_id"),
                "to_class_id": target_class_id,
                "academic_year_id": student.get("academic_year_id"),
                "details": "Passage dans la classe supérieure.",
            }
        )
        return student

    @staticmethod
    def get_history(student_id: str) -> list[dict]:
        StudentService.get(student_id)
        return StudentHistoryRepository.list(student_id)

    @staticmethod
    def export_pdf(params: dict, requested_by: str) -> str:
        job = ReportJobRepository.create(
            {
                "type": "students_pdf",
                "status": "pending",
                "requested_by": requested_by,
                "params": json.dumps(StudentService._params_to_dict(params), ensure_ascii=True),
            }
        )
        generate_students_pdf_export_task.delay(job["id"], job.get("params"))
        return job["id"]

    @staticmethod
    def export_excel(params: dict, requested_by: str) -> str:
        job = ReportJobRepository.create(
            {
                "type": "students_excel",
                "status": "pending",
                "requested_by": requested_by,
                "params": json.dumps(StudentService._params_to_dict(params), ensure_ascii=True),
            }
        )
        generate_students_excel_export_task.delay(job["id"], job.get("params"))
        return job["id"]

    @staticmethod
    def _params_to_dict(params: dict) -> dict:
        if hasattr(params, "items"):
            return {key: value for key, value in params.items()}
        return dict(params)