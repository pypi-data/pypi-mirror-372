from functools import (
    partial,
)
from itertools import (
    chain,
)

from educommon.importer.constants import (
    ALL_ROWS_HAVE_ERRORS_MSG,
    IMPORT_FAIL_WITH_CRITICAL_ERROR,
    IMPORT_SUCCESS_MSG,
    IMPORT_SUCCESS_WITH_ERRORS_MSG,
)


class BaseImportLogger:
    """Абстрактный логгер для импорта.

    Ключ row_info в хэндлерах: (имя_листа, № листа, № строки).
    """

    def on_sheet_errors(self, sheet, errors, *args, **kwargs):
        raise NotImplementedError

    def on_header_errors(self, header_info, errors, *args, **kwargs):
        raise NotImplementedError

    def on_row_processed(self, row_info, *args, **kwargs):
        raise NotImplementedError

    def on_row_errors(self, row_info, errors, warnings=None, *args, **kwargs):
        raise NotImplementedError

    def on_critical_error(self, row_info, errors, *args, **kwargs):
        raise NotImplementedError

    def on_row_save(self, row_info, *args, **kwargs):
        raise NotImplementedError

    def on_row_save_rollback(self, row_info, *args, **kwargs):
        raise NotImplementedError

    def on_save_rollback(self, *args, **kwargs):
        raise NotImplementedError


class ImportLogger(BaseImportLogger):
    """Логгер для импорта.

    Сохраняет необходимую информацию при импорте, для дальнейшей
    обработки.

    Атрибуты:
        sheets_errors   Словарь хранит названия листов excel файла и их ошибки.
        header_errors   Словарь хранит названия листов excel файла и ошибки
                        обработки шапки таблиц.
        processed_rows  Список обработанных строк.
        saved_rows      Список сохраненных строк.
        critical_error_msg  Сообщение о критической ошибке (из-за которой
                        остановился импорт) импорта.
        rows_errors     Словарь хранит информацию об ошибках, полученных при
                        импорте.
        rows_warnings   Словарь хранит информацию о предупреждениях, полученных
                        при импорте.
    """

    def __init__(self, ignore_bad_rows=False, *args, **kwargs):
        """Инициализация логгера."""
        self.ignore_bad_rows = ignore_bad_rows
        self.load_errors = []
        self.sheets_errors = {}
        self.header_errors = {}
        self.processed_rows = []
        self.saved_rows = []
        self.critical_error_msg = None
        self.rows_errors = {}
        self.rows_warnings = {}

    def on_sheet_errors(self, sheet, errors, *args, **kwargs):
        self.sheets_errors.setdefault(sheet, []).extend(errors)

    def on_header_errors(self, sheet, errors, *args, **kwargs):
        self.header_errors.setdefault(sheet, []).extend(errors)

    def on_row_processed(self, row_info, *args, **kwargs):
        if row_info not in self.processed_rows:
            self.processed_rows.append(row_info)

    def on_row_errors(self, row_info, errors, warnings=None, *args, **kwargs):
        if errors:
            self.rows_errors.setdefault(row_info, []).extend(errors)

        if warnings:
            self.rows_warnings.setdefault(row_info, []).extend(warnings)

    def on_critical_error(self, row_info, error, *args, **kwargs):
        self.critical_error_msg = '{0}\n {1}'.format(self._get_row_label(row_info), error)

    def on_row_save(self, row_info, *args, **kwargs):
        if row_info not in self.saved_rows:
            self.saved_rows.append(row_info)

    def on_row_save_rollback(self, row_info, *args, **kwargs):
        try:
            self.saved_rows.remove(row_info)
        except ValueError:
            pass

    def on_save_rollback(self, *args, **kwargs):
        self.saved_rows = []

    def have_errors_in_all_rows(self):
        """Проверка на ошибки во всех обработанных записях."""
        if not self.processed_rows:
            return False

        return sorted(self.rows_errors.keys()) == sorted(self.processed_rows)

    @staticmethod
    def _add_text_lines(result, lines, top_margin=0, bottom_margin=0):
        """Добавление строк в массив с указанием отступов.

        :param list result: Массив, куда добавляется.
        :param list or basestring lines: Массив или строка для добавления.
        :param int top_margin: Отступ сверху.
        :param int bottom_margin: Отступ снизу.
        """
        if top_margin:
            result.extend(top_margin * [''])

        result.extend([lines] if isinstance(lines, str) else lines)

        if bottom_margin:
            result.extend(bottom_margin * [''])

    @staticmethod
    def _get_row_label(row_info):
        """Возвращает информацию о строке в читаемом виде."""
        sheet_name, sheet_num, row_num = row_info

        return f'Лист "{sheet_name}" ({sheet_num}), строка {row_num}:'

    @staticmethod
    def _sort_rows_info(rows_info, key=lambda x: x[2]):
        return sorted(rows_info, key=key)

    def has_error(self):
        return bool(self.critical_error_msg or self.rows_errors)

    def get_pretty_log(self):
        """Возвращает лог в читаемом виде."""
        result_lines = []
        add_lines = partial(self._add_text_lines, result_lines)

        def find_series(numbers):
            """Находит интервалы номеров в списке.

            .. code-block:: python
                >>> a = (1, 2, 3, 4, 8, 9, 10, 13)
                >>> tuple(find_series(iter(a)))

                ((1, 4), (8, 10), (13, 13))
            """
            last = prev = next(numbers)
            for cur in numbers:
                if cur - prev > 1:
                    yield last, prev
                    last = cur
                prev = cur
            yield last, prev

        def get_saved_rows_info():
            """Группированное перечисление сохранненых строк.

            Пример: 1-20, 43-200, 203-208.
            """
            rows_numbers = sorted([x[2] for x in self.saved_rows])
            series = find_series(iter(rows_numbers))

            result = ', '.join('{}-{}'.format(x, y) if x != y else str(x) for x, y in series)
            return 'Загружены строки : {0}.'.format(result)

        if self.critical_error_msg is not None:
            add_lines(IMPORT_FAIL_WITH_CRITICAL_ERROR, 0, 1)
            add_lines(self.critical_error_msg)

        elif self.saved_rows:
            if not self.rows_errors:
                if self.ignore_bad_rows:
                    add_lines(IMPORT_SUCCESS_WITH_ERRORS_MSG)
                    add_lines(get_saved_rows_info())
                else:
                    add_lines(IMPORT_SUCCESS_MSG)
            else:
                add_lines(get_saved_rows_info())

            # Дополнительно выводим предупреждения для загруженных строк
            if self.rows_warnings:
                add_lines('ПРЕДУПРЕЖДЕНИЯ:', 1, 1)

                for row in self._sort_rows_info(self.saved_rows):
                    add_lines(self._get_row_label(row), 0, 1)
                    add_lines(self.rows_warnings.get(row, []), 0, 1)
        else:
            if self.have_errors_in_all_rows():
                add_lines(ALL_ROWS_HAVE_ERRORS_MSG, 0, 1)

            if self.load_errors:
                add_lines(self.load_errors, 0, 1)
            # Список строк с любыми ошибками
            rows_with_errors = list(set(chain(self.rows_errors, self.rows_warnings)))

            for row in self._sort_rows_info(rows_with_errors):
                row_errors = self.rows_errors.get(row, [])
                row_warnings = self.rows_warnings.get(row, [])

                if row_errors or row_warnings:
                    add_lines(self._get_row_label(row), 0, 1)

                if row_errors:
                    add_lines('ОШИБКИ:')
                    add_lines(row_errors, 0, 1)

                if row_warnings:
                    add_lines('ПРЕДУПРЕЖДЕНИЯ:')
                    add_lines(self.rows_warnings, 0, 1)

        return '\n'.join(result_lines)


class SeparateImportLogger(ImportLogger):
    """Логгер с раздельным выводом ошибок."""

    def get_pretty_log(self):
        """При наличии ошибок разделяет их на разные блоки."""
        if self.critical_error_msg is not None and not self.rows_errors or self.ignore_bad_rows:
            return super().get_pretty_log()

        result_lines = []
        add_lines = partial(self._add_text_lines, result_lines)

        if self.have_errors_in_all_rows():
            add_lines(ALL_ROWS_HAVE_ERRORS_MSG, 0, 1)

        if self.load_errors:
            add_lines(self.load_errors, 0, 1)
        # Вывод ошибок по всем записям
        if self.rows_errors:
            add_lines('ОШИБКИ:', 0, 1)
        else:
            add_lines(IMPORT_SUCCESS_MSG, 0, 1)

        for row in self._sort_rows_info(list(self.rows_errors)):
            add_lines(self._get_row_label(row))
            add_lines(self.rows_errors.get(row, []), 0, 1)
        # Вывод предупреждений по всем записям
        if self.rows_warnings:
            add_lines('ПРЕДУПРЕЖДЕНИЯ:', 0, 1)

            for row in self._sort_rows_info(list(self.rows_warnings)):
                add_lines(self._get_row_label(row))
                add_lines(self.rows_warnings.get(row, []), 0, 1)

        return '\n'.join(result_lines)
