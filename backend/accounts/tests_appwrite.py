"""Integration tests using real Appwrite Cloud."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from django.test import TestCase

from accounts.repository import UserRepository
from core.appwrite_test_utils import skip_unless_appwrite


def _appwrite_user_payload(**overrides) -> dict:
	now = datetime.now(timezone.utc).isoformat()
	payload = {
		"first_name": "Test",
		"last_name": "User",
		"phone": "",
		"is_deleted": False,
		"created_at": now,
		"updated_at": now,
	}
	payload.update(overrides)
	return payload


@skip_unless_appwrite()
class UserCreationWithAppwriteTests(TestCase):
	"""Test user creation with real Appwrite Cloud backend."""

	def setUp(self) -> None:
		self.test_emails = [
			"test_superadmin@sgep.test",
			"test_comptable@sgep.test",
			"test_parent@sgep.test",
			"test_duplicate@sgep.test",
		]

	def tearDown(self) -> None:
		for email in self.test_emails:
			try:
				user = UserRepository.get_by_email(email)
				if user:
					pass
			except Exception:
				pass

	def test_create_superadmin_user_in_appwrite(self) -> None:
		email = "test_superadmin@sgep.test"
		password = "TestPass123!"

		user_data = _appwrite_user_payload(
			email=email,
			password=password,
			role="superadmin",
			account_status="active",
		)

		created_user = UserRepository.create(user_data)

		self.assertIsNotNone(created_user)
		self.assertIsNotNone(created_user.get("id"))
		self.assertEqual(created_user["email"], email)
		self.assertEqual(created_user["role"], "superadmin")
		self.assertEqual(created_user["account_status"], "active")

	def test_create_comptable_user_in_appwrite(self) -> None:
		email = "test_comptable@sgep.test"
		password = "TestPass123!"

		user_data = _appwrite_user_payload(
			email=email,
			password=password,
			role="comptable",
			account_status="active",
		)

		created_user = UserRepository.create(user_data)

		self.assertIsNotNone(created_user)
		self.assertEqual(created_user["email"], email)
		self.assertEqual(created_user["role"], "comptable")

	def test_create_parent_user_in_appwrite(self) -> None:
		email = "test_parent@sgep.test"
		password = "TestPass123!"

		user_data = _appwrite_user_payload(
			email=email,
			password=password,
			role="parent",
			account_status="active",
		)

		created_user = UserRepository.create(user_data)

		self.assertIsNotNone(created_user)
		self.assertEqual(created_user["email"], email)
		self.assertEqual(created_user["role"], "parent")

	def test_retrieve_user_by_email_from_appwrite(self) -> None:
		email = "test_superadmin@sgep.test"
		password = "TestPass123!"

		user_data = _appwrite_user_payload(
			email=email,
			password=password,
			role="superadmin",
			account_status="active",
		)
		UserRepository.create(user_data)

		retrieved_user = UserRepository.get_by_email(email)

		self.assertIsNotNone(retrieved_user)
		self.assertEqual(retrieved_user["email"], email)
		self.assertEqual(retrieved_user["role"], "superadmin")

	def test_retrieve_user_by_id_from_appwrite(self) -> None:
		email = "test_comptable@sgep.test"
		password = "TestPass123!"

		user_data = _appwrite_user_payload(
			email=email,
			password=password,
			role="comptable",
			account_status="active",
		)
		created_user = UserRepository.create(user_data)
		user_id = created_user["id"]

		retrieved_user = UserRepository.get_by_id(user_id)

		self.assertIsNotNone(retrieved_user)
		self.assertEqual(retrieved_user["id"], user_id)
		self.assertEqual(retrieved_user["email"], email)

	def test_update_user_status_in_appwrite(self) -> None:
		email = "test_parent@sgep.test"
		password = "TestPass123!"

		user_data = _appwrite_user_payload(
			email=email,
			password=password,
			role="parent",
			account_status="active",
		)
		created_user = UserRepository.create(user_data)
		user_id = created_user["id"]

		updated_user = UserRepository.update(user_id, {"account_status": "suspended"})

		self.assertEqual(updated_user["account_status"], "suspended")

		retrieved_user = UserRepository.get_by_id(user_id)
		self.assertEqual(retrieved_user["account_status"], "suspended")

	def test_user_not_found_returns_none(self) -> None:
		non_existent_email = "does_not_exist@sgep.test"

		user = UserRepository.get_by_email(non_existent_email)

		self.assertIsNone(user)

	def test_multiple_user_creation_different_roles(self) -> None:
		users_data = [
			_appwrite_user_payload(
				email="test_superadmin@sgep.test",
				password="Pass123!",
				role="superadmin",
				account_status="active",
			),
			_appwrite_user_payload(
				email="test_comptable@sgep.test",
				password="Pass123!",
				role="comptable",
				account_status="active",
			),
			_appwrite_user_payload(
				email="test_parent@sgep.test",
				password="Pass123!",
				role="parent",
				account_status="active",
			),
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
		local_part = f"Test.User.{uuid.uuid4().hex[:8]}"
		email = f"{local_part}@Sgep.Test"
		password = "TestPass123!"

		user_data = _appwrite_user_payload(
			email=email,
			password=password,
			role="parent",
			account_status="active",
		)
		created_user = UserRepository.create(user_data)

		retrieved_user = UserRepository.get_by_email(email.lower())

		self.assertIsNotNone(retrieved_user)
		self.assertEqual(retrieved_user["id"], created_user["id"])
		self.assertEqual(retrieved_user["email"].lower(), email.lower())
