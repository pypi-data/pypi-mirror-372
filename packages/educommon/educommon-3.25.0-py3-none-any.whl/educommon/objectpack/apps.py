from django.apps import (
    AppConfig,
)


class EduObjectPackConfig(AppConfig):
    """Конфигурация приложения educommon.objectpack.

    Определяет имя, метку и читаемое имя Django-приложения,
    содержащего расширения и дополнения к objectpack.
    """

    name = 'educommon.objectpack'
    label = 'educommon_objectpack'
    verbose_name = 'Набор дополнений к objectpack'
