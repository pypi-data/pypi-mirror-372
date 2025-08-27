import django
import logging

from educommon.logger.helpers import (
    get_logger_method,
)
from educommon.logger.loggers import (
    WebEduLogger,
)


if django.VERSION < (3, 2):
    default_app_config = 'educommon.logger.apps.EduLoggerConfig'

# Переопределение класса логера
logging.setLoggerClass(WebEduLogger)

__all__ = ['debug', 'info', 'warning', 'error', 'rest_error', 'exception', 'default_app_config']


debug = get_logger_method(level='DEBUG')
info = get_logger_method(level='INFO')
warning = get_logger_method(level='WARNING')
error = get_logger_method(level='ERROR')
exception = get_logger_method(level='EXCEPTION')


def rest_error(msg, *args, **kwargs):
    """Логер REST-запросов."""
    log = logging.getLogger('rest_error_logger')

    msg = f'URL: {kwargs.get("path", None)} \n {msg}'

    log.error(msg)
