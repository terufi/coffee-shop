from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Читать каталог может любой авторизованный, менять только админ (is_staff)."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff