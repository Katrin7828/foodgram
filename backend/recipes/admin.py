from django.contrib import admin

from .models import (
    Ingredient, Tag, Recipe,
    RecipeIngredient, Favorite, ShoppingCart,
)


admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка отображения ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 20


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка отображения рецептов."""

    list_display = ('id', 'name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    list_per_page = 20

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        """Возвращает количество добавлений рецепта в избранное."""
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка отображения тегов."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
