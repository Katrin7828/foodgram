import base64
import binascii
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Преобразует изображение из Base64 в файл Django."""

    def to_internal_value(self, data):
        """Обрабатывает входящее изображение."""

        if isinstance(data, str):
            if not data.startswith('data:image/'):
                raise serializers.ValidationError(
                    'Ожидается изображение в формате Base64.'
                )

            try:
                format_part, encoded_image = data.split(',', 1)
            except ValueError:
                raise serializers.ValidationError(
                    'Некорректный формат изображения.'
                )

            if not format_part.endswith(';base64'):
                raise serializers.ValidationError(
                    'Некорректный заголовок Base64.'
                )

            extension = format_part.split('/')[1].split(';')[0].lower()

            if extension == 'jpeg':
                extension = 'jpg'

            if extension not in ('jpg', 'png', 'gif', 'webp'):
                raise serializers.ValidationError(
                    'Неподдерживаемый формат изображения.'
                )

            try:
                image_data = base64.b64decode(
                    encoded_image,
                    validate=True,
                )
            except (ValueError, binascii.Error):
                raise serializers.ValidationError(
                    'Некорректное изображение в формате Base64.'
                )

            filename = f'{uuid.uuid4()}.{extension}'

            data = ContentFile(
                image_data,
                name=filename,
            )

        return super().to_internal_value(data)
