class ReportConstructorException(Exception):
    """Базовый класс для исключений конструктора отчетов."""


class DataSourceParamsNotFound(ReportConstructorException):
    """Исключение при отсутствии в реестре параметров источника данных."""

    def __init__(self, data_source_name):
        self.data_source_name = data_source_name

        super().__init__(
            'Параметры для источника данных с именем "{}" не зарегистрированы в системе.'.format(
                self.data_source_name.name
            )
        )


class FilterError(ReportConstructorException):
    """Ошибка в фильтре."""

    def __init__(self, report_filter, message):
        self.report_filter = report_filter

        if not message:
            message = 'Ошибка в фильтре для столбца {}'.format(self.report_filter.column.title)

        super().__init__('Ошибка в фильтре для столбца {}: {}'.format(self.report_filter.column.title, message))
