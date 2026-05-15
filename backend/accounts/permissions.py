from rest_framework.permissions import BasePermission

ROLE_SUPERADMIN = "superadmin"
ROLE_COMPTABLE = "comptable"
ROLE_PARENT = "parent"


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == ROLE_SUPERADMIN


class IsComptable(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in (ROLE_SUPERADMIN, ROLE_COMPTABLE)
        )


class IsActiveParent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == ROLE_PARENT
            and request.user.account_status == "active"
        )


class IsParentAny(BasePermission):
    """Acces parent meme si compte suspendu (factures, recus)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == ROLE_PARENT
