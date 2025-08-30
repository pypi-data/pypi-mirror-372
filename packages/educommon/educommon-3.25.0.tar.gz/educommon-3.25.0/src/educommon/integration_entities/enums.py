from m3.db import (
    BaseEnumerate,
)


class EntityLogOperation(BaseEnumerate):
    """Действие по отслеживаемым данным."""

    CREATE = 1
    UPDATE = 2
    DELETE = 3

    values = {
        CREATE: 'Создание',
        UPDATE: 'Изменение',
        DELETE: 'Удаление',
    }
