from __future__ import annotations

from rest_framework import serializers


class SchoolSerializer(serializers.Serializer):
	id = serializers.CharField(read_only=True)
	name = serializers.CharField()
	code = serializers.CharField()
	address = serializers.CharField(required=False, allow_blank=True, default="")
	phone = serializers.CharField(required=False, allow_blank=True, default="")
	email = serializers.EmailField(required=False, allow_blank=True, default="")
	is_active = serializers.BooleanField(default=True)


class AcademicYearSerializer(serializers.Serializer):
	id = serializers.CharField(read_only=True)
	name = serializers.CharField()
	start_date = serializers.CharField()
	end_date = serializers.CharField()
	school_id = serializers.CharField(required=False, allow_blank=True, default="")
	is_active = serializers.BooleanField(default=False)


class AdminDashboardStatSerializer(serializers.Serializer):
	label = serializers.CharField()
	value = serializers.CharField()
	change = serializers.CharField()
	positive = serializers.BooleanField(allow_null=True)


class AdminDashboardActivitySerializer(serializers.Serializer):
	id = serializers.CharField()
	name = serializers.CharField()
	action = serializers.CharField()
	grade = serializers.CharField()
	status = serializers.CharField()
	time = serializers.CharField()


class AdminDashboardResponseSerializer(serializers.Serializer):
	generated_at = serializers.CharField()
	academic_year = serializers.DictField(allow_null=True, required=False)
	stats = AdminDashboardStatSerializer(many=True)
	finance = serializers.DictField()
	recent_activity = AdminDashboardActivitySerializer(many=True)
