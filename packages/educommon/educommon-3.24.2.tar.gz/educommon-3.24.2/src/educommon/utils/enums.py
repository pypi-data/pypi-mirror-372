from enum import (
    Enum,
)
from functools import (
    lru_cache,
)

from m3.db import (
    BaseEnumerate,
)


class NamedIntEnum(Enum):

    """Базовый класс для набора пар число + строка.

    Пример использования:
    .. code-block:: python
        class Status(NamedIntEnum):

            NEW = (1, 'Новый')
            PROGRESS = (2, 'В процессе')
            CLOSED = (3, 'Закрыт')

    """

    def __init__(self, id_: int, verbose: str) -> None:
        self.id = id_
        self.verbose = verbose

    @classmethod
    @lru_cache(maxsize=1)
    def get_choices(cls) -> tuple[tuple[int, str], ...]:
        return tuple((value.id, value.verbose) for value in cls)

    def as_dict(self, *, verbose_field: str = 'verbose'):
        return {
            'id': self.id,
            verbose_field: self.verbose,
        }


class HashGostFunctionVersion(BaseEnumerate):
    """ГОСТ версия функции хеширования."""

    GOST12_256 = 'md_gost12_256'
    GOST12_512 = 'md_gost12_512'
