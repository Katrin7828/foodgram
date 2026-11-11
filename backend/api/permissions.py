from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Разрешает чтение всем, изменение — только автору."""

    def has_permission(self, request, view):
        """Проверка общих прав доступа."""

        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Права доступа к определенному рецепту."""

        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
