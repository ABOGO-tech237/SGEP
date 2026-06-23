from __future__ import annotations

import uuid
from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.test import SimpleTestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_SUPERADMIN, User


class AuthApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.user_id = str(uuid.uuid4())
		self.password = "SecurePass123!"
		self.user_payload = {
			"id": self.user_id,
			"email": "admin@example.com",
			"password": make_password(self.password),
			"role": ROLE_SUPERADMIN,
			"account_status": ACCOUNT_STATUS_ACTIVE,
			"student_id": None,
		}
		self.user = User.from_appwrite(self.user_payload)

	def test_login_success(self):
		with patch("accounts.services.UserRepository.get_by_email", return_value=self.user_payload):
			response = self.client.post(
				"/api/v1/auth/login/",
				{"email": "admin@example.com", "password": self.password},
				format="json",
			)

		self.assertEqual(response.status_code, 200)
		self.assertIn("access_token", response.data)
		self.assertIn("refresh_token", response.data)

	def test_login_invalid_credentials(self):
		with patch("accounts.services.UserRepository.get_by_email", return_value=None):
			response = self.client.post(
				"/api/v1/auth/login/",
				{"email": "wrong@example.com", "password": "bad"},
				format="json",
			)

		self.assertEqual(response.status_code, 403)

	def test_refresh_success(self):
		refresh = RefreshToken.for_user(self.user)
		refresh["role"] = self.user.role
		refresh["account_status"] = self.user.account_status
		refresh["email"] = self.user.email
		refresh["student_id"] = self.user.student_id

		with patch("accounts.services.RefreshTokenBlacklistRepository.is_blacklisted", return_value=False):
			response = self.client.post(
				"/api/v1/auth/refresh/",
				{"refresh": str(refresh)},
				format="json",
			)

		self.assertEqual(response.status_code, 200)
		self.assertIn("access_token", response.data)

	def test_refresh_blacklisted_token(self):
		refresh = RefreshToken.for_user(self.user)

		with patch("accounts.services.RefreshTokenBlacklistRepository.is_blacklisted", return_value=True):
			response = self.client.post(
				"/api/v1/auth/refresh/",
				{"refresh": str(refresh)},
				format="json",
			)

		self.assertEqual(response.status_code, 403)

	def test_logout_blacklists_token(self):
		refresh = RefreshToken.for_user(self.user)
		refresh["role"] = self.user.role
		refresh["account_status"] = self.user.account_status
		refresh["email"] = self.user.email
		refresh["student_id"] = self.user.student_id

		self.client.force_authenticate(user=self.user)

		with patch("accounts.services.RefreshTokenBlacklistRepository.is_blacklisted", return_value=False), patch(
			"accounts.services.RefreshTokenBlacklistRepository.add"
		) as add_mock:
			response = self.client.post(
				"/api/v1/auth/logout/",
				{"refresh": str(refresh)},
				format="json",
			)

		self.assertEqual(response.status_code, 204)
		add_mock.assert_called_once()

	def test_change_password_success(self):
		self.client.force_authenticate(user=self.user)

		with patch("accounts.services.UserRepository.get_by_id", return_value=self.user_payload), patch(
			"accounts.services.UserRepository.update"
		) as update_mock:
			response = self.client.post(
				"/api/v1/auth/change-password/",
				{
					"old_password": self.password,
					"new_password": "NewSecurePass456!",
					"confirm_password": "NewSecurePass456!",
				},
				format="json",
			)

		self.assertEqual(response.status_code, 200)
		update_mock.assert_called_once()

	def test_change_password_invalid_old_password(self):
		self.client.force_authenticate(user=self.user)

		with patch("accounts.services.UserRepository.get_by_id", return_value=self.user_payload):
			response = self.client.post(
				"/api/v1/auth/change-password/",
				{
					"old_password": "wrong-password",
					"new_password": "NewSecurePass456!",
					"confirm_password": "NewSecurePass456!",
				},
				format="json",
			)

		self.assertEqual(response.status_code, 401)


class BootstrapApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.url = "/api/v1/auth/bootstrap/"
		self.secret = "test-bootstrap-secret"
		self.payload = {
			"email": "admin@sgep.cm",
			"password": "AdminPassword123!",
			"role": "superadmin",
		}
		self.created_result = {
			"action": "created",
			"email": "admin@sgep.cm",
			"auth_id": "auth-1",
			"user_id": "user-1",
			"role": "superadmin",
		}

	@patch("accounts.views.settings.BOOTSTRAP_SECRET", "")
	def test_bootstrap_disabled_without_secret(self):
		response = self.client.post(
			self.url,
			self.payload,
			format="json",
			HTTP_X_BOOTSTRAP_TOKEN="anything",
		)
		self.assertEqual(response.status_code, 404)

	@patch("accounts.views.settings.BOOTSTRAP_SECRET", "test-bootstrap-secret")
	def test_bootstrap_wrong_token(self):
		response = self.client.post(
			self.url,
			self.payload,
			format="json",
			HTTP_X_BOOTSTRAP_TOKEN="wrong",
		)
		self.assertEqual(response.status_code, 403)

	@patch("accounts.views.settings.BOOTSTRAP_SECRET", "test-bootstrap-secret")
	@patch("accounts.views.UserRepository.count", return_value=1)
	def test_bootstrap_conflict_when_users_exist_without_email(self, _count_mock):
		response = self.client.post(
			self.url,
			{"password": "AdminPassword123!", "role": "superadmin"},
			format="json",
			HTTP_X_BOOTSTRAP_TOKEN=self.secret,
		)
		self.assertEqual(response.status_code, 409)

	@patch("accounts.views.settings.BOOTSTRAP_SECRET", "test-bootstrap-secret")
	@patch("accounts.views.create_or_reset_login_user", return_value=None)
	@patch("accounts.views.UserRepository.count", return_value=0)
	def test_bootstrap_create_success(self, _count_mock, create_mock):
		create_mock.return_value = self.created_result
		response = self.client.post(
			self.url,
			self.payload,
			format="json",
			HTTP_X_BOOTSTRAP_TOKEN=self.secret,
		)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["action"], "created")
		create_mock.assert_called_once()

	@patch("accounts.views.settings.BOOTSTRAP_SECRET", "test-bootstrap-secret")
	@patch("accounts.views.create_or_reset_login_user")
	@patch("accounts.views.UserRepository.count", return_value=2)
	def test_bootstrap_update_with_explicit_email(self, _count_mock, create_mock):
		create_mock.return_value = {
			"action": "updated",
			"email": "admin@sgep.cm",
			"user_id": "user-1",
			"auth_id": "user-1",
			"role": "superadmin",
			"auth_updated": True,
			"auth_error": None,
		}
		response = self.client.post(
			self.url,
			self.payload,
			format="json",
			HTTP_X_BOOTSTRAP_TOKEN=self.secret,
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["action"], "updated")
