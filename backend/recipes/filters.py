from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтрация ингредиентов по началу названия."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтрация рецептов."""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = filters.NumberFilter(
        field_name='author_id',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_favorited(self, queryset, name, value):
        """Фильтрация по избранным рецептам."""

        user = self.request.user

        if not user.is_authenticated:
            return queryset.none() if value else queryset

        return queryset.filter(
            favorite__user=user,
        ) if value else queryset.exclude(
            favorite__user=user,
        )

    def filter_shopping_cart(self, queryset, name, value):
        """Фильтрация по списку покупок."""

        user = self.request.user

        if not user.is_authenticated:
            return queryset.none() if value else queryset

        return queryset.filter(
            shoppingcart__user=user,
        ) if value else queryset.exclude(
            shoppingcart__user=user,
        )
