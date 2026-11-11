from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.permissions import IsAuthorOrReadOnly
from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from recipes.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = (
        'get', 'post', 'patch', 'delete', 'head', 'options'
    )

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""

        if self.action in ('create', 'partial_update'):
            return RecipeWriteSerializer

        return RecipeReadSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""

        recipe = self.get_object()

        serializer = FavoriteSerializer(
            data={
                'user': request.user.pk,
                'recipe': recipe.pk,
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удаление рецепта из избранного."""

        recipe = self.get_object()

        deleted_count, _ = Favorite.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()

        if not deleted_count:
            raise serializers.ValidationError(
                'Рецепт не добавлен в избранное.'
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в список покупок."""

        recipe = self.get_object()

        serializer = ShoppingCartSerializer(
            data={
                'user': request.user.pk,
                'recipe': recipe.pk,
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удаление рецепта из списка покупок."""

        recipe = self.get_object()

        deleted_count, _ = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()

        if not deleted_count:
            raise serializers.ValidationError(
                'Рецепта нет в списке покупок.'
            )

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
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        lines = ['Список покупок', '']

        for number, ingredient in enumerate(ingredients, start=1):
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']

            lines.append(
                f'{number}. {name} — {amount} {unit}'
            )

        content = '\n'.join(lines)

        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8',
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""

        recipe = self.get_object()

        if not recipe.short_code:
            recipe.short_code = recipe.generate_short_code()
            recipe.save(update_fields=['short_code'])

        short_link = request.build_absolute_uri(
            f'/s/{recipe.short_code}/'
        )

        return Response({'short-link': short_link})


def redirect_to_recipe(request, short_code):
    """Перенаправляет с короткой ссылки на страницу рецепта."""

    recipe = get_object_or_404(Recipe, short_code=short_code)

    return HttpResponseRedirect(
        request.build_absolute_uri(f'/recipes/{recipe.id}/')
    )
