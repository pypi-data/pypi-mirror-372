import os
import sys
import uuid

from simple_report.report import (
    SpreadsheetReport,
)

from educommon.report.reporter import (
    get_path,
    get_url,
)


class BaseFailureImportReport:
    """Базовый класс отчета об импорте."""

    template_name = None
    reports_dir = 'reports'
    default_extension = 'xlsx'

    def __init__(self, data):
        """:param data - данные для отчета."""

        self.data = data
        # Текущая директория
        current_dir = os.path.dirname(sys.modules[self.__module__].__file__)
        reports_dir = os.path.join(current_dir, self.reports_dir)
        # Сгенерируемое название файла
        self.base_name = '%s.%s' % (uuid.uuid4().hex, self.default_extension)

        # Директория в которую будет сохранен отчет
        self.out_file_path = get_path(self.base_name)
        # url адрес, по которому будет доступен отчет
        self.out_file_url = get_url(self.base_name)
        self.report = SpreadsheetReport(os.path.join(reports_dir, f'{self.template_name}.{self.default_extension}'))

        # Создадим директории, если их нет
        folder_path = get_path('')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def make(self):
        """Сбор отчета."""
        raise NotImplementedError
