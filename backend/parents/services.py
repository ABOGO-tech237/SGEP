from __future__ import annotations

import secrets
import string
from datetime import datetime, timezone

from django.contrib.auth.hashers import make_password

from accounts.models import ACCOUNT_STATUS_ACTIVE, ACCOUNT_STATUS_SUSPENDED, ROLE_PARENT
from accounts.repository import UserRepository
from notifications.tasks import (
	notify_account_reactivated_task,
	notify_account_suspended_task,
	send_parent_credentials_task,
)


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
					UserRepository.update(
						existing["id"],
						{"student_id": student_id, "updated_at": ParentAccountService._now()},
					)
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
			send_parent_credentials_task.delay(user["id"], email, temp_password)
			created_accounts.append(
				{
					"parent_id": user["id"],
					"email": email,
					"temp_password": temp_password,
					"created": True,
				}
			)

		return created_accounts

	@staticmethod
	def suspend(student_id: str) -> list[dict]:
		suspended_accounts: list[dict] = []
		parents = UserRepository.list_by_student_id(student_id)

		for parent in parents:
			if parent.get("account_status") == ACCOUNT_STATUS_SUSPENDED:
				continue
			updated = UserRepository.update(
				parent["id"],
				{
					"account_status": ACCOUNT_STATUS_SUSPENDED,
					"updated_at": ParentAccountService._now(),
				},
			)
			notify_account_suspended_task.delay(parent["id"])
			suspended_accounts.append(updated)

		return suspended_accounts

	@staticmethod
	def reactivate(student_id: str) -> list[dict]:
		reactivated_accounts: list[dict] = []
		parents = UserRepository.list_by_student_id(student_id)

		for parent in parents:
			if parent.get("account_status") == ACCOUNT_STATUS_ACTIVE:
				continue
			updated = UserRepository.update(
				parent["id"],
				{
					"account_status": ACCOUNT_STATUS_ACTIVE,
					"updated_at": ParentAccountService._now(),
				},
			)
			notify_account_reactivated_task.delay(parent["id"])
			reactivated_accounts.append(updated)

		return reactivated_accounts
