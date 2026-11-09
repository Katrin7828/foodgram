from django.db import transaction
from rest_framework import serializers

from users.serializers import UserSerializer

from .fields import Base64ImageField
from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


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
        fields = ['id', 'name', 'measurement_unit', 'amount']


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

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное."""

        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            return False

        return Favorite.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, находится ли рецепт в списке покупок."""

        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            return False

        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()

    class Meta:
        model = Recipe
        fields = [
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
        ]


class IngredientWriteSerializer(serializers.Serializer):
    """Сериализатор ингредиентов при записи рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(min_value=1)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования рецептов."""

    ingredients = IngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        ]

    def validate_ingredients(self, value):
        """Проверяет наличие ингредиентов и отсутствие повторений."""

        if not value:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )
        ingredient_ids = set()

        for item in value:
            ingredient_id = item['id'].id

            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
            ingredient_ids.add(ingredient_id)

        return value

    def validate_tags(self, value):
        """Проверяет наличие тегов и отсутствие повторений."""

        if not value:
            raise serializers.ValidationError(
                'Добавьте хотя бы один тег.'
            )
        tag_ids = set()

        for tag in value:
            if tag.id in tag_ids:
                raise serializers.ValidationError(
                    'Теги не должны повторяться.'
                )
            tag_ids.add(tag.id)

        return value

    @staticmethod
    def save_ingredients(recipe, ingredients_data):
        """Создаёт связи рецепта с ингредиентами."""

        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=item['id'],
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

        ingredients_data = validated_data.pop(
            'ingredients',
            None,
        )
        tags_data = validated_data.pop(
            'tags',
            None,
        )
        instance = super().update(
            instance,
            validated_data,
        )

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()
            self.save_ingredients(instance, ingredients_data)

        return instance

    def to_representation(self, instance):
        """Возвращает созданный или обновлённый рецепт в полном формате."""

        return RecipeReadSerializer(
            instance,
            context=self.context,
        ).data
