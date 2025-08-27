import logging

from celery.result import (
    AsyncResult,
)
from django.core.cache import (
    cache,
)
from django.utils.functional import (
    cached_property,
)

from educommon.async_tasks.exceptions import (
    TaskUniqueException,
)


# по-умолчанию задача считается уникальной в течении
DEFAULT_LOCK_EXPIRE = 30 * 60


class TaskLocker:
    """Класс, отвечающий за блокировку задач"""

    # формат ключа в кэше
    lock_id_format = 'async-{task_name}_{params}'
    DEFAULT_LOCK_MSG = 'Задача уже выполняется или находится в очереди!'

    # параметры блокировки
    task_name = ''
    params = {}
    task_id = None
    expire_on = DEFAULT_LOCK_EXPIRE

    def __init__(
        self,
        task_name='',
        params={},
        task_id=None,
        expire_on=DEFAULT_LOCK_EXPIRE,
    ):
        self.task_name = task_name
        self.params = params
        self.task_id = task_id
        self.expire_on = expire_on

    def debug(self, *args, **kwargs):
        logger = logging.getLogger('educommon.async')
        logger.debug(*args, **kwargs)

    @cached_property
    def lock_id(self) -> str:
        """Ключ в кэше."""
        str_params = [f'{k}={v}' for k, v in self.params.items()]
        return self.lock_id_format.format(task_name=self.task_name, params='&'.join(str_params))

    def acquire_lock(self) -> None:
        """Установка блокировки."""
        value = self.task_id or 'true'
        cache.set(self.lock_id, value, self.expire_on)
        self.debug(f'Lock acquired for Task {self.task_name} ({self.params}) with value: {value}')

    def delete_lock(self) -> None:
        """Удаление блокировки."""
        cache.delete(self.lock_id)

    @staticmethod
    def delete_lock_by_id(lock_id: str) -> None:
        """Удаление блокировки по ключу.

        :param lock_id: ключ
        """
        cache.delete(lock_id)

    def is_locked(self) -> bool:
        """Заблокировано."""
        is_locked = False

        value = cache.get(self.lock_id)

        if value:
            is_locked = True
            if value != 'true':
                # значит в value должен быть task_id предыдущей задачи
                # и по нему пытаемся определить её статус
                prev_task_id = value
                async_result = AsyncResult(prev_task_id)
                if async_result.ready():
                    # задача есть, но она уже завершилась - снимаем блокировку
                    self.delete_lock()
                    is_locked = False

        return is_locked

    def raise_if_locked(self, message=None):
        """Если блокировано вызывает исключение.

        :raises: educommon.async_task.exceptions.TaskUniqueException
        """
        if self.is_locked():
            self.debug(f'Add failed. Task {self.task_name} currently locked ({self.params})')
            raise TaskUniqueException(message or self.DEFAULT_LOCK_MSG)
