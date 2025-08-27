from django.db import (
    models,
)
from m3_django_compat import (
    AUTH_USER_MODEL,
)


class ResetPasswords(models.Model):
    """Сброшенные пароли."""

    user = models.ForeignKey(
        AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    code = models.CharField(
        'Код восстановления',
        max_length=32,
        unique=True,
    )
    date = models.DateTimeField(
        'Дата сброса пароля',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Сброшенный пароль'
        verbose_name_plural = 'Сброшенные пароли'
