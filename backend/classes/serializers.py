from __future__ import annotations

from rest_framework import serializers


class ClassSerializer(serializers.Serializer):
	id = serializers.CharField(read_only=True)
	name = serializers.CharField()
	level_id = serializers.CharField()
	academic_year_id = serializers.CharField()
	school_id = serializers.CharField(required=False, allow_blank=True, default="")
	capacity = serializers.IntegerField(required=False, allow_null=True)
	teacher_id = serializers.CharField(required=False, allow_blank=True, default="")


class SubjectSerializer(serializers.Serializer):
	id = serializers.CharField(read_only=True)
	name = serializers.CharField()
	code = serializers.CharField()
	coefficient = serializers.IntegerField(min_value=1)
	class_id = serializers.CharField(required=False, allow_blank=True, default="")
	level_id = serializers.CharField(required=False, allow_blank=True, default="")
