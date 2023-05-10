from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Кастомный пермишн для проверки текущего пользователя"""

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj == user
