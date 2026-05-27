from __future__ import annotations

import secrets
import string

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_PARENT
from accounts.repository import UserRepository
from parents.repository import ParentRepository, ParentStudentRepository

try:
    from notifications.tasks import (
        send_account_reactivated_notification_task,
        send_account_suspended_notification_task,
        send_parent_credentials_task,
        suspend_parent_accounts_for_new_year_task,
    )
except Exception:  # pragma: no cover - tasks are optional at import time
    send_account_reactivated_notification_task = None
    send_account_suspended_notification_task = None
    send_parent_credentials_task = None
    suspend_parent_accounts_for_new_year_task = None


class ParentAccountService:
    @staticmethod
    def _temp_password(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def _resolve_student(student_or_id: dict | str) -> dict:
        if isinstance(student_or_id, dict):
            return student_or_id

        from students.repository import StudentRepository

        student = StudentRepository.get(str(student_or_id))
        if not student:
            raise ValidationError("Eleve introuvable.")
        return student

    @staticmethod
    def create_from_student(student_id: str | dict, guardians: list[dict]) -> list[dict]:
        student = ParentAccountService._resolve_student(student_id)
        if not guardians:
            raise ValidationError("Les informations du parent sont requises.")

        created_links: list[dict] = []

        for guardian in guardians:
            email = str(guardian.get("email", "")).lower().strip()
            if not email:
                raise ValidationError("L'email du parent est requis.")

            link = ParentStudentRepository.find_link(student["id"], email)
            if link:
                created_links.append(link)
                continue

            existing_parent = ParentRepository.get_by_email(email)
            user = None
            if existing_parent and existing_parent.get("user_id"):
                user_id = str(existing_parent["user_id"])
                user = UserRepository.get_by_id(user_id)
                if not user:
                    user = UserRepository.get_by_email(email)

            if not user:
                temp_password = ParentAccountService._temp_password(12)
                user_payload = {
                    "email": email,
                    "first_name": guardian.get("first_name", ""),
                    "last_name": guardian.get("last_name", ""),
                    "role": ROLE_PARENT,
                    "school_id": student.get("school_id"),
                    "phone": guardian.get("phone"),
                    "account_status": ACCOUNT_STATUS_ACTIVE,
                    "student_id": student.get("id"),
                    "is_deleted": False,
                    "password": make_password(temp_password),
                    "created_at": timezone.now().isoformat(),
                    "updated_at": timezone.now().isoformat(),
                }
                user = UserRepository.create(user_payload)

                if send_parent_credentials_task is not None:
                    send_parent_credentials_task.delay(user["id"], email, temp_password)

            parent_payload = {
                "first_name": guardian.get("first_name", ""),
                "last_name": guardian.get("last_name", ""),
                "relationship": guardian.get("relationship", ""),
                "phone": guardian.get("phone", ""),
                "phone2": guardian.get("phone2"),
                "email": email,
                "user_id": user["id"],
                "account_status": ACCOUNT_STATUS_ACTIVE,
                "school_id": student.get("school_id"),
                "is_deleted": False,
                "created_at": timezone.now().isoformat(),
                "updated_at": timezone.now().isoformat(),
            }

            parent = existing_parent or ParentRepository.create(parent_payload)

            link_payload = {
                "student_id": student["id"],
                "parent_id": parent.get("id"),
                "user_id": user["id"],
                "email": email,
                "relationship": guardian.get("relationship", ""),
                "is_deleted": False,
                "created_at": timezone.now().isoformat(),
                "updated_at": timezone.now().isoformat(),
            }
            created_links.append(ParentStudentRepository.create(link_payload))

        return created_links

    @staticmethod
    def suspend(student_id: str) -> list[dict]:
        links = ParentStudentRepository.list_by_student_id(student_id)
        updated_parents: list[dict] = []

        for link in links:
            parent_user_id = link.get("user_id")
            if not parent_user_id:
                continue

            updated = UserRepository.update(parent_user_id, {"account_status": "suspended", "updated_at": timezone.now().isoformat()})
            updated_parents.append(updated)

        if send_account_suspended_notification_task is not None:
            send_account_suspended_notification_task.delay(student_id)

        return updated_parents

    @staticmethod
    def reactivate(student_id: str) -> list[dict]:
        links = ParentStudentRepository.list_by_student_id(student_id)
        updated_parents: list[dict] = []

        for link in links:
            parent_user_id = link.get("user_id")
            if not parent_user_id:
                continue

            updated = UserRepository.update(parent_user_id, {"account_status": ACCOUNT_STATUS_ACTIVE, "updated_at": timezone.now().isoformat()})
            updated_parents.append(updated)

        if send_account_reactivated_notification_task is not None:
            send_account_reactivated_notification_task.delay(student_id)

        return updated_parents

    @staticmethod
    def suspend_new_school_year() -> list[dict]:
        if suspend_parent_accounts_for_new_year_task is not None:
            suspend_parent_accounts_for_new_year_task.delay()
        return []