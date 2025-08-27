"""Базовые классы для асинхронных задач."""

import logging
from collections import (
    OrderedDict,
)
from datetime import (
    datetime,
)

from celery import (
    Task,
    states,
)
from kombu import (
    uuid,
)

from educommon.async_tasks import (
    models,
    statuses,
)
from educommon.async_tasks.locks import (
    TaskLocker,
)


# DEPRECATED Не использовать!
# Вместо этого использовать приложение educommon.async_task
class AsyncTask(Task):
    """Базовый класс асинхронных задач."""

    abstract = True

    # описание (имя) асинх.задачи (отображается в реестре)
    description = None

    def debug(self, *args, **kwargs):
        """Логирование в debug-лог."""
        logger = logging.getLogger('educommon.async')
        logger.debug(*args, **kwargs)

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None, link=None, link_error=None, **options):
        """Постановка задачи в очередь.

        автор задачи задаётся снаружи через 2 поля в словаре kwargs:
            object_id и content_type
        """
        if kwargs is None:
            kwargs = {}

        async_result = super().apply_async(
            args=args, kwargs=kwargs, task_id=task_id, producer=producer, link=link, link_error=link_error, **options
        )

        location = self.__class__.__module__ + '.' + self.__class__.__name__
        task_meta = models.AsyncTaskMeta.objects.create(location=location, description=self.description)
        params = dict(
            task_meta=task_meta,
            status=statuses.STATUS_RECEIVED,
            object_id=kwargs.get('object_id'),
            content_type=kwargs.get('content_type'),
            task_type_id=kwargs.get('task_type', models.AsyncTaskType.TASK_UNKNOWN),
            # время начала задачи
            # для случая, когда celery успевает начать задачу ещё до
            # коммита в БД создаваемой здесь models.RunningTask
            queued_on=datetime.now(),
        )

        models.RunningTask.objects.get_or_create(task_id=async_result.task_id, defaults=params)

        self.debug(f'Task {self.__name__} added')

        return async_result

    def run(self, *args, **kwargs):
        """Выполнение задачи (отложенное)."""
        # начальное состояние задачи
        self.state = {
            # результаты задачи
            'values': OrderedDict(),
            # описание результата
            'description': self.description,
            # прогресс выполнения задачи
            'progress': 'Неизвестно',
        }
        self.update_state(state=statuses.get_state_str(statuses.STATUS_STARTED), meta=self.state)
        self.debug(f'Task {self.__name__} run (task_id = {self.request.id} )')

        return {}

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Завершение задачи."""
        self.debug(f'Task {self.__name__} completed')

        if isinstance(retval, dict):
            self.update_state(state=retval.get('task_state', status), meta=retval)
        else:
            self.update_state(state=status, meta=retval)

    def update_state(self, task_id=None, state=None, meta=None):
        """Обновленение модели при изменении состояния асинх. результата.

        :param str task_id: id задачи celery
        :param str task_state: состояние задачи celery (celery.states)
        :param meta: состояние метаданых (см. базовый класс в Celery).
        """
        if task_id is None:
            task_id = self.request.id

        running_task = models.RunningTask.objects.filter(task_id=task_id).order_by('queued_on').first()

        if not running_task:
            return

        if state == states.SUCCESS:
            self.state['values']['Время выполения'] = datetime.now() - running_task.queued_on

        super().update_state(task_id=task_id, state=state, meta=meta)

        running_task.status = statuses.get_status_idx(state)

        if state == states.STARTED:
            # если обновление статуса связано с переходом в состояние 'RUNNING'
            running_task.queued_on = datetime.now()
        running_task.clean_and_save()

    def set_progress(self, task_id=None, task_state=states.STARTED, progress=None, values=None):
        """Обновление состояния выполнения задачи.

        :param str task_id: id задачи celery
        :param str task_state: состояние задачи celery (celery.states)
        :param str progress: строковое описание состояния выполнения задачи
        :param dict values: значения задаваемые процедурой выполнения задачи
        """
        if task_id is None:
            task_id = self.request.id

        if progress:
            self.state['progress'] = progress
        if values:
            self.state['values'].update(values)
        self.backend.store_result(task_id, self.state, task_state)


class LockableAsyncTask(AsyncTask):
    """
    Базовый класс асинхронных задач с возможностью блокировки.

    Поддерживает блокировки. Блокировка не позволяет создать задачу
    с такими-же параметрами, пока не завершится существующая.

    >>>
    ...task = LockableAsyncTask()
    ...
    ...try:
    ...    async_result = task.apply_async(
    ...        args,
    ...        # kwargs доступные при выполнении
    ...        {'user_id': 1, 'context': context},
    ...        # параметры одновременного запуска
    ...        locker_config={
    ...            'lock_params': {'unit_id': 1745},
    ...            'lock_message': 'Для данной организации уже запущено!'
    ...        }
    ...    )
    ...except TaskUniqueException as e:
    ...    raise ApplicationLogicException(str(e))

    """

    abstract = True

    # класс отвечающий за невозможность одновременного запуска
    # задач по определенным критериям
    _locker_class = TaskLocker
    # параметры, определяющие блокировку задачи
    # можно определить для класса задач,
    # можно дополнить в apply_async (при постановке в очередь)
    _locker_config = {
        # словарь параметров, например {'unit_id': 1745}
        'lock_params': None,
        # текст сообщения об ошибке
        'lock_message': None,
        # время в сек., когда снимется блокировка незав-мо от завершения задачи
        'lock_expire': None,
    }

    # имя блокировки, используется как часть ключа.
    _lock_name = None

    @classmethod
    def _get_lock_name(cls):
        """Возвращает имя блокировки.

        По-умолчанию — имя класса.
        Используется как часть ключа блокировки.
        """
        return cls._lock_name or cls.__name__

    @classmethod
    def _handle_locks(cls, locks, task_id=None):
        """Проверка имеющейся блокировки или ее установка.

        :raises: educommon.async_task.exceptions.TaskUniqueException
        """
        lock_params = locks.get('lock_params')
        message = locks.get('lock_message')
        lock_expire = locks.get('lock_expire')

        # если параметров нет — блокировка не устанавливается.я
        if lock_params:
            # была определена уникальность задач
            locker = cls._locker_class(
                # имя блокировки
                cls._get_lock_name(),
                # параметры блокировки
                lock_params,
                # UUID задачи
                task_id,
                # время жизни
                lock_expire,
            )
            locker.raise_if_locked(message)

            locker.acquire_lock()

            return locker.lock_id

    def _validate_lock_data(self, lock_data):
        """Проверяет параметры блокировки.

        :raises: educommon.async_task.exceptions.TaskLockDataValidationError
        """
        pass

    def apply_async(self, args=None, kwargs={}, task_id=None, producer=None, link=None, link_error=None, **options):
        """Постановка в очередь.

        Для задач, реализующих уникальность, метод выбрасывает исключение.

        :raises: educommon.async_task.exceptions.TaskUniqueException
        """
        # параметры, определяющие блокировку, можно определить для конкретного
        # исполнения
        locker_config = options.pop('locker_config', None)
        self._validate_lock_data(locker_config)
        if locker_config:
            self._locker_config.update(locker_config)
            if not task_id:
                task_id = uuid()
        lock_id = self._handle_locks(self._locker_config, task_id=task_id)
        # для снятия блокирования после завершения задачи
        kwargs.update(lock_id=lock_id)

        async_result = super().apply_async(
            args=args, kwargs=kwargs, task_id=task_id, producer=producer, link=link, link_error=link_error, **options
        )

        return async_result

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Завершение задачи"""
        super().after_return(status, retval, task_id, args, kwargs, einfo)
        # снимаем блокировку
        lock_id = kwargs.get('lock_id')
        if lock_id:
            # задача завершена, убрать лок
            self.debug(f'Unlock task {self.__name__} lock_id = {lock_id}')
            self._locker_class.delete_lock_by_id(lock_id)
