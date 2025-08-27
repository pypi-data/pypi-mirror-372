from django.utils.module_loading import (
    import_string,
)

from educommon.ws_log import (
    config as manager_config,
)
from educommon.ws_log.base import (
    DefaultWsApplicationLogger,
)


class LoggerManager:
    """Класс для работы с логгерами приложений веб-сервисов."""

    def __init__(self):
        self._ws_loggers = dict(default=DefaultWsApplicationLogger())

    @staticmethod
    def __import_logger_class(logger_path):
        """Импортирует класс логгера приложения веб-сервиса."""

        result = None
        if manager_config and logger_path in manager_config.loggers:
            try:
                result = import_string(logger_path)
            except ImportError:
                pass

        return result

    def get_application_logger(self, ws_app_name):
        """Возвращает логгер для приложения веб-сервиса.

        Если не был найден подходящий логгер, то возвращается по умолчанию.
        :param ws_app_name: Имя приложения веб-сервиса.
        :return: Логгер веб-сервиса.
        """

        logger = self._ws_loggers.get(ws_app_name, None)
        if not logger:
            logger_path = ws_app_name + '.logger.WsApplicationLogger'
            logger_class = self.__import_logger_class(logger_path)
            if logger_class:
                logger = logger_class()
                self._ws_loggers[ws_app_name] = logger
            else:
                logger = self._ws_loggers.get('default')

        return logger


logger_manager = LoggerManager()
