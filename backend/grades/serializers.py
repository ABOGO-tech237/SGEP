from rest_framework import serializers


class GradeSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    student_id = serializers.CharField()
    subject_id = serializers.CharField()
    period_id = serializers.CharField(source="sequence")
    value = serializers.FloatField()
    coefficient = serializers.FloatField(required=False, allow_null=True)
    comments = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class GradeCreateSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    subject_id = serializers.CharField()
    period_id = serializers.CharField()
    value = serializers.FloatField()
    coefficient = serializers.FloatField(required=False, allow_null=True)
    comments = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_value(self, value):
        if value < 0 or value > 20:
            raise serializers.ValidationError("La note doit être entre 0 et 20.")
        return value


class BulkGradeCreateSerializer(serializers.Serializer):
    grades = GradeCreateSerializer(many=True)
