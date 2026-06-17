"""Integration tests using real Appwrite Cloud."""

from __future__ import annotations

import time
from django.test import TestCase

from accounts.repository import UserRepository
from accounts.services import AuthService


class UserCreationWithAppwriteTests(TestCase):
    """Test user creation with real Appwrite Cloud backend."""

    def setUp(self) -> None:
        """Clean up test users before each test."""
        self.test_emails = [
            "test_superadmin@sgep.test",
            "test_comptable@sgep.test",
            "test_parent@sgep.test",
            "test_duplicate@sgep.test",
        ]

    def tearDown(self) -> None:
        """Clean up test users after each test."""
        for email in self.test_emails:
            try:
                user = UserRepository.get_by_email(email)
                if user:
                    # Delete would need implementation in repository
                    pass
            except Exception:
                pass

    def test_create_superadmin_user_in_appwrite(self) -> None:
        """Test creating a superadmin user in Appwrite."""
        email = "test_superadmin@sgep.test"
        password = "TestPass123!"

        user_data = {
            "email": email,
            "password": password,
            "role": "superadmin",
            "account_status": "active",
            "is_staff": True,
            "is_superuser": True,
        }

        # Create user in Appwrite
        created_user = UserRepository.create(user_data)

        self.assertIsNotNone(created_user)
        self.assertIsNotNone(created_user.get("id"))
        self.assertEqual(created_user["email"], email)
        self.assertEqual(created_user["role"], "superadmin")
        self.assertEqual(created_user["account_status"], "active")

    def test_create_comptable_user_in_appwrite(self) -> None:
        """Test creating an accountant user in Appwrite."""
        email = "test_comptable@sgep.test"
        password = "TestPass123!"

        user_data = {
            "email": email,
            "password": password,
            "role": "comptable",
            "account_status": "active",
        }

        created_user = UserRepository.create(user_data)

        self.assertIsNotNone(created_user)
        self.assertEqual(created_user["email"], email)
        self.assertEqual(created_user["role"], "comptable")

    def test_create_parent_user_in_appwrite(self) -> None:
        """Test creating a parent user in Appwrite."""
        email = "test_parent@sgep.test"
        password = "TestPass123!"

        user_data = {
            "email": email,
            "password": password,
            "role": "parent",
            "account_status": "active",
        }

        created_user = UserRepository.create(user_data)

        self.assertIsNotNone(created_user)
        self.assertEqual(created_user["email"], email)
        self.assertEqual(created_user["role"], "parent")

    def test_retrieve_user_by_email_from_appwrite(self) -> None:
        """Test retrieving a user by email from Appwrite."""
        email = "test_superadmin@sgep.test"
        password = "TestPass123!"

        # Create user
        user_data = {
            "email": email,
            "password": password,
            "role": "superadmin",
            "account_status": "active",
        }
        UserRepository.create(user_data)

        # Retrieve by email
        retrieved_user = UserRepository.get_by_email(email)

        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user["email"], email)
        self.assertEqual(retrieved_user["role"], "superadmin")

    def test_retrieve_user_by_id_from_appwrite(self) -> None:
        """Test retrieving a user by ID from Appwrite."""
        email = "test_comptable@sgep.test"
        password = "TestPass123!"

        # Create user
        user_data = {
            "email": email,
            "password": password,
            "role": "comptable",
            "account_status": "active",
        }
        created_user = UserRepository.create(user_data)
        user_id = created_user["id"]

        # Retrieve by ID
        retrieved_user = UserRepository.get_by_id(user_id)

        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user["id"], user_id)
        self.assertEqual(retrieved_user["email"], email)

    def test_update_user_status_in_appwrite(self) -> None:
        """Test updating user account status in Appwrite."""
        email = "test_parent@sgep.test"
        password = "TestPass123!"

        # Create user with active status
        user_data = {
            "email": email,
            "password": password,
            "role": "parent",
            "account_status": "active",
        }
        created_user = UserRepository.create(user_data)
        user_id = created_user["id"]

        # Update to suspended
        updated_user = UserRepository.update(user_id, {"account_status": "suspended"})

        self.assertEqual(updated_user["account_status"], "suspended")

        # Verify update persisted
        retrieved_user = UserRepository.get_by_id(user_id)
        self.assertEqual(retrieved_user["account_status"], "suspended")

    def test_user_not_found_returns_none(self) -> None:
        """Test that retrieving non-existent user returns None."""
        non_existent_email = "does_not_exist@sgep.test"

        user = UserRepository.get_by_email(non_existent_email)

        self.assertIsNone(user)

    def test_multiple_user_creation_different_roles(self) -> None:
        """Test creating users with all different roles."""
        users_data = [
            {
                "email": "test_superadmin@sgep.test",
                "password": "Pass123!",
                "role": "superadmin",
                "account_status": "active",
            },
            {
                "email": "test_comptable@sgep.test",
                "password": "Pass123!",
                "role": "comptable",
                "account_status": "active",
            },
            {
                "email": "test_parent@sgep.test",
                "password": "Pass123!",
                "role": "parent",
                "account_status": "active",
            },
        ]

        created_users = []
        for user_data in users_data:
            user = UserRepository.create(user_data)
            created_users.append(user)

        self.assertEqual(len(created_users), 3)
        self.assertEqual(created_users[0]["role"], "superadmin")
        self.assertEqual(created_users[1]["role"], "comptable")
        self.assertEqual(created_users[2]["role"], "parent")

    def test_case_insensitive_email_lookup(self) -> None:
        """Test that email lookup is case-insensitive."""
        email = "Test.User@Sgep.Test"
        password = "TestPass123!"

        # Create with mixed case
        user_data = {
            "email": email,
            "password": password,
            "role": "parent",
            "account_status": "active",
        }
        created_user = UserRepository.create(user_data)

        # Retrieve with different case
        retrieved_user = UserRepository.get_by_email(email.lower())

        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user["id"], created_user["id"])
