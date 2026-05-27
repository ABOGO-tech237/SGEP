from __future__ import annotations

from rest_framework import serializers

from students.repository import StudentRepository


class ParentInputSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    relationship = serializers.CharField(max_length=50)
    phone = serializers.CharField(max_length=20)
    phone2 = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField()


class StudentBaseSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    matricule = serializers.CharField(max_length=50)
    birth_date = serializers.DateTimeField()
    birth_place = serializers.CharField(max_length=100)
    gender = serializers.CharField(max_length=10)
    id_number = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    medical = serializers.JSONField(required=False, allow_null=True)
    school_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
    class_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
    academic_year_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
    current_level_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField(required=False)


class StudentCreateSerializer(StudentBaseSerializer):
    parent = ParentInputSerializer(required=False)

    def validate_matricule(self, value: str) -> str:
        student_id = self.context.get("student_id")
        existing = StudentRepository.find_by_matricule(value, exclude_student_id=student_id)
        if existing:
            raise serializers.ValidationError("Ce matricule existe déjà.")
        return value

    def validate(self, attrs):
        if not self.partial and not attrs.get("parent"):
            raise serializers.ValidationError({"parent": "Les informations du parent sont requises."})
        return attrs


class StudentSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    matricule = serializers.CharField()
    birth_date = serializers.DateTimeField()
    birth_place = serializers.CharField()
    gender = serializers.CharField()
    id_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    medical = serializers.JSONField(required=False, allow_null=True)
    school_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    class_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    academic_year_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    current_level_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    parent_user_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField()
    is_deleted = serializers.BooleanField(required=False)
    created_at = serializers.CharField(required=False)
    updated_at = serializers.CharField(required=False)


class StudentListSerializer(serializers.Serializer):
    id = serializers.CharField()
    matricule = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    class_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    academic_year_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    current_level_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField()


class StudentEnrollSerializer(serializers.Serializer):
    class_id = serializers.CharField(max_length=36)
    academic_year_id = serializers.CharField(max_length=36)


class StudentPromoteSerializer(serializers.Serializer):
    target_class_id = serializers.CharField(max_length=36)


class StudentQuerySerializer(serializers.Serializer):
    class_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
    academic_year_id = serializers.CharField(max_length=36, required=False, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    search = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)