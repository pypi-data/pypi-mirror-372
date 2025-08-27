"""Конфигурация асинхронной сборки отчета."""

from abc import (
    ABCMeta,
    abstractmethod,
)


class ConstructorConfig(metaclass=ABCMeta):
    """Конфигурация конструктора отчетов."""

    @property
    @abstractmethod
    def async_task(self):
        """Асинхронная задача, в которой будет выполняться построение отчета.

        :rtype: :class:`celery.app.task.Task`
        """

    @property
    @abstractmethod
    def current_user_func(self):
        """Функция, возвращающая текущего пользователя."""


# : Конфигурация конструктора отчетов.
# :
# : В проекте, который использует конструктор отчетов, в этой переменной должен
# : быть сохранен экземпляр потомка класса :class:`
#  ~constructor.config.ConstructorConfig`.
report_constructor_config = None
