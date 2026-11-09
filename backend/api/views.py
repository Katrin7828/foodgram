from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.http import HttpResponse
from django.db.models import Sum

from recipes.models import (
    Ingredient, Tag, Recipe, Favorite, ShoppingCart, RecipeIngredient)
from recipes.serializers import (
    IngredientSerializer, TagSerializer,
    RecipeReadSerializer, RecipeWriteSerializer)
from recipes.short_serializers import RecipeShortSerializer
from .permissions import IsAuthorOrReadOnly


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """Получение игредиентов."""
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')

        if name is not None:
            queryset = queryset.filter(name__istartswith=name)

        return queryset


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        """Возвращает рецепты с учётом фильтрации по автору."""

        queryset = Recipe.objects.all()
        author = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )

        if author is not None:
            queryset = queryset.filter(author_id=author)

        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        if is_favorited == '1':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(
                    favorite__user=self.request.user
                )
            else:
                queryset = queryset.none()

        if is_in_shopping_cart == '1':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(
                    shoppingcart__user=self.request.user
                )
            else:
                queryset = queryset.none()

        return queryset

    def get_serializer_class(self):
        """Определяет, с каким сериализатором работать."""

        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer

        return RecipeReadSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """Добавление и удаление рецепта из избранного."""

        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Рецепт уже добавлен в избранное.'
                )

            Favorite.objects.create(
                user=user,
                recipe=recipe,
            )
            serializer = RecipeShortSerializer(
                recipe,
                context={'request': request},
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                user=user,
                recipe=recipe,
            )

            if not favorite.exists():
                raise serializers.ValidationError(
                    'Рецепт не добавлен в избранное.'
                )
            favorite.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецепта из списка покупок."""

        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=user,
                recipe=recipe,
            ).exists():
                raise serializers.ValidationError(
                    'Рецепт уже добавлен в список покупок.'
                )
            ShoppingCart.objects.create(
                user=user,
                recipe=recipe,
            )

            serializer = RecipeShortSerializer(
                recipe,
                context={'request': request},
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == 'DELETE':
            shopping_cart = ShoppingCart.objects.filter(
                user=user,
                recipe=recipe,
            )

            if not shopping_cart.exists():
                raise serializers.ValidationError(
                    'Рецепта нет в списке покупок.'
                )

            shopping_cart.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""

        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user,
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')

        lines = ['Список покупок', '']
        for number, ingredient in enumerate(ingredients, start=1):
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            lines.append(f'{number}. {name} — {amount} {unit}')
        content = '\n'.join(lines)
        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8',
        )

        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response
