from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .models import Follow, User
from .serializers import AvatarSerializer, SubscriptionSerializer


class SubscribeView(APIView):
    """Создание и удаление подписки на автора."""

    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """Подписаться на автора."""
        author = get_object_or_404(User, id=id)
        if request.user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Follow.objects.create(
            user=request.user,
            author=author,
        )

        serializer = SubscriptionSerializer(
            author,
            context={'request': request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, id):
        """Отписаться от автора."""
        author = get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(
            user=request.user,
            author=author,
        )

        if not subscription.exists():
            return Response(
                {'errors': 'Вы не подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionListView(ListAPIView):
    """Список подписок текущего пользователя."""

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Авторы, на которых подписан пользователь."""
        return User.objects.filter(
            subscribers__user=self.request.user,
        )


class AvatarView(APIView):
    """Загрузка и удаление аватара пользователя."""

    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Загрузить или заменить аватар."""
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        """Удалить аватар."""
        user = request.user

        if user.avatar:
            user.avatar.delete(save=True)

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
