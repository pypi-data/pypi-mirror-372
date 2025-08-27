"Модуль с построителями отчетов"

import os
import sys
import uuid

from django.conf import (
    settings,
)
from simple_report.converter.abstract import (
    FileConverter,
)
from simple_report.report import (
    DocumentReport,
    SpreadsheetReport,
)
from simple_report.xls.document import (
    DocumentXLS,
)


path_dir = settings.REPORTS_DIR
if not os.path.exists(path_dir):
    os.makedirs(path_dir)


def get_path(filename):
    """Путь до временного файла отчёта.

    :param str filename: имя файла (с раcширением, без пути до файла)
    :rtype: str
    """
    return os.path.abspath(os.path.join(path_dir, filename))


def get_url(filename):
    """URL до временного файла отчёта.

    :param str filename: имя файла (с раcширением, без пути до файла)
    :rtype: str
    """
    return '/'.join((settings.REPORTS_URL, filename))


class SimpleReporter:
    """Объект занимающийся комплексным построением отчета на основе simple_report.

    1) инстанцированием и загрузкой данных провайдера
    2) инстанцированием билдера
    3) построением отчета

    Можно использовать вне паков и экшнов

    ..code:

    reporter = MySimpleReporter(provider_params, builder_params)
    report_url = reporter.make_report()
    """

    # доступные форматы
    _available_extensions = ['.xls', '.xlsx', '.docx']

    # формат по-умолчанию
    extension = '.xls'

    # путь где лежит файл шаблона отчета
    template_file_path = None
    """
    будет искать шаблон report.{extension} в директори отчета
    template_file_path = None
    custom_report.{extension} по абсолютному пути
    template_file_path = '/tmp/some/custom_report.{extension}'
    по относительному ./templates в директории отчета
    template_file_path = './templates/custom_report.{extension}'
    report.{extension} в ./templates/somedir/
    template_file_path = './templates/somedir/'
    """

    # класс провайдера для случая простого провайдера
    data_provider_class = None

    # класс билдера
    builder_class = None

    # класс адаптера
    adapter_class = None

    def __init__(self, provider_params, builder_params):
        assert self.builder_class, ''
        self.provider_params = provider_params
        self.builder_params = builder_params

    def get_template(self, default_base_name='report'):
        """Возвращает путь к шаблону отчета.

        :param default_base_name: базовое имя шаблона,
            если определить не удалось
        :type default_base_name: str
        :returns: str - полный путь к шаблону
        """
        if self.template_file_path is not None and os.path.isabs(self.template_file_path):
            return self.template_file_path

        report_file_path = sys.modules[self.__module__].__file__

        report_dir = os.path.dirname(report_file_path)

        rel_sub_path = ''
        if self.template_file_path is not None and self.template_file_path.startswith('./'):
            rel_sub_path = os.path.relpath(os.path.dirname(self.template_file_path))

        if self.template_file_path is None:
            base_name, _ = os.path.splitext(os.path.basename(report_dir))
        else:
            base_name, _ = os.path.splitext(os.path.basename(self.template_file_path))
            if not base_name:
                base_name = default_base_name

        auto_report_name = '{0}{1}{2}'.format(base_name, os.path.extsep, self.extension.strip('.'))
        auto_report_path = os.path.join(report_dir, rel_sub_path, auto_report_name)

        assert os.path.isfile(auto_report_path), "Report template '{0}' not found at {1}".format(
            auto_report_name, auto_report_path
        )

        return auto_report_path

    def set_up_report(self):
        """Настройка формата отчёта."""
        template_path = self.get_template()

        if self.extension == '.xls':
            report = SpreadsheetReport(template_path, wrapper=DocumentXLS, type=FileConverter.XLS)
        elif self.extension == '.xlsx':
            report = SpreadsheetReport(template_path)
        elif self.extension == '.docx':
            report = DocumentReport(template_path)
        else:
            raise Exception('Unknown template extension')

        return report

    def set_file_and_url(self):
        """Возвращает кортеж из абс. пути отчёта и url для скачивания.

        Не требует переопределения.
        """
        title = self.builder_params.get('title')
        title = title + '_' if title else ''
        base_name = title + str(uuid.uuid4())[0:16] + self.extension
        out_file_path = get_path(base_name)
        out_file_url = get_url(base_name)

        return (out_file_path, out_file_url)

    def create_provider(self):
        """Кастомный метод для создания экземпляра класса провайдера.

        Используется в случае необходимости явного вызова конструктора
        провайдера, например, для композитного провайдера.
        :returns: инстанс дата-провайдера
        """

    def init_provider(self, data_provider):
        """Инициализирует дата-провайдер с параметрами self.provider_params."""
        data_provider.init(**self.provider_params)

    def create_builder(self, data_provider, report):
        """
        Создание билдера.
        Если требуется, можно использовать адаптер self.adapter_class

        :returns: билдер с параметрами self.builder_params
        """
        return self.builder_class(data_provider, adapter=self.adapter_class, report=report, params=self.builder_params)

    def get_data_provider(self):
        """Создание провайдера и взятие данных.

        :return: Provider с уже сформированным результатом
        """
        # создание провайдера
        # для случая композитного провайдера
        data_provider = self.create_provider()
        if data_provider is None:
            # если простой провайдер, достаточно описать его класс
            data_provider = self.data_provider_class()

        self.init_provider(data_provider)
        data_provider.load_data()

        return data_provider

    def _get_report_builder(self, data_provider, report):
        """Создание билдера и построение отчета.

        :param data_provider: Provider с уже сформированным результатом.
        :param report: Отчет форматов .xls, .xlsx или .docx
        :returns: Результат выполнения метода build
        """
        # создание билдера, который будет строить кастомный отчёт
        report_builder = self.create_builder(data_provider, report=report)
        return report_builder.build()

    def create_dir(self, out_file):
        """Создание директории для сохранения файла.

        :param out_file:  str, путь к файлу.
        :raise: OsError
        :return: None
        """
        # Если пытаемся сохранить файл в несуществующую директорию,
        # то попробуем её предварительно создать
        cat = os.path.dirname(out_file)
        if not os.path.exists(cat):
            # здесь может быть OsError
            os.makedirs(cat)

    def build_report(self, report, out_file, params):
        """Построение отчета.

        :param report: Отчет форматов .xls, .xlsx или .docx
        :param out_file: str, путь к файлу.
        :param params: Результат выполение работы билдера.
        :return: None
        """
        # построение отчёта
        if isinstance(report, DocumentReport):
            report.build(out_file, params)
        else:
            report.build(out_file)

    def make_report(self):
        """Основной метод, выполняющий построение отчета."""
        # получение абс. пути отчёта
        out_file, out_url = self.set_file_and_url()
        # настройка формата отчета
        report = self.set_up_report()

        # создает провайдер и формирует данные
        data_provider = self.get_data_provider()

        # создание билдера и построение отчета
        params = self._get_report_builder(data_provider, report)

        # создание директории для сохранения файла
        self.create_dir(out_file)

        # построение отчета.
        self.build_report(report, out_file, params)

        return out_url
