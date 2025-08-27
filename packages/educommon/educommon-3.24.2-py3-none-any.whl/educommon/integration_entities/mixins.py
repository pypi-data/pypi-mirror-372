from typing import (
    TYPE_CHECKING,
    List,
)

from m3_django_compat import (
    classproperty,
)


if TYPE_CHECKING:
    from m3_db_utils.models import (
        ModelEnumValue,
    )


class EntitiesMixin:
    """
    Добавляет метод подготовки сущностей и свойства для доступа к ним.
    """

    # flake8: noqa: N805
    @classproperty
    def first_entity(cls) -> 'ModelEnumValue':
        """
        Возвращает первый ключ модели-перечисления сущностей.
        """
        return cls._prepare_entities()[0]

    # flake8: noqa: N805
    @classproperty
    def entities(cls) -> List['ModelEnumValue']:
        """
        Возвращает ключи модели-перечисления сущностей.
        """
        return cls._prepare_entities()

    @classmethod
    def _prepare_entities(cls) -> List['ModelEnumValue']:
        """
        Формирование списка ключей модели-перечисления сущностей.
        """
        return []
