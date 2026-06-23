from __future__ import annotations

from rest_framework import serializers


class GradeSerializer(serializers.Serializer):
	id = serializers.CharField(read_only=True)
	student_id = serializers.CharField()
	subject_id = serializers.CharField()
	period_id = serializers.CharField()
	value = serializers.FloatField()
	coefficient = serializers.FloatField(read_only=True)
	academic_year_id = serializers.CharField(required=False, allow_blank=True)
	comments = serializers.CharField(required=False, allow_blank=True)
	recorded_by = serializers.CharField(read_only=True)
	created_at = serializers.CharField(read_only=True)
	updated_at = serializers.CharField(read_only=True)


class GradeCreateSerializer(serializers.Serializer):
	student_id = serializers.CharField()
	subject_id = serializers.CharField()
	period_id = serializers.CharField()
	value = serializers.FloatField(min_value=0, max_value=20)
	academic_year_id = serializers.CharField(required=False, allow_blank=True, default="")
	comments = serializers.CharField(required=False, allow_blank=True, default="")


class BulkGradeCreateSerializer(serializers.Serializer):
	grades = GradeCreateSerializer(many=True)


class ReportCardGenerateSerializer(serializers.Serializer):
	class_id = serializers.CharField()
	period_id = serializers.CharField()
	academic_year_id = serializers.CharField(required=False, allow_blank=True, default="")


class ReportCardSerializer(serializers.Serializer):
	id = serializers.CharField(read_only=True)
	student_id = serializers.CharField()
	academic_year_id = serializers.CharField()
	period_id = serializers.CharField()
	file_path = serializers.CharField(required=False, allow_blank=True)
	status = serializers.CharField()
	generated_at = serializers.CharField(required=False, allow_blank=True)

	def to_representation(self, instance):
		data = super().to_representation(instance)
		data["period_id"] = instance.get("sequence", data.get("period_id", ""))
		return data
