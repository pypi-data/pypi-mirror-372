"""Приложение для логирования запросов СМЭВ."""

import sys
import traceback

from spyne.decorator import (
    rpc,
)
from spyne.model import (
    Fault,
)
from spyne.model.primitive import (
    Unicode,
)
from spyne.protocol import (
    ProtocolBase,
)
from spyne.server.wsgi import (
    WsgiApplication,
)
from spyne.service import (
    ServiceBase,
)
from spyne_smev.fault import (
    ApiError,
)
from spyne_smev.server.django import (
    DjangoApplication,
)

from educommon.ws_log.smev.exceptions import (
    SpyneException,
)
from educommon.ws_log.utils import (
    logger_manager,
)


class LoggingDjangoApplication(DjangoApplication):
    """Переопределенный класс для логирования запросов СМЭВ."""

    def __init__(self, app, chunked=True, max_content_length=10 * 1024 * 1024, block_length=8 * 1024):
        """Метод инициализации приложения для логирования запросов СМЭВ."""
        super().__init__(app, chunked, max_content_length, block_length)

        self.application_logger = logger_manager.get_application_logger(self.app.name)
        self.app.event_manager.add_listener('method_call', self.application_logger.collect_log_data)
        self.event_manager.add_listener('wsgi_exception', wsgi_exception)

    def generate_contexts(self, ctx, in_string_charset=None):
        """Call create_in_document and decompose_incoming_envelope.

        To get method_request string in order to generate contexts.
        """
        try:
            # sets ctx.in_document
            self.app.in_protocol.create_in_document(ctx, in_string_charset)

            # sets ctx.in_body_doc, ctx.in_header_doc and
            # ctx.method_request_string
            self.app.in_protocol.decompose_incoming_envelope(ctx, ProtocolBase.REQUEST)

            # returns a list of contexts. multiple contexts can be returned
            # when the requested method also has bound auxiliary methods.
            retval = self.app.in_protocol.generate_method_contexts(ctx)

        except Fault as e:
            traceback_data = sys.exc_info()
            log_record = ctx.transport.req['log_record']
            self.application_logger.collect_error(log_record, traceback_data)
            ctx.in_object = None
            ctx.in_error = e
            ctx.out_error = e
            retval = (ctx,)

        return retval

    def __call__(self, request):
        """Логируем запрос, при вызове объекта приложения как функции."""

        def start_response(status, headers):
            # Status is one of spyne.const.http
            status, reason = status.split(' ', 1)

            retval.status_code = int(status)
            for header, value in headers:
                retval[header] = value

        retval = self.HttpResponseObject()
        environ = self.application_logger.get_prepared_environ(request)

        try:
            response = WsgiApplication.__call__(self, environ, start_response)
            self.set_response(retval, response)
        except Exception:
            traceback_data = sys.exc_info()
        else:
            traceback_data = None

        self.application_logger.save_log_record(
            wsgi_app=self,
            uri=request.build_absolute_uri(),
            retval=retval,
            traceback_data=traceback_data,
            environ=environ,
        )

        return retval


class LoggingService(ServiceBase):
    """Перекрытый класс базового класса web-сервисов spyne."""

    @classmethod
    def call_wrapper(cls, ctx):
        """Перекрыли, чтобы отдавать валидную для СМЭВ ошибку."""
        try:
            if ctx.function is not None:
                if ctx.descriptor.no_ctx:
                    result = ctx.function(*ctx.in_object)
                else:
                    result = ctx.function(ctx, *ctx.in_object)

                if hasattr(cls, 'update_log'):
                    # Метод, для кастомного обновления лог-объекта, для
                    # использования должен быть определен в классе web-сервиса.
                    cls.update_log(ctx)

                return result

        except SpyneException as exc:
            raise ApiError(exc.faultcode, exc.faultstring, ctx.function.__name__.replace('Request', 'Response'))

        except Exception as exc:
            log = ctx.transport.req['log_record']
            log.result = str(traceback.format_exc(), errors='ignore')
            raise ApiError('Server', str(exc), ctx.function.__name__.replace('Request', 'Response'))

    @rpc(Unicode, _returns=Unicode)
    def upper(self, s):
        return s.upper()


def wsgi_exception(ctx):
    """Обработчик события 'wsgi_exception'.

    Логирует обращения к web-сервисам, когда происходят ошибки десериализации
    входящего документа или ошибки функции web-сервиса.
    """
    log = ctx.transport.req['log_record']
    error = ctx.in_error or ctx.out_error

    log.method_name = ctx.method_name
    if isinstance(error, ApiError):
        log.result = error.errorMessage
    else:
        log.result = str(error)

    app_logger = logger_manager.get_application_logger(ctx.app.name)
    app_logger.collect_log_data(ctx)
