"""Appwrite authentication service."""

from appwrite.exception import AppwriteException
from django.conf import settings
from config.appwrite_client import users
from accounts.repository import UserRepository
from django.contrib.auth.hashers import make_password
import uuid
import secrets
from datetime import datetime


class AppwriteAuthService:
    """Service for managing Appwrite user authentication."""

    @staticmethod
    def create_user_account(email: str, password: str, name: str = "") -> dict:
        """
        Create an Appwrite user account.

        Args:
            email: User email
            password: User password
            name: User full name

        Returns:
            Created user dict with id, email, name
        """
        try:
            user = users.create(
                user_id="unique()",
                email=email,
                password=password,
                name=name,
            )
            return {
                "id": user.get("$id", user.get("id")),
                "email": user.get("email"),
                "name": user.get("name"),
            }
        except AppwriteException as e:
            raise Exception(f"Failed to create Appwrite user: {str(e)}")

    @staticmethod
    def create_user_with_auth(email: str, password: str, user_data: dict) -> dict:
        """
        Create both an Appwrite Auth account and a Users collection document.

        Args:
            email: User email
            password: User password
            user_data: Dict with role, first_name, last_name, account_status, etc.

        Returns:
            Created user document with auth linked
        """
        try:
            # Generate user ID upfront for consistency
            user_id = str(uuid.uuid4())

            # Create Appwrite Auth account
            auth_user = users.create(
                user_id=user_id,
                email=email,
                password=password,
                name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            )

            # Create user document in database with timestamps and hashed password
            now_iso = datetime.utcnow().isoformat()
            user_doc_data = {
                **user_data,
                "email": email.lower(),
                "password": make_password(password),
                "created_at": now_iso,
                "updated_at": now_iso,
            }

            user_doc = UserRepository.create(user_doc_data)

            return {
                "auth_id": auth_user.get("$id", auth_user.get("id")),
                "user_id": user_doc.get("id"),
                "email": email,
                "role": user_data.get("role"),
            }
        except AppwriteException as e:
            raise Exception(f"Failed to create user with auth: {str(e)}")

    @staticmethod
    def delete_user_account(user_id: str) -> bool:
        """Delete an Appwrite user account."""
        try:
            users.delete(user_id)
            return True
        except AppwriteException as e:
            raise Exception(f"Failed to delete Appwrite user: {str(e)}")

    @staticmethod
    def update_user_password(user_id: str, password: str) -> bool:
        """Update user password."""
        try:
            users.update_password(user_id, password)
            return True
        except AppwriteException as e:
            raise Exception(f"Failed to update password: {str(e)}")

    @staticmethod
    def get_user(user_id: str) -> dict:
        """Get Appwrite user by ID."""
        try:
            user = users.get(user_id)
            return {
                "id": user.get("$id", user.get("id")),
                "email": user.get("email"),
                "name": user.get("name"),
                "status": user.get("status"),
            }
        except AppwriteException as e:
            raise Exception(f"Failed to get user: {str(e)}")
