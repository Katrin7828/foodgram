from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    """Создаёт стандартные теги рецептов."""

    help = 'Загрузка стандартных тегов Foodgram'

    def handle(self, *args, **options):
        tags = (
            ('Завтрак', 'breakfast'),
            ('Обед', 'lunch'),
            ('Ужин', 'dinner'),
        )

        created_count = 0

        for name, slug in tags:
            _, created = Tag.objects.get_or_create(
                slug=slug,
                defaults={'name': name},
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Загрузка завершена. '
                f'Добавлено тегов: {created_count}'
            )
        )
