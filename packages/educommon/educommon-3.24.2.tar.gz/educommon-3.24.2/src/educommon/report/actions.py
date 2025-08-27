"""Генерация отчётов средствами платформы M3."""

from m3 import (
    ApplicationLogicException,
)
from m3.actions import (
    OperationResult,
)

from objectpack.actions import (
    BaseAction,
    BasePack,
    BaseWindowAction,
)
from objectpack.ui import (
    BaseEditWindow,
)


class BaseReportPack(BasePack):
    """Базовый класс отчёта.

    Отчёты на любых движках могут быть описаны на основе этого класса.
    """

    title = 'Отчёт'

    # дефолтное окно отчёта
    report_window = BaseEditWindow

    # признак асинхронного выполнения
    is_async = False

    # класс провайдера данных.
    data_provider_class = None

    # класс построителя отчётов
    report_builder_class = None

    # экземпляр класса провайдера
    data_provider = None

    # экземпляр класса построителя отчёта
    report_builder = None

    def create_provider(self, context):
        """Кастомный метод для создания экземпляра класса провайдера.

        Используется в случае необходимости явного вызова конструктора
        провайдера, например для композитного провайдера.

        Внимание! Экземпляр созданного провайдера должен быть присвоен
        атрибуту data_provider
        """

    def init_provider(self, context):
        """Кастомный метод для инициации провайдера.

        Данный метод должен извлечь параметры из контекста, а затем
        вызывать метод провайдера init().
        """

    def create_builder(self, context, *args, **kwargs):
        """Специальный метод для создания билдера.

        Извлекает параметры создания билдера из контекста или из *args/**kwargs
        затем инстанцирует билдер, присваивая его атрибуту self.report_builder
        """


def download_result(url):
    """Функция для скачивания файла отчёта."""
    if not isinstance(url, str):
        url = str(url, 'utf-8')
    return OperationResult(
        success=True,
        code=f"""
            (function() {{
                var hiddenIFrameID = 'hiddenDownloader',
                    iframe = document.getElementById(hiddenIFrameID);
                if (iframe === null) {{
                    iframe = document.createElement('iframe');
                    iframe.id = hiddenIFrameID;
                    iframe.style.display = 'none';
                    document.body.appendChild(iframe);
                }}
                iframe.src = "{url}";
            }})()
        """,
    )


class CommonReportWindowAction(BaseWindowAction):
    """Экшн показа окна параметров отчёта (перед выполнением отчёта)."""

    perm_code = 'report'

    def create_window(self):
        """Создание окна параметров отчёта."""
        self.win = self.parent.create_report_window(self.request, self.context)

    def configure_window(self):
        """Конфигурирование окна параметров отчёта."""
        self.win.save_btn.text = 'Сформировать'

    def set_window_params(self):
        """Задание параметров окна."""
        super().set_window_params()

        params = self.win_params.copy()
        params['title'] = self.parent.title
        params['form_url'] = self.parent.get_reporting_url()
        self.win_params = self.parent.set_report_window_params(params, self.request, self.context)


class CommonReportAction(BaseAction):
    """Экшн, выполняющий отчёт."""

    perm_code = 'report'

    def run(self, request, context):
        """Выполнение запроса."""
        pack = self.parent
        # проверка параметров отчёта
        pack.check_report_params(request, context)
        provider_params = pack.get_provider_params(request, context)
        builder_params = pack.get_builder_params(request, context)

        if 'title' not in builder_params and hasattr(pack, 'title'):
            builder_params.update(title=pack.title)
        # генерация отчёта
        out_file_url = pack.make_report(provider_params, builder_params)

        return download_result(out_file_url.encode('utf-8'))


class CommonReportPack(BasePack):
    """Пак, реализующий генерацию отчётов.

    Использует класс-построитель reporter.
    """

    title = 'Отчёт'

    # дефолтное окно отчёта
    report_window = BaseEditWindow

    # признак асинхронного выполнения
    is_async = False

    reporter_class = None
    """
    класс построителя отчета, наследник SimpleReporter

    ..code:

        reporter = MySimpleReporter
    """

    def __init__(self):
        """Конструктор пака генерации отчётов."""
        super().__init__()

        self.report_window_action = CommonReportWindowAction()
        self.report_action = CommonReportAction()
        self.actions.extend(
            [
                self.report_window_action,
                self.report_action,
            ]
        )

    def get_reporting_url(self):
        """Отдаёт адрес форме, куда передавать данные для обработки."""
        return self.report_action.get_absolute_url()

    @staticmethod
    def context2dict(context):
        """Преобразование контекста в словарь."""
        result = {}
        for key, value in context.__dict__.items():
            try:
                if callable(value):
                    value = value()
                result[key] = value
            except TypeError:
                continue

        return result

    def check_report_params(self, request, context):
        """Проверка передаваемых параметров для формирования отчёта.

        :raise: ApplicationLogicException
        """
        pass

    def get_provider_params(self, request, context):
        """Преобразование request, context к словарю для создания провайдера.

        :param request:
        :param context:
        """
        return {}

    def get_builder_params(self, request, context):
        """Преобразование request, context к словарю для создания билдера.

        :param request:
        :param context:
        """
        return {}

    def init_reporter(self, provider_params, builder_params):
        """Инициализация построителя с передачей параметров билдеру и провайдеру.

        Не требует переопределения.
        """
        return self.reporter_class(provider_params, builder_params)

    def make_report(self, provider_params, builder_params):
        """Синхронное построение отчёта. Не требует переопределения."""
        reporter = self.init_reporter(provider_params, builder_params)
        url = reporter.make_report()

        return url

    def set_report_window_params(self, params, request, context):
        """Дополнение параметров окна отчёта."""
        if self.reporter_class.extension not in (self.reporter_class._available_extensions):
            raise ApplicationLogicException('Расширение указано неверно!')
        params['extension'] = self.reporter_class.extension

        return params

    def create_report_window(self, request, context):
        """Cоздание окна настройки параметров отчёта.

        Не требует переопределения.
        """
        return self.report_window()

    def extend_menu(self, menu):
        """Размещение в меню."""
        pass
