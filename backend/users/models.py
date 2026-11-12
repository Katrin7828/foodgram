from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q

from .constants import USER_LENGTH


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=USER_LENGTH)
    last_name = models.CharField(max_length=USER_LENGTH)
    avatar = models.ImageField(blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Подписки пользователей."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='subscribers')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'),
            models.CheckConstraint(
                condition=~Q(user=F('author')),
                name='prevent_self_follow')]

    def __str__(self):
        return f'{self.user}-{self.author}'
