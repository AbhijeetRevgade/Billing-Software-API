from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Allows access only to users whose role is OWNER.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'OWNER'
        )


class IsStaff(BasePermission):
    """
    Allows access only to users whose role is STAFF.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'STAFF'
        )
