"""Shared logic for creating or resetting login users (management command + bootstrap API)."""

from __future__ import annotations

from datetime import datetime

from django.contrib.auth.hashers import make_password

from accounts.auth_service import AppwriteAuthService
from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_SUPERADMIN
from accounts.repository import UserRepository


def create_or_reset_login_user(
    *,
    email: str,
    password: str,
    role: str = ROLE_SUPERADMIN,
    first_name: str = "Admin",
    last_name: str = "SGEP",
) -> dict:
    """
    Create a new login user or reset an existing user's password.

    Mirrors ``python manage.py create_login_user`` — Appwrite Auth + users document
    with Django-hashed password for JWT login.
    """
    email = email.strip().lower()
    existing = UserRepository.get_by_email(email=email)
    if existing:
        user_id = existing.get("id")
        now_iso = datetime.utcnow().isoformat()
        UserRepository.update(
            user_id=user_id,
            data={
                "password": make_password(password),
                "updated_at": now_iso,
            },
        )
        auth_updated = True
        auth_error = None
        try:
            AppwriteAuthService.update_user_password(user_id=user_id, password=password)
        except Exception as exc:
            auth_updated = False
            auth_error = str(exc)
        return {
            "action": "updated",
            "email": email,
            "user_id": user_id,
            "auth_id": user_id,
            "role": existing.get("role", role),
            "auth_updated": auth_updated,
            "auth_error": auth_error,
        }

    result = AppwriteAuthService.create_user_with_auth(
        email=email,
        password=password,
        user_data={
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "account_status": ACCOUNT_STATUS_ACTIVE,
        },
    )
    return {
        "action": "created",
        "email": result["email"],
        "auth_id": result["auth_id"],
        "user_id": result["user_id"],
        "role": result["role"],
    }
