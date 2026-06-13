from __future__ import annotations

from rest_framework import serializers


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
	status = serializers.CharField()
	progress = serializers.IntegerField()
	file_path = serializers.CharField(required=False, allow_blank=True)


class ParentProfileResponseSerializer(serializers.Serializer):
	id = serializers.CharField()
	email = serializers.CharField()
	account_status = serializers.CharField()
	student_id = serializers.CharField(required=False, allow_null=True)


class ParentMessageCreateSerializer(serializers.Serializer):
	subject = serializers.CharField()
	body = serializers.CharField()
