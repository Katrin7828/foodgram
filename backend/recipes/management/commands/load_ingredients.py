import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Загружает ингредиенты из JSON в базу данных."""

    help = 'Загрузка ингредиентов из data/ingredients.json'

    def handle(self, *args, **options):
        file_path = (
            Path('/data/ingredients.json')
            if Path('/data/ingredients.json').exists()
            else settings.BASE_DIR.parent / 'data' / 'ingredients.json'
        )

        if not file_path.is_file():
            raise CommandError(
                f'Файл с ингредиентами не найден: {file_path}'
            )

        with file_path.open(encoding='utf-8') as file:
            ingredients = json.load(file)

        created_count = 0

        for ingredient in ingredients:
            _, created = Ingredient.objects.get_or_create(
                name=ingredient['name'],
                measurement_unit=ingredient['measurement_unit'],
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Загрузка завершена. '
                f'Добавлено ингредиентов: {created_count}'
            )
        )
