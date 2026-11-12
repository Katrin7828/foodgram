from django.db import transaction
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from users.serializers import UserSerializer

from .models import (Favorite, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)
from .short_serializers import RecipeShortSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов с количеством."""

    id = serializers.IntegerField(
        source='ingredient.id',
        read_only=True,
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True,
    )
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное."""

        request = self.context.get('request')

        return bool(
            request and request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в список покупок."""

        request = self.context.get('request')

        return bool(
            request and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        )


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов при записи рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования рецептов."""

    ingredients = IngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField(
        required=True,
        allow_null=False,
        allow_empty_file=False,
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, attrs):
        """Проверяет ингредиенты и теги рецепта."""

        ingredients = attrs.get('ingredients')
        tags = attrs.get('tags')

        if ingredients is None:
            raise serializers.ValidationError({
                'ingredients': 'Это поле обязательно.'
            })

        if tags is None:
            raise serializers.ValidationError({
                'tags': 'Это поле обязательно.'
            })

        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Добавьте хотя бы один ингредиент.'
            })

        if not tags:
            raise serializers.ValidationError({
                'tags': 'Добавьте хотя бы один тег.'
            })

        ingredient_ids = set()

        for item in ingredients:
            ingredient_id = item['ingredient'].id

            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты не должны повторяться.'
                })

            ingredient_ids.add(ingredient_id)

        tag_ids = set()

        for tag in tags:
            if tag.id in tag_ids:
                raise serializers.ValidationError({
                    'tags': 'Теги не должны повторяться.'
                })

            tag_ids.add(tag.id)

        return attrs

    @staticmethod
    def save_ingredients(recipe, ingredients_data):
        """Создаёт связи рецепта с ингредиентами."""

        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=item['ingredient'],
                    amount=item['amount'],
                )
                for item in ingredients_data
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        """Создаёт рецепт, теги и ингредиенты."""

        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        author = self.context['request'].user

        recipe = Recipe.objects.create(
            author=author,
            **validated_data,
        )

        recipe.tags.set(tags_data)
        self.save_ingredients(recipe, ingredients_data)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт, теги и ингредиенты."""

        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        instance = super().update(
            instance,
            validated_data,
        )

        instance.tags.set(tags_data)

        instance.recipeingredient_set.all().delete()
        self.save_ingredients(instance, ingredients_data)

        return instance

    def to_representation(self, instance):
        """Возвращает рецепт в полном формате."""

        return RecipeReadSerializer(
            instance,
            context=self.context,
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def validate(self, attrs):
        """Проверка повторного добавления рецепта."""

        if Favorite.objects.filter(
            user=attrs['user'],
            recipe=attrs['recipe'],
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )

        return attrs

    def to_representation(self, instance):
        """Возвращает краткую информацию о рецепте."""

        return RecipeShortSerializer(
            instance.recipe,
            context=self.context,
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в корзину покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)

    def validate(self, attrs):
        """Проверяет, что рецепт ещё не добавлен в корзину."""

        if ShoppingCart.objects.filter(
            user=attrs['user'],
            recipe=attrs['recipe'],
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок.'
            )

        return attrs

    def to_representation(self, instance):
        """Возвращает краткую информацию о рецепте."""

        return RecipeShortSerializer(
            instance.recipe,
            context=self.context,
        ).data
