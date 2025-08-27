from abc import (
    abstractmethod,
)
from dataclasses import (
    dataclass,
)
from typing import (
    Tuple,
)


@dataclass
class BaseEntity:
    """
    Базовый дата-класс сущности РВД.

    Дата-классы сущностей предназначены для формирования объектов сущностей и дальнейшей трансформации данных для
    выгрузки.
    """

    # Проводимая операция с записью сущности
    operation: int
    # Id выгружаемой модели
    id: str

    @classmethod
    @abstractmethod
    def get_ordered_fields(cls) -> Tuple[str, ...]:
        """
        Возвращает кортеж полей в правильном порядке.
        """

    @classmethod
    @abstractmethod
    def get_primary_key_fields(cls) -> Tuple[str, ...]:
        """
        Возвращает кортеж полей первичного ключа.
        """

    @classmethod
    @abstractmethod
    def get_foreign_key_fields(cls) -> Tuple[str, ...]:
        """
        Возвращает кортеж полей внешних ключей.
        """
        return ()

    @classmethod
    @abstractmethod
    def get_required_fields(cls) -> Tuple[str, ...]:
        """
        Возвращает кортеж обязательных полей.
        """

    @classmethod
    @abstractmethod
    def get_hashable_fields(cls) -> Tuple[str, ...]:
        """
        Возвращает кортеж полей, которые необходимо деперсонализировать (хэшировать).
        """

    @classmethod
    def get_ignore_prefix_key_fields(cls) -> Tuple[str, ...]:
        """
        Возвращает кортеж из первичных и внешних ключей,
        которые должны быть проигнорированы при добавлении RDM_EXPORT_ENTITY_ID_PREFIX.
        """
        return ()
