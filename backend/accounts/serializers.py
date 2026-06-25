from rest_framework import serializers

from accounts.models import ROLE_COMPTABLE, ROLE_PARENT, ROLE_SUPERADMIN


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=False)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=False)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(trim_whitespace=False, write_only=True)
    new_password = serializers.CharField(trim_whitespace=False, write_only=True)
    confirm_password = serializers.CharField(trim_whitespace=False, write_only=True)

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")

        if len(new_password or "") < 8:
            raise serializers.ValidationError(
                "Le nouveau mot de passe doit contenir au moins 8 caracteres."
            )

        return attrs


class BootstrapSerializer(serializers.Serializer):
    email = serializers.EmailField(default="admin@sgep.cm", required=False)
    password = serializers.CharField(
        default="AdminPassword123!",
        trim_whitespace=False,
        write_only=True,
        required=False,
    )
    role = serializers.ChoiceField(
        choices=[ROLE_SUPERADMIN, ROLE_COMPTABLE, ROLE_PARENT],
        default=ROLE_SUPERADMIN,
        required=False,
    )
    first_name = serializers.CharField(default="Admin", required=False)
    last_name = serializers.CharField(default="SGEP", required=False)

    def validate_password(self, value):
        if len(value or "") < 8:
            raise serializers.ValidationError(
                "Le mot de passe doit contenir au moins 8 caracteres."
            )
        return value


class AdminUserSummarySerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.EmailField()
    name = serializers.CharField(allow_blank=True)
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    role = serializers.CharField()
    account_status = serializers.CharField()
    created_at = serializers.CharField(allow_blank=True)
    updated_at = serializers.CharField(allow_blank=True)


class AdminDashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    suspended_users = serializers.IntegerField()
    superadmins = serializers.IntegerField()
    comptables = serializers.IntegerField()
    parents = serializers.IntegerField()
    recent_users = AdminUserSummarySerializer(many=True)
