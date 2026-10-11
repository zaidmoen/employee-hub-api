from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsAuthenticatedAndAdminWrite(BasePermission):
    """Allow signed-in users to read and staff users to change data."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff
