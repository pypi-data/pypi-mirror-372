from educommon.audit_log.utils import (
    get_audit_log_context,
    set_db_param,
)


try:
    from django.utils.deprecation import (
        MiddlewareMixin,
    )
except ImportError:
    MiddlewareMixin = object


class AuditLogMiddleware(MiddlewareMixin):
    """Устанавливает параметры из запроса в текущей сессии БД.

    Устанавливает в custom settings postgresql:
      - audit_log.user_id - id пользователя;
      - audit_log.user_type_id - id ContentType модели пользователя;
      - audit_log.ip - IP адрес, с которого пришел запрос.

    В дальнейшем эта информация используется в логирующем триггере.
    """

    def process_request(self, request):
        for name, value in get_audit_log_context(request).items():
            set_db_param('audit_log.' + name, value)

    def process_response(self, request, response):
        for name in ('user_id', 'user_type_id', 'ip'):
            set_db_param('audit_log.' + name, None)
        return response
