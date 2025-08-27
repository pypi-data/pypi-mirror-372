from abc import (
    ABCMeta,
    abstractmethod,
)


class IConfig(metaclass=ABCMeta):
    """Класс интерфейс для конфигурации менеджера логгеров веб-сервисов."""

    @property
    @abstractmethod
    def loggers(self):
        """Список логгеров Системы.

        :return: Кортеж из строк, содержащих полные наименования
            модулей (с наименованием пакета), содержащих класс логгера.
        :type: tuple of strings
        """


#: Конфигурация приложения ``ws_log``.
#:
#: Заполняется экземпляром класса :class:`ws_log.IConfig`, либо его
#: потомком, при инициализации проекта *до* инициализации приложения
#: ``ws_log``.
config = None
