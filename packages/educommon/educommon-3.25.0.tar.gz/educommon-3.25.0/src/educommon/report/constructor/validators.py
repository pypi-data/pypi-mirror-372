from django.core.exceptions import (
    ValidationError,
)

from educommon.report.constructor.registries import (
    registry,
)


def validate_data_source_name(value):
    """Валидатор для имен источников данных.

    Источник данных должен быть зарегистрирован в реестре.
    """
    if value not in registry:
        raise ValidationError('Источник данных "{}" не существует.'.format(value))
