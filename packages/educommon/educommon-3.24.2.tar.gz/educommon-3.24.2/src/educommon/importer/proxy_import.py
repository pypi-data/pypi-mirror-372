from educommon.importer.loggers import (
    ImportLogger,
)
from educommon.importer.XLSReader import (
    XLSLoader,
)


SUCCESFUL_IMPORTED = 'Файл успешно импортирован'


class ProxyLoader:
    """Загрузка файла по словарю прокси-загрузчиков."""

    report_cls = None
    """Класс отчета об ошибках."""

    report_url = None
    """Адрес отчета об ошибках."""

    message = None
    """Сообщение о результате."""

    def __init__(
        self, loaders, _file, file_name, context=None, separate_logs=False, ignore_bad_rows=False, result_logger=None
    ):
        """Загрузка файла по словарю прокси-загрузчиков.

        :param dict loaders: словарь постраничных загрузчиков файла
        :param InMemoryUploadedFile _file: файл загрузки в оперативной памяти
        :param str file_name: название файла
        :param dict context: контекст
        :param bool separate_logs: флаг разделения логов импорта
        :param bool ignore_bad_rows: флаг для пропуска строк с ошибками
        :param result_logger: логгер для сбора информации импорта
        :type result_logger: educommon.importer.loggers.BaseImportLogger
        """

        config = {}
        for key, loader in loaders.items():
            config[key] = loader.make_config() if loader else {}

        self.xls_loader = XLSLoader(_file, config)
        self.loaders = loaders
        self.context = context or {}
        self.context['XLS_POS'] = self.xls_loader.XLS_POS
        self.context['ignore_bad_rows'] = ignore_bad_rows
        self.separate_logs = separate_logs
        self.ignore_bad_rows = ignore_bad_rows
        self.result_logger = result_logger or ImportLogger()

    def make_log(self, log):
        """Сбор лога для окна результата.

        :param dict log: лог
        :rtype str
        """
        return '\n'.join(self.xls_loader.log + self.xls_loader.prepare_row_errors(log))

    def load(self):
        """Импорт данных из файла."""
        if not self.xls_loader.load():
            self.message = self.make_log(self.xls_loader.rows_log)
            # FIXME: Все очень сложно.. Так как у парсера свой лог, а
            # FIXME: в этом участке кода формируется сообщение == хак.
            self.result_logger.load_errors = self.xls_loader.log
            self.result_logger.processed_rows = list(self.xls_loader.rows_log)
            self.result_logger.rows_errors = self.xls_loader.rows_log

            result = not self.message

            return result

        # Заполняем логи нового логгера логами загрузчика, чтобы не игнорились
        # ошибки, которые были при обработке xml.
        if not self.ignore_bad_rows:
            self.result_logger.load_errors = self.xls_loader.log
            self.result_logger.rows_errors = self.xls_loader.rows_log

        # Логи разделены с целью дать возможность загрузчику принять решение о
        # дальнейшей загрузке если были ошибки парсинга ячеек лог разбора ячеек
        parse_log = self.xls_loader.rows_log
        # сквозной лог загрузки данных проксями будет дополнен parse_log'ом в
        # методе load_rows у загрузчика листа
        import_log = {}
        # опционально - сквозной лог для предупреждений
        warning_log = {} if self.separate_logs else None

        for sheet, data in self.xls_loader.data.items():
            header = self.xls_loader.headers.get(sheet, [])
            # Класс загрузчика листа
            if sheet in self.loaders:
                loader_cls = self.loaders.get(sheet)
            else:
                loader_cls = self.loaders.get(sheet.upper())
            if not loader_cls:
                # Если не найден загрузчик для листа
                error_msg = f'Некорректное имя листа "{sheet}"'
                import_log[data[0][self.xls_loader.XLS_POS]] = error_msg
                # Заносим запись об ошибке при обработке листа в общий лог
                self.result_logger.on_sheet_errors(sheet, [error_msg])
                continue

            # выполняет загрузку листа (с разбором шапки и логированием)
            loader_cls.load_rows(
                header_data=header,
                rows_data=data,
                parse_log=parse_log,
                log=import_log,
                context=self.context,
                warning_log=warning_log,
                result_logger=self.result_logger,
            )

        log = self.make_log(import_log)
        result = bool(self.result_logger.saved_rows)

        if self.separate_logs:
            # если задан режим разделения логов
            if log:
                # всё же были какие-то ошибки
                final_log = [' ОШИБКИ:\n ', log]
            else:
                final_log = [
                    SUCCESFUL_IMPORTED,
                ]

            if warning_log:
                final_log.extend([' ПРЕДУПРЕЖДЕНИЯ:\n ', self.make_log(warning_log)])

            self.message = '\n'.join(final_log)
        else:
            self.message = log or SUCCESFUL_IMPORTED

        # Если произошла ошибка, составим отчет
        if not result and self.report_cls:
            report = self.report_cls(import_log)
            self.report_url = report.make()

        return result
