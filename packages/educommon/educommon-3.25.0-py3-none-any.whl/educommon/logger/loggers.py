import os
import platform
import sys
from logging import (
    addLevelName,
    getLoggerClass,
)
from typing import (
    Mapping,
    Optional,
)

from django.utils.encoding import (
    smart_str,
)
from packaging.version import (
    Version,
)

from educommon.logger.helpers import (
    get_session_info,
)
from educommon.logger.records import (
    WebEduLogRecord,
)


_srcfile = os.path.normcase(addLevelName.__code__.co_filename)


class WebEduLogger(getLoggerClass()):
    """Расширенный логер для работы с различными версиями Python."""

    def makeRecord(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: object,
        args,
        exc_info,
        func: Optional[str] = ...,
        extra: Optional[Mapping[str, object]] = ...,
        sinfo: Optional[str] = ...,
    ) -> WebEduLogRecord:
        """Метод формирования записи лога."""
        rv = WebEduLogRecord(name, level, fn, lno, msg, args, exc_info, func)

        if extra:
            for key in extra:
                if (key in ['message', 'asctime']) or (key in rv.__dict__):
                    raise KeyError(f'Attempt to overwrite {key!r} in LogRecord')

                rv.__dict__[key] = extra[key]

        return rv

    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
        request=None,
    ):
        """Низкоуровневая процедура логирования.

        Создает LogRecord и передает его всем обработчикам данного логгера.
        """
        sinfo = None

        if _srcfile:
            # IronPython doesn't track Python frames, so findCaller raises an
            # exception on some versions of IronPython. We trap it here so that
            # IronPython can use logging.
            try:
                python_version = platform.python_version()

                if Version(python_version) < Version('3.9'):
                    fn, lno, func, sinfo = self.findCaller(stack_info)
                else:
                    fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)

            except ValueError:  # pragma: no cover
                fn, lno, func = '(unknown file)', 0, '(unknown function)'
        else:  # pragma: no cover
            fn, lno, func = '(unknown file)', 0, '(unknown function)'

        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()

        session_info = get_session_info(request)
        msg = f'{session_info}{smart_str(msg)}'

        record = self.makeRecord(self.name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)
        self.handle(record)
