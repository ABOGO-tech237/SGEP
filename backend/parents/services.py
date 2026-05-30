from __future__ import annotations

import secrets
import string
from datetime import datetime, timezone

from django.contrib.auth.hashers import make_password

from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_PARENT
from accounts.repository import UserRepository


class ParentAccountService:
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _generate_temp_password(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def create_from_student(student_id: str, guardians: list[dict]) -> list[dict]:
        created_accounts: list[dict] = []

        for guardian in guardians:
            email = str(guardian.get("email", "")).strip().lower()
            if not email:
                continue

            existing = UserRepository.get_by_email(email)
            if existing:
                if not existing.get("student_id"):
                    UserRepository.update(existing["id"], {"student_id": student_id, "updated_at": ParentAccountService._now()})
                created_accounts.append({"parent_id": existing["id"], "email": email, "created": False})
                continue

            temp_password = ParentAccountService._generate_temp_password()
            payload = {
                "email": email,
                "password": make_password(temp_password),
                "role": ROLE_PARENT,
                "account_status": ACCOUNT_STATUS_ACTIVE,
                "student_id": student_id,
                "first_name": guardian.get("first_name", ""),
                "last_name": guardian.get("last_name", ""),
                "phone": guardian.get("phone", ""),
                "is_deleted": False,
                "created_at": ParentAccountService._now(),
                "updated_at": ParentAccountService._now(),
            }
            user = UserRepository.create(payload)
            created_accounts.append(
                {
                    "parent_id": user["id"],
                    "email": email,
                    "temp_password": temp_password,
                    "created": True,
                }
            )

        return created_accounts