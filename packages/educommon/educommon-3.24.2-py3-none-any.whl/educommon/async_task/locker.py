from typing import (
    Optional,
)

from celery.result import (
    AsyncResult,
)
from django.core.cache import (
    cache,
)
from django.utils.functional import (
    cached_property,
)

from educommon.async_task.exceptions import (
    TaskUniqueException,
)
from educommon.logger import (
    debug,
)
from educommon.utils.conversion import (
    uuid_or_none,
)


# по-умолчанию задача считается уникальной в течение
DEFAULT_LOCK_EXPIRE = 30 * 60


class TaskLocker:
    """Класс, отвечающий за блокировку задач."""

    # формат ключа в кэше
    lock_id_format = 'async_task:lock:{task_name}_{params}'

    DEFAULT_LOCK_MSG = 'Задача уже выполняется или находится в очереди!'
    DEFAULT_LOCK_VALUE = 'value'

    debug = debug

    def __init__(
        self,
        task_name: str = '',
        params: Optional[dict] = None,
        task_id: Optional[str] = None,
        expire_on: Optional[int] = None,
    ):
        self.task_name = task_name
        self.task_id = task_id
        self.params = params if params is not None else {}
        self.expire_on = expire_on if expire_on is not None else DEFAULT_LOCK_EXPIRE

    @cached_property
    def lock_id(self) -> str:
        """Ключ в кэше."""
        return self.lock_id_format.format(
            task_name=self.task_name, params='&'.join(f'{k}={v}' for k, v in self.params.items())
        )

    def acquire_lock(self) -> str:
        """Установка блокировки."""
        value = self.task_id or self.DEFAULT_LOCK_VALUE
        cache.set(self.lock_id, value, self.expire_on)
        self.debug(f'Lock acquired for Task {self.task_name} ({self.params}) with value: {value}')

        return self.lock_id

    def delete_lock(self) -> None:
        """Удаление блокировки."""
        cache.delete(self.lock_id)

    @staticmethod
    def delete_lock_by_id(lock_id: str) -> bool:
        """Удаление блокировки по ключу.

        :param lock_id: ключ
        """
        return cache.delete(lock_id)

    def is_locked(self) -> bool:
        """Установлена ли блокировка."""
        is_locked = False

        value = cache.get(self.lock_id)

        if value:
            is_locked = True

            # Возможна ситуация, когда задача по которой была выставлена блокировка
            # завершила свою работу, при этом блокировка не была снята. Поэтому проверяем
            # статус задачи по которой выставлялась блокировка:
            if value != self.DEFAULT_LOCK_VALUE and uuid_or_none(value):
                # значит в value должен быть task_id предыдущей задачи и по нему пытаемся определить её статус
                async_result = AsyncResult(value)
                if async_result and async_result.ready():
                    # задача есть, но она уже завершилась - снимаем блокировку
                    self.delete_lock()
                    is_locked = False

        return is_locked

    def raise_if_locked(self, message: Optional[str] = None):
        """Если блокировано, то вызывает исключение.

        :raises: educommon.async_task.exceptions.TaskUniqueException
        """
        if self.is_locked():
            self.debug(f'Add failed. Task {self.task_name} currently locked ({self.params})')

            raise TaskUniqueException(message or self.DEFAULT_LOCK_MSG)
