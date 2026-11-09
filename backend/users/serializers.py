from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)

from .models import User, Follow
from recipes.short_serializers import RecipeShortSerializer
from recipes.fields import Base64ImageField


USER_FIELDS = ['id', 'username', 'email', 'first_name', 'last_name']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [*USER_FIELDS, 'avatar', 'is_subscribed']

    def get_is_subscribed(self, obj):
        """Проверить подписку текущего пользователя на автора."""
        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            return False

        return Follow.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор регистрации пользователя."""

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = [*USER_FIELDS, 'password']


class SubscriptionSerializer(UserSerializer):
    """Сериализатор информации об авторе подписки."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def get_recipes_count(self, obj):
        """Вернуть количество рецептов автора."""
        return obj.recipe_set.count()

    def get_recipes(self, obj):
        """Вернуть рецепты автора с учётом ограничения."""
        recipes = obj.recipe_set.all()

        request = self.context.get('request')

        if request is not None:
            recipes_limit = request.query_params.get('recipes_limit')

            if recipes_limit is not None and recipes_limit.isdigit():
                limit = int(recipes_limit)
                recipes = recipes[:limit]

        serializer = RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context,
        )
        return serializer.data

    class Meta(UserSerializer.Meta):
        fields = [*UserSerializer.Meta.fields, 'recipes_count', 'recipes']


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для загрузки аватара пользователя."""

    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ['avatar']
