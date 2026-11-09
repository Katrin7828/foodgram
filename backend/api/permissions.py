from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Разрешает чтение всем, изменение — только автору."""

    def has_permission(self, request, view):
        """Проверка общих прав доступа."""

        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Права доступа к определенному рецепту."""

        if request.method in SAFE_METHODS:
            return True

        return obj.author == request.user
