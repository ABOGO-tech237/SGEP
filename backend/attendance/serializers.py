from rest_framework import serializers


class AttendanceQuerySerializer(serializers.Serializer):
    class_id = serializers.CharField(required=False, allow_blank=False)
    student_id = serializers.CharField(required=False, allow_blank=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)


class AttendanceSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    student_id = serializers.CharField()
    class_id = serializers.CharField()
    date = serializers.DateField()
    type = serializers.ChoiceField(choices=["absence", "retard"])
    motif = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_justified = serializers.BooleanField(required=False)
    justification_motif = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    justification_doc = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AttendanceCreateSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    class_id = serializers.CharField()
    date = serializers.DateField()
    type = serializers.ChoiceField(choices=["absence", "retard"])
    motif = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AttendanceUpdateSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)
    type = serializers.ChoiceField(choices=["absence", "retard"], required=False)
    motif = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AttendanceJustifySerializer(serializers.Serializer):
    motif = serializers.CharField()
    justification_doc = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AttendanceStatsQuerySerializer(serializers.Serializer):
    class_id = serializers.CharField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()


class AttendanceExportQuerySerializer(serializers.Serializer):
    class_id = serializers.CharField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    format = serializers.ChoiceField(choices=["pdf", "excel"])
