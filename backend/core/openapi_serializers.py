from __future__ import annotations

from rest_framework import serializers

from accounts.serializers import AdminDashboardSerializer
from students.serializers import StudentListSerializer


class MessageResponseSerializer(serializers.Serializer):
	detail = serializers.CharField()


class JobIdResponseSerializer(serializers.Serializer):
	job_id = serializers.CharField()


class TokenResponseSerializer(serializers.Serializer):
	access_token = serializers.CharField()
	refresh_token = serializers.CharField(required=False)


class AccessTokenResponseSerializer(serializers.Serializer):
	access_token = serializers.CharField()


class FinanceDashboardResponseSerializer(serializers.Serializer):
	total_billed = serializers.FloatField()
	total_collected = serializers.FloatField()
	recovery_rate = serializers.FloatField()
	overdue_count = serializers.IntegerField()


class InvoiceGenerateResponseSerializer(serializers.Serializer):
	created = serializers.IntegerField()


class ReportCardStatusResponseSerializer(serializers.Serializer):
	status = serializers.CharField(help_text="pending, completed, failed, not_found, …")
	progress = serializers.IntegerField()
	file_path = serializers.CharField(required=False, allow_blank=True)


class ReportJobStatusResponseSerializer(serializers.Serializer):
	job_id = serializers.CharField()
	status = serializers.CharField()
	progress = serializers.IntegerField()
	file_path = serializers.CharField(required=False, allow_blank=True)
	error = serializers.CharField(required=False, allow_blank=True)
	type = serializers.CharField(required=False, allow_blank=True)


class ParentProfileResponseSerializer(serializers.Serializer):
	id = serializers.CharField()
	email = serializers.CharField()
	account_status = serializers.CharField()
	student_id = serializers.CharField(required=False, allow_null=True)


class StudentListPaginatedResponseSerializer(serializers.Serializer):
	items = StudentListSerializer(many=True)
	total = serializers.IntegerField()
	page = serializers.IntegerField()
	page_size = serializers.IntegerField()


class StudentHistoryResponseSerializer(serializers.Serializer):
	student_id = serializers.CharField()
	history = serializers.ListField(child=serializers.DictField())


class GuardianInputSerializer(serializers.Serializer):
	first_name = serializers.CharField()
	last_name = serializers.CharField()
	relationship = serializers.CharField()
	phone = serializers.CharField()
	phone2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	email = serializers.EmailField()


class StudentCreateRequestSerializer(serializers.Serializer):
	"""Schéma OpenAPI pour POST /students/ — reflète les champs attendus à la création."""

	first_name = serializers.CharField(max_length=100)
	last_name = serializers.CharField(max_length=100)
	matricule = serializers.CharField(
		max_length=50,
		help_text=(
			"Identifiant élève. Peut être omis ou laissé vide à la création : "
			"le serveur génère alors un matricule unique (format STU-AA-XXXXXX)."
		),
	)
	birth_date = serializers.CharField(help_text="Date de naissance (ISO 8601).")
	birth_place = serializers.CharField(max_length=100)
	gender = serializers.CharField(max_length=10)
	class_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
	academic_year_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
	id_number = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
	school_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
	is_active = serializers.BooleanField(required=False)
	medical = serializers.JSONField(required=False, allow_null=True)
	guardians = GuardianInputSerializer(many=True, required=False)


class ApiErrorResponseSerializer(serializers.Serializer):
	success = serializers.BooleanField(default=False)
	error = serializers.DictField(
		child=serializers.CharField(),
		help_text="Contient message et éventuellement details (validation).",
	)


AdminDashboardAccountsResponseSerializer = AdminDashboardSerializer
