from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .models import User, Follow
from recipes.short_serializers import RecipeShortSerializer


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields: tuple[str, ...] = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверяет подписку текущего пользователя на автора."""

        request = self.context.get('request')

        return bool(
            request
            and request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user,
                author=obj,
            ).exists()
        )


class SubscriptionSerializer(UserSerializer):
    """Сериализатор информации об авторе подписки."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields: tuple[str, ...] = (
            *UserSerializer.Meta.fields,
            'recipes_count',
            'recipes',
        )

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

                if limit > 0:
                    recipes = recipes[:limit]

        serializer = RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context,
        )
        return serializer.data


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор создания и проверки подписки."""

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, attrs):
        """Проверяет возможность подписки на автора."""

        user = attrs['user']
        author = attrs['author']

        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )

        if Follow.objects.filter(
            user=user,
            author=author,
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.'
            )

        return attrs

    def to_representation(self, instance):
        """Возвращает информацию об авторе подписки."""

        return SubscriptionSerializer(
            instance.author,
            context=self.context,
        ).data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для загрузки аватара пользователя."""

    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)
