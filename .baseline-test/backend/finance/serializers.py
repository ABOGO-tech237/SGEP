from __future__ import annotations

from rest_framework import serializers


class InvoiceSerializer(serializers.Serializer):
	id = serializers.CharField(read_only=True)
	number = serializers.CharField()
	student_id = serializers.CharField()
	academic_year_id = serializers.CharField()
	fee_type_id = serializers.CharField(required=False, allow_blank=True)
	amount = serializers.FloatField()
	status = serializers.CharField()
	due_date = serializers.CharField()


class InvoiceGenerateSerializer(serializers.Serializer):
	class_id = serializers.CharField(required=False, allow_blank=True)
	fee_type_id = serializers.CharField()
	academic_year_id = serializers.CharField()


class PaymentCreateSerializer(serializers.Serializer):
	invoice_id = serializers.CharField()
	amount = serializers.FloatField(min_value=0.01)
	method = serializers.CharField()
	reference = serializers.CharField(required=False, allow_blank=True, default="")


class PaymentSerializer(serializers.Serializer):
	id = serializers.CharField(read_only=True)
	invoice_id = serializers.CharField()
	amount = serializers.FloatField()
	method = serializers.CharField()
	reference = serializers.CharField(required=False, allow_blank=True)
	status = serializers.CharField()
	receipt_path = serializers.CharField(required=False, allow_blank=True)
