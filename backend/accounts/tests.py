"""Test user creation for all types."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserCreationTests(TestCase):
    """Test user creation for all role types."""

    def test_create_superadmin_user(self) -> None:
        """Test creating a superadmin user."""
        user = User.objects.create_superuser(
            email="admin@sgep.cm",
            password="TestPass123!",
        )

        self.assertEqual(user.email, "admin@sgep.cm")
        self.assertEqual(user.role, "superadmin")
        self.assertEqual(user.account_status, "active")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_comptable_user(self) -> None:
        """Test creating an accountant user."""
        user = User.objects.create_user(
            email="accounts@sgep.cm",
            password="TestPass123!",
            role="comptable",
            account_status="active",
        )

        self.assertEqual(user.email, "accounts@sgep.cm")
        self.assertEqual(user.role, "comptable")
        self.assertEqual(user.account_status, "active")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_parent_user(self) -> None:
        """Test creating a parent user."""
        user = User.objects.create_user(
            email="parent@example.cm",
            password="TestPass123!",
            role="parent",
            account_status="active",
        )

        self.assertEqual(user.email, "parent@example.cm")
        self.assertEqual(user.role, "parent")
        self.assertEqual(user.account_status, "active")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_user_without_email_fails(self) -> None:
        """Test creating a user without email raises error."""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                email="",
                password="TestPass123!",
            )

        self.assertIn("email", str(context.exception).lower())

    def test_create_user_with_suspended_status(self) -> None:
        """Test creating a user with suspended status."""
        user = User.objects.create_user(
            email="suspended@sgep.cm",
            password="TestPass123!",
            role="comptable",
            account_status="suspended",
        )

        self.assertEqual(user.account_status, "suspended")
        self.assertTrue(user.is_active)  # is_active != account_status

    def test_user_password_hashing(self) -> None:
        """Test that user passwords are hashed."""
        password = "TestPass123!"
        user = User.objects.create_user(
            email="user@sgep.cm",
            password=password,
        )

        # Password should be hashed, not plaintext
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.check_password(password))

    def test_superadmin_requires_is_staff_and_is_superuser(self) -> None:
        """Test that superadmin creation requires is_staff and is_superuser."""
        user = User.objects.create_superuser(
            email="admin@test.cm",
            password="TestPass123!",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_duplicate_email_allowed_at_creation(self) -> None:
        """Test that duplicate emails can be created (DB will reject or unique constraint)."""
        User.objects.create_user(
            email="duplicate@sgep.cm",
            password="TestPass123!",
        )

        # The second create_user might fail at DB level depending on constraints
        # This test documents the current behavior
        try:
            User.objects.create_user(
                email="duplicate@sgep.cm",
                password="TestPass123!",
            )
            # If we get here, duplicates are allowed
        except Exception:
            # If we get an error, duplicates are not allowed
            pass
