import traceback
from abc import (
    ABCMeta,
    abstractmethod,
)
from io import (
    BytesIO,
)

from django.apps import (
    apps,
)


def read_request_body(request_body):
    return BytesIO(request_body)


class BaseWsApplicationLogger(metaclass=ABCMeta):
    """Базовый класс логгера для приложения веб-сервиса.

    Ожидает что будут определены аттрибуты app_name и log_model в потомках.
    В качестве значения для log_model ожидается кортеж вида
    ('app_name', 'model_name').
    """

    @property
    @abstractmethod
    def log_model(self):
        """Модель для логирования запросов."""

    def get_prepared_environ(self, request):
        """Возвращает подготовленное для логирования окружение запроса.

        :param request: Запрос.
        """

        log_record = self._prepare_log_record()
        log_record.request = request.body.decode('UTF-8')
        request.META['wsgi.input'] = read_request_body(request.body)
        environ = request.META.copy()
        environ['log_record'] = log_record
        return environ

    @staticmethod
    def collect_error(log_record, traceback_data):
        """Сохраняет ошибку при обращении к веб-сервису.

        :param log_record: Запись лога веб-сервиса
        :param traceback_data: Данные возникшей ошибки.
        """
        etype, value, tb = traceback_data
        traceback_text = str(''.join(traceback.format_exception(etype, value, tb, None)))
        log_record.result = traceback_text

    def save_log_record(self, wsgi_app, uri, retval, traceback_data, environ):
        """Сохраняет лог в БД.

        :param wsgi_app: Объект WSGI-приложения.
        :param uri: Полный адрес веб-сервиса.
        :param retval: Сформированный ответ веб-сервиса.
        :param traceback_data: Данные возникшей ошибки.
        :param environ: Окружение запроса.
        """

        log_record = environ['log_record']
        if traceback_data:
            self.collect_error(log_record, traceback_data)
        else:
            log_record.response = retval.content.decode('UTF-8')

        if log_record.request:
            log_record.service_address = uri
        if not wsgi_app.is_wsdl_request(environ):
            log_record.save()

    def __init_log_model_class(self):
        """Инициализирует модель для логирования."""

        if isinstance(self.log_model, (tuple, list)):
            self.log_model = apps.get_model(*self.log_model)

    def _prepare_log_record(self):
        """Подготавливает запись модели логов.

        Возможно добавление в запись значений не зависящих от выполнения
        логируемого метода веб-сервиса.
        """
        self.__init_log_model_class()
        log_record = self.log_model()
        return log_record

    @staticmethod
    def collect_log_data(ctx):
        """Сохраняет атрибуты записи лога зависящие от данных метода сервиса.

        Используется перед непосредственным вызовом метода веб-сервиса.
        """
        raise NotImplementedError


class DefaultWsApplicationLogger(BaseWsApplicationLogger):
    """Логгер по умолчанию.

    Используется для логирования уже существующих веб-сервисов.
    """

    log_model = ('ws_log', 'SmevLog')

    def _prepare_log_record(self):
        log_object = super()._prepare_log_record()
        log_object.direction = self.log_model.INCOMING
        log_object.interaction_type = self.log_model.IS_NOT_SMEV
        return log_object

    @staticmethod
    def collect_log_data(ctx):
        """Обработчик события "Вызов метода".

        Словарь METHOD_VERBOSE_NAMES обязательно должен быть определен в классе
        приложения web-сервиса. Это словарь с ключами:

            * method_verbose_name - Описание сервиса.
              interaction - Вид взаимодействия (СМЭВ или не СМЭВ).
              protocol - Протокол взаимодействия, для случаев, когда вид
                  взаимодействия определяется по протоколу.
              consumer_type - Тип потребителя сервиса.
              is_consumer_fio - Если True, то попытается заполнить наименование
                поставщика, из блока Man запроса.

        * - значения являются обязательными.
        """
        SmevLog = apps.get_model('ws_log', 'SmevLog')
        SmevProvider = apps.get_model('ws_log', 'SmevProvider')
        req_env = ctx.transport.req_env
        log_record = ctx.transport.req['log_record']

        if ctx.descriptor and ctx.descriptor.service_class:
            method_info = ctx.descriptor.service_class.METHOD_VERBOSE_NAMES[ctx.method_name]

            log_record.method_name = ctx.method_name
            log_record.method_verbose_name = method_info['method_verbose_name']
            log_record.consumer_type = method_info.get('consumer_type')

            interaction_type = method_info.get('interaction')

            if log_record.consumer_type == SmevLog.ENTITY:
                mnemonic = ctx.udc.in_smev_message.Service.Mnemonic
                address = req_env['HTTP_HOST'] + req_env['PATH_INFO']

                smev_providers = SmevProvider.objects.filter(mnemonics=mnemonic, address=address)[:1]

                if smev_providers.exists():
                    log_record.consumer_name = smev_providers[0].mnemonics

                    if interaction_type == SmevLog.IS_SMEV:
                        log_record.source = smev_providers[0].source

                        log_record.target_name = smev_providers[0].service_name

            if interaction_type is None:
                protocol = method_info.get('protocol', '')
                interaction_type = SmevLog.IS_SMEV if protocol.find('smev') != -1 else SmevLog.IS_NOT_SMEV

            log_record.interaction_type = interaction_type

        else:
            log_record.method_name = ctx.method_request_string
