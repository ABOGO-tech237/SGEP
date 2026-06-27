from __future__ import annotations

import json

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers

from .repository import StudentRepository


def _fernet() -> Fernet:
    key = settings.MEDICAL_ENCRYPTION_KEY.strip()
    if not key:
        raise ImproperlyConfigured("MEDICAL_ENCRYPTION_KEY is required to decrypt student medical data.")
    return Fernet(key.encode())


def _decode_medical(value: str | None) -> dict | None:
    if not value:
        return None
    try:
        decrypted = _fernet().decrypt(value.encode()).decode()
        return json.loads(decrypted)
    except (InvalidToken, json.JSONDecodeError, ValueError):
        return None


def _parse_history(value: str | list | None) -> list[dict]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


class StudentSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    matricule = serializers.CharField()
    birth_date = serializers.CharField()
    birth_place = serializers.CharField()
    gender = serializers.CharField()
    id_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    class_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    academic_year_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    school_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    is_deleted = serializers.BooleanField(required=False)
    medical = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()
    created_at = serializers.CharField(required=False)
    updated_at = serializers.CharField(required=False)
    deleted_at = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def get_medical(self, obj: dict) -> dict | None:
        return _decode_medical(obj.get("medical"))

    def get_history(self, obj: dict) -> list[dict]:
        return _parse_history(obj.get("history"))


class StudentListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    matricule = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    class_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    academic_year_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField(required=False)


class StudentCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    matricule = serializers.CharField(max_length=50)
    birth_date = serializers.CharField()
    birth_place = serializers.CharField(max_length=100)
    gender = serializers.CharField(max_length=10)
    id_number = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    class_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
    academic_year_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
    school_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    medical = serializers.JSONField(required=False, allow_null=True)
    guardians = serializers.ListField(child=serializers.DictField(), required=False)

    def validate_matricule(self, value: str) -> str:
        student_id = self.context.get("student_id")
        existing = StudentRepository.find_by_matricule(value)
        if existing and existing.get("id") != student_id:
            raise serializers.ValidationError("Le matricule existe deja.")
        return value


class StudentEnrollSerializer(serializers.Serializer):
    class_id = serializers.CharField(max_length=36)
    academic_year_id = serializers.CharField(max_length=36)


class StudentPromoteSerializer(serializers.Serializer):
    target_class_id = serializers.CharField(max_length=36)