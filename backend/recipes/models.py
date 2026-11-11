import secrets
import string

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


INGREDIENT_LENGTH = 128
MEASUREMENT_LENGTH = 64
TAG_LENGTH = 32
RECIPE_LENGTH = 256
CODE_LENGTH = 10
SHORT_CODE_LENGTH = 6
MIN_AMOUNT = 1
MAX_COOKING_TIME = 32000


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(max_length=INGREDIENT_LENGTH)
    measurement_unit = models.CharField(max_length=MEASUREMENT_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_measurement_unit',
            )
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(max_length=TAG_LENGTH, unique=True)
    slug = models.SlugField(max_length=TAG_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=RECIPE_LENGTH)
    image = models.ImageField(blank=False)
    text = models.TextField()
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_COOKING_TIME),
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    short_code = models.CharField(
        max_length=CODE_LENGTH,
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name

    @staticmethod
    def generate_short_code():
        """Генерирует уникальный короткий код рецепта."""

        alphabet = string.ascii_letters + string.digits

        while True:
            code = ''.join(
                secrets.choice(alphabet)
                for _ in range(SHORT_CODE_LENGTH)
            )

            if not Recipe.objects.filter(short_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        """Создаёт короткий код при первом сохранении рецепта."""

        if self._state.adding and not self.short_code:
            self.short_code = self.generate_short_code()

        super().save(*args, **kwargs)


class RecipeIngredient(models.Model):
    """Промежуточная модель между рецептом и ингредиентом."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe',
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name} — {self.amount}'


class Favorite(models.Model):
    """Избранные рецепты."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe',
            )
        ]

    def __str__(self):
        return f'{self.user} — {self.recipe}'


class ShoppingCart(models.Model):
    """Рецепты в списке покупок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_user_recipe',
            )
        ]

    def __str__(self):
        return f'{self.user} — {self.recipe}'
