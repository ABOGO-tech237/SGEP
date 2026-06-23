from __future__ import annotations

from django.contrib.auth.hashers import check_password, make_password
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from appwrite.query import Query

from accounts.models import (
    ACCOUNT_STATUS_ACTIVE,
    ACCOUNT_STATUS_SUSPENDED,
    ROLE_COMPTABLE,
    ROLE_PARENT,
    ROLE_SUPERADMIN,
    User,
)
from accounts.repository import RefreshTokenBlacklistRepository, UserRepository


class AuthService:
    @staticmethod
    def login(email: str, password: str) -> dict:
        user_payload = UserRepository.get_by_email(email=email)
        if not user_payload:
            raise AuthenticationFailed("Identifiants invalides.")

        stored_hash = user_payload.get("password", "")
        is_password_valid = check_password(password, stored_hash)

        # Temporary compatibility if legacy data contains clear password values.
        if not is_password_valid and stored_hash == password:
            is_password_valid = True

        if not is_password_valid:
            raise AuthenticationFailed("Identifiants invalides.")

        if user_payload.get("account_status") == ACCOUNT_STATUS_SUSPENDED:
            raise AuthenticationFailed("Compte suspendu.")

        user = User.from_appwrite(user_payload)
        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role
        refresh["account_status"] = user.account_status
        refresh["email"] = user.email
        refresh["student_id"] = user.student_id

        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        try:
            refresh = RefreshToken(refresh_token)
        except TokenError as exc:
            raise AuthenticationFailed("Refresh token invalide.") from exc

        jti = str(refresh.get("jti", ""))
        if not jti:
            raise AuthenticationFailed("Refresh token invalide.")

        if RefreshTokenBlacklistRepository.is_blacklisted(jti=jti):
            raise AuthenticationFailed("Refresh token blacklisté.")

        return {"access_token": str(refresh.access_token)}

    @staticmethod
    def logout(refresh_token: str) -> None:
        try:
            refresh = RefreshToken(refresh_token)
        except TokenError as exc:
            raise AuthenticationFailed("Refresh token invalide.") from exc

        jti = str(refresh.get("jti", ""))
        user_id = str(refresh.get("user_id", ""))
        exp = int(refresh.get("exp", 0))

        if not jti or not user_id or not exp:
            raise ValidationError("Refresh token incomplet.")

        if RefreshTokenBlacklistRepository.is_blacklisted(jti=jti):
            return

        RefreshTokenBlacklistRepository.add(
            jti=jti,
            token=refresh_token,
            user_id=user_id,
            expires_at=exp,
        )

    @staticmethod
    def change_password(user_id: str, old_password: str, new_password: str) -> None:
        user_payload = UserRepository.get_by_id(user_id=user_id)
        if not user_payload:
            raise AuthenticationFailed("Utilisateur introuvable.")

        stored_hash = user_payload.get("password", "")
        is_password_valid = check_password(old_password, stored_hash)

        if not is_password_valid and stored_hash == old_password:
            is_password_valid = True

        if not is_password_valid:
            raise AuthenticationFailed("Ancien mot de passe invalide.")

        UserRepository.update(user_id=user_id, data={"password": make_password(new_password)})


class AdminDashboardService:
    @staticmethod
    def _build_user_summary(document: dict) -> dict:
        first_name = str(document.get("first_name", "") or "").strip()
        last_name = str(document.get("last_name", "") or "").strip()
        name = str(document.get("name", "") or "").strip()
        full_name = " ".join(part for part in [first_name, last_name] if part).strip()

        return {
            "id": document.get("id", ""),
            "email": document.get("email", ""),
            "name": name or full_name or document.get("email", ""),
            "first_name": first_name,
            "last_name": last_name,
            "role": document.get("role", ROLE_PARENT),
            "account_status": document.get("account_status", ACCOUNT_STATUS_ACTIVE),
            "created_at": str(document.get("created_at", document.get("$createdAt", "")) or ""),
            "updated_at": str(document.get("updated_at", document.get("$updatedAt", "")) or ""),
        }

    @staticmethod
    def get_overview() -> dict:
        total_users = UserRepository.count()
        active_users = UserRepository.count([Query.equal("account_status", [ACCOUNT_STATUS_ACTIVE])])
        suspended_users = UserRepository.count([Query.equal("account_status", [ACCOUNT_STATUS_SUSPENDED])])
        superadmins = UserRepository.count([Query.equal("role", [ROLE_SUPERADMIN])])
        comptables = UserRepository.count([Query.equal("role", [ROLE_COMPTABLE])])
        parents = UserRepository.count([Query.equal("role", [ROLE_PARENT])])

        recent_response = UserRepository.list(limit=5)
        recent_users = [
            AdminDashboardService._build_user_summary(document)
            for document in recent_response.get("documents", [])
        ]

        return {
            "total_users": total_users,
            "active_users": active_users,
            "suspended_users": suspended_users,
            "superadmins": superadmins,
            "comptables": comptables,
            "parents": parents,
            "recent_users": recent_users,
        }
