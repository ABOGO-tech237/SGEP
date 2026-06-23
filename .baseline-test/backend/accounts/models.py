import uuid
from typing import Optional, List

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


ROLE_SUPERADMIN = "superadmin"
ROLE_COMPTABLE = "comptable"
ROLE_PARENT = "parent"

ACCOUNT_STATUS_ACTIVE = "active"
ACCOUNT_STATUS_SUSPENDED = "suspended"


class UserManager(BaseUserManager):
	def create_user(self, email: str, password: Optional[str] = None, **extra_fields):
		if not email:
			raise ValueError("L'email est requis.")
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		if password:
			user.set_password(password)
		else:
			user.set_unusable_password()
		return user

	def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields):
		extra_fields.setdefault("role", ROLE_SUPERADMIN)
		extra_fields.setdefault("account_status", ACCOUNT_STATUS_ACTIVE)
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)

		if extra_fields.get("is_staff") is not True:
			raise ValueError("Le superuser doit avoir is_staff=True.")
		if extra_fields.get("is_superuser") is not True:
			raise ValueError("Le superuser doit avoir is_superuser=True.")

		return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	ROLE_CHOICES = (
		(ROLE_SUPERADMIN, "Super Admin"),
		(ROLE_COMPTABLE, "Comptable"),
		(ROLE_PARENT, "Parent"),
	)

	ACCOUNT_STATUS_CHOICES = (
		(ACCOUNT_STATUS_ACTIVE, "Active"),
		(ACCOUNT_STATUS_SUSPENDED, "Suspended"),
	)

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	email = models.EmailField(unique=True)
	role = models.CharField(max_length=20, choices=ROLE_CHOICES)
	account_status = models.CharField(
		max_length=20,
		choices=ACCOUNT_STATUS_CHOICES,
		default=ACCOUNT_STATUS_ACTIVE,
	)
	student_id = models.CharField(max_length=64, null=True, blank=True)

	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	date_joined = models.DateTimeField(default=timezone.now)

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS: List[str] = []

	objects = UserManager()

	class Meta:
		managed = False
		db_table = "accounts_user"

	def __str__(self) -> str:
		return self.email

	@classmethod
	def from_appwrite(cls, payload: dict):
		raw_id = payload.get("id") or payload.get("$id")
		return cls(
			id=raw_id,
			email=payload.get("email", ""),
			role=payload.get("role", ROLE_PARENT),
			account_status=payload.get("account_status", ACCOUNT_STATUS_ACTIVE),
			student_id=payload.get("student_id"),
			password=payload.get("password", ""),
			is_staff=payload.get("role") == ROLE_SUPERADMIN,
			is_superuser=payload.get("role") == ROLE_SUPERADMIN,
			is_active=payload.get("account_status") == ACCOUNT_STATUS_ACTIVE,
		)
