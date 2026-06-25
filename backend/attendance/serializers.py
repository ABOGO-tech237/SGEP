from __future__ import annotations

from rest_framework import serializers

from .repository import TYPE_TO_STATUS


class AttendanceSerializer(serializers.Serializer):
	id = serializers.CharField(read_only=True)
	student_id = serializers.CharField()
	class_id = serializers.CharField()
	date = serializers.CharField()
	status = serializers.CharField()
	reason = serializers.CharField(required=False, allow_blank=True)
	academic_year_id = serializers.CharField()
	recorded_by = serializers.CharField()
	created_at = serializers.CharField(read_only=True)
	updated_at = serializers.CharField(read_only=True)

	def to_representation(self, instance):
		data = super().to_representation(instance)
		status = data.get("status", "")
		reverse_map = {value: key for key, value in TYPE_TO_STATUS.items()}
		data["type"] = reverse_map.get(status, status.lower())
		data["motif"] = data.pop("reason", "")
		return data


class AttendanceCreateSerializer(serializers.Serializer):
	student_id = serializers.CharField()
	class_id = serializers.CharField()
	date = serializers.CharField()
	type = serializers.ChoiceField(choices=["absence", "retard"])
	motif = serializers.CharField(required=False, allow_blank=True, default="")
	academic_year_id = serializers.CharField()

	def validate_type(self, value: str) -> str:
		if value not in TYPE_TO_STATUS:
			raise serializers.ValidationError("Le type doit être 'absence' ou 'retard'.")
		return value


class AttendanceUpdateSerializer(serializers.Serializer):
	student_id = serializers.CharField(required=False)
	class_id = serializers.CharField(required=False)
	date = serializers.CharField(required=False)
	type = serializers.ChoiceField(choices=["absence", "retard"], required=False)
	motif = serializers.CharField(required=False, allow_blank=True)
	academic_year_id = serializers.CharField(required=False)


class JustifySerializer(serializers.Serializer):
	motif = serializers.CharField()


class AttendanceStatsSerializer(serializers.Serializer):
	student_id = serializers.CharField()
	absences = serializers.IntegerField()
	retards = serializers.IntegerField()
	justified = serializers.IntegerField()
	rate = serializers.FloatField()
