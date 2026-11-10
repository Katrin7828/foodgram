from rest_framework.permissions import SAFE_METHODS
from djoser.permissions import CurrentUserOrAdmin


class PublicReadOnlyOrOwner(CurrentUserOrAdmin):
    """Публичный просмотр, изменение только владельцем или админом."""

    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return super().has_object_permission(request, view, obj)
