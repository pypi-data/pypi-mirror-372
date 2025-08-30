from contextlib import (
    closing,
)

from django.db import (
    connections,
)
from django.db.utils import (
    ProgrammingError,
)


def is_extension_exists(alias, name):
    """Возвращает True, если в БД доступно расширение с указанным именем.

    :param str alias: Алиас базы данных (напр. ``'default'``).
    :param str name: Имя расширения.

    :rtype: bool
    """
    with closing(connections[alias].cursor()) as cursor:
        cursor.execute('SELECT 1 FROM pg_extension WHERE extname = %s', (name,))
        return cursor.fetchone() is not None


def create_extension(alias, name, quite=False):
    """Создает в БД расширение PostgreSQL.

    :param str alias: Алиас базы данных (напр. ``'default'``).
    :param str name: Имя расширения.
    :param bool quite: Флаг, указывающий на необходимость генерации исключения
        при невозможности создания расширения (отсутствии соответствующих
        прав).

    :returns: ``True``, если расширение было успешно создано.
    :rtype: bool
    """
    with closing(connections[alias].cursor()) as cursor:
        try:
            cursor.execute('CREATE EXTENSION {}'.format(name))
        except ProgrammingError:
            if quite:
                return False
            else:
                raise
        else:
            return True


class Lock:
    """Блокировка с помощью функции PostgreSQL ``pg_advisory_lock``.

    .. seealso::

       `Функции управления рекомендательными блокировками <https://postgrespro\
       .ru/docs/postgrespro/9.5/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS>`
    """

    def __init__(self, alias, key):
        """Инициализация экземпляра.

        :param str alias: Алиас базы данных.

        :param key: Идентификатор блокировки.
        :type key: str or int
        """
        assert alias in connections, alias

        self.alias = alias

        if isinstance(key, str):
            self.key = hash(key)
        else:
            self.key = int(key)

    @property
    def _connection(self):
        return connections[self.alias]

    def __enter__(self):
        with closing(self._connection.cursor()) as cursor:
            cursor.callproc('pg_try_advisory_lock', (self.key,))

    def __exit__(self, exc_type, exc_val, exc_tb):
        with closing(self._connection.cursor()) as cursor:
            cursor.callproc('pg_advisory_unlock', (self.key,))
