from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .serializers import (
    AvatarSerializer,
    FollowSerializer,
    SubscriptionSerializer,
)


class FoodgramUserViewSet(UserViewSet):
    """Представление для пользователей, подписок и аватара."""

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        """Получить данные текущего пользователя."""

        return super().me(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe',
    )
    def subscribe(self, request, id=None):
        """Подписаться на автора."""

        author = self.get_object()

        serializer = FollowSerializer(
            data={
                'user': request.user.pk,
                'author': author.pk,
            },
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Отписаться от автора."""

        author = self.get_object()

        deleted_count, _ = Follow.objects.filter(
            user=request.user,
            author=author,
        ).delete()

        if not deleted_count:
            return Response(
                {'errors': 'Вы не подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        """Получить список авторов, на которых подписан пользователь."""

        authors = User.objects.filter(
            subscribers__user=request.user,
        )
        page = self.paginate_queryset(authors)

        serializer = SubscriptionSerializer(
            page,
            many=True,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        """Загрузить или заменить аватар."""

        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удалить аватар пользователя."""

        user = request.user

        if user.avatar:
            user.avatar.delete(save=True)

        return Response(status=status.HTTP_204_NO_CONTENT)
