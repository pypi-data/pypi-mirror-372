import logging
from typing import (
    Optional,
)

from django.http import (
    HttpRequest,
)

from educommon.logger.consts import (
    LEVEL_LOGGER_MAP,
)


def get_logger_method(
    level: str,
):
    """
    Функция получения метода логирования указанного уровня логирования.
    """
    logger_name, log_method = LEVEL_LOGGER_MAP[level]

    logger = logging.getLogger(logger_name)

    return getattr(logger, log_method)


def get_session_info(
    request: Optional[HttpRequest],
):
    """
    Возвращает строку для лога с информацией о запросе.

    Формат строки с пользователем:
        'URL: {uri} ({http_method}) - {username}, {email}, {FIO}. '

    Формат строки без пользователя:
        'URL: {uri} ({http_method}). '

    :param request: Http-запрос
    :type request: HttpRequest
    :return: Строка с информацией о запросе
    :rtype: basestring
    """
    session_info = ''

    if isinstance(request, HttpRequest):
        # Адрес запроса:
        url_info = f'URL: {request.get_full_path()} ({request.method})'

        # Информация о пользователе:
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            user_info = f' - {user.get_username()}, {user.email}, {user.get_full_name()}'
        else:
            user_info = ''

        session_info = f'{url_info}{user_info}. '

    return session_info
