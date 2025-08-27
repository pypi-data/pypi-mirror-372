import re
import uuid
from datetime import (
    datetime,
)

import xlrd
from django.core.exceptions import (
    ValidationError,
)
from xlrd.xldate import (
    XLDateAmbiguous,
    XLDateBadDatemode,
    XLDateNegative,
    XLDateTooLarge,
)


SUBTREE_CAN_BE_EMPTY = '__grp_can_be_empty'
START_ROW = '__start_row'
HEADER_PARSER = '__header_parser'
END_ROW = '__end_row_end_row'

_SPECIAL_KEYS = (
    SUBTREE_CAN_BE_EMPTY,
    START_ROW,
    HEADER_PARSER,
    END_ROW,
)


def _fold(tree, path='', group=None):
    """Свертка словаря-дерева.

    Свертка словаря-дерева в список пар (путь, значение, группа|None)
    ("группа", это uuid, для группировки значений одного поддерева).
    """

    if not isinstance(tree, dict):
        return [(path, tree, group)]

    if not group:
        if tree.get(SUBTREE_CAN_BE_EMPTY, False):
            group = uuid.uuid4()

    path = f'{path}/{{0}}' if path else '{0}'

    res = []
    for key, val in tree.items():
        if key in _SPECIAL_KEYS:
            continue

        key = path.format(key)
        res.extend(_fold(val, key, group))

    return res


def _unfold(lst):
    """Развертка списка пар (путь, значение) в словарь-дерево."""
    res = {}

    def set_val(res, path, val):
        key, path = (path.split('/', 1) + [None])[:2]
        if path:
            set_val(res.setdefault(key, {}), path, val)
        else:
            res[key] = val

    for path, val in lst:
        set_val(res, path, val)

    return res


# уникальное значение для отсутствия дефолтного значения
_NO_DEFAULT = uuid.UUID

MATCH_IF_EXACT = 1
MATCH_IF_STARTS_WITH = 2
MATCH_IF_CONTAINS = 3


def _is_match(value, pattern, match_type=MATCH_IF_EXACT):
    """Проверка на совпадение значения с образцом."""
    pattern = pattern.upper()
    value = value.upper()

    if match_type == MATCH_IF_CONTAINS:
        return value.find(pattern) >= 0
    elif match_type == MATCH_IF_STARTS_WITH:
        return value.startswith(pattern)

    return value == pattern


class CellValueError(Exception):
    """Исключение для неверного значения ячейки."""

    pass


class EmptyObligatoryCellError(CellValueError):
    """Исключение для неверного значения ячейки."""

    def __init__(self, message=None):
        super().__init__(message or 'Ячейка не может быть пустой!')


class BaseCell:
    """Прототип парсера ячейки."""

    _default = _NO_DEFAULT

    def __init__(self, default=_NO_DEFAULT):
        self._default = default

    def default(self):
        return (self._default, True)

    def result(self, value):
        return (value, False)

    def _parse(self, value):
        """Разбор значения."""
        raise NotImplementedError('Прототип не используется напрямую!')

    def from_cell(self, sheet, row, col):
        """Получение значения из ячейки в виде (значение, is_default)."""
        try:
            value = sheet.cell(row, col).value
        except IndexError:
            if self.is_obligatory():
                raise EmptyObligatoryCellError()
            return self.default()

        if isinstance(value, str):
            value = value.strip()

        if value is None or value == '':
            if self.is_obligatory():
                raise EmptyObligatoryCellError()
            return self.default()

        return self._parse(str(value))

    def is_obligatory(self):
        return self._default == _NO_DEFAULT


class StringCell(BaseCell):
    """Строковая ячейка."""

    MSG_RECORD_TRUNCATED = 'Превышена максимально допустимая длина записи. Запись сокращена'

    DEFAULT_RE_MESSAGE = 'Неправильный формат записи'

    def __init__(
        self, default=_NO_DEFAULT, max_length=None, regex=None, validator=None, error_message=None, verbose=True
    ):
        """Строковая ячейка.

        :param int max_length: Максимальная длина строки.
        :param regex: Регулярное выражение для проверки значения.
        :param validator: Регулярное выражение для проверки значения.
        :param error_message: Сообщение в случае провала проверки.
        :param bool verbose: Записывать ли сообщения в лог.
        """
        assert max_length is None or isinstance(max_length, int)

        super().__init__(default)

        self._max_length = max_length
        self._verbose = verbose
        self._regex = regex
        self._validator = validator
        self._error_message = error_message

        self.message = None

    def set_mgs(self, msg):
        self.message = self.message or '' + msg

    def _validate(self, value):
        """Выплоняет проверку по регулярному выражению.

        Если проверка не пройдена и ячейка обязательна, то райзит
        CellValueError. Если ячейка не обязательна, то она пропускается и
        пишется в лог, если verbose == True.
        """
        if self._regex:
            if not self._regex.match(value):
                message = self._error_message or self.DEFAULT_RE_MESSAGE

                if self._default is None:
                    if self._verbose:
                        self.set_mgs(message)
                    value = ''

                elif self._default is _NO_DEFAULT:
                    raise CellValueError(message)

        elif self._validator:
            try:
                self._validator(value)

            except ValidationError as err:
                if self._default is None:
                    if self._verbose:
                        self.set_mgs(', '.join(err.messages))
                    value = ''

                elif self._default is _NO_DEFAULT:
                    raise CellValueError(', '.join(err.messages))

        return value

    def _truncate(self, value):
        """Обрезает строку до указанной в self._max_length длины."""
        new_value = value[: self._max_length]
        if self._verbose and new_value != value:
            self.set_mgs(self.MSG_RECORD_TRUNCATED)

        return new_value

    def _parse(self, value):
        self.message = None

        if value.endswith('.0'):
            # эти преобразования нужны для отбрасывания ".0" из строки,
            # когда Excel сохраняет значение в виде числа с
            # неотображаемой дробной частью
            value = value[:-2]

        if self._max_length is not None:
            value = self._truncate(value)

        if self._regex is not None or self._validator is not None:
            value = self._validate(value)

        return self.result(str(value))


class MaybeStringCell(StringCell):
    """Строка или None."""

    def __init__(self, default=None, max_length=None, regex=None, validator=None, error_message=None, verbose=True):
        """Строка или None.

        :param int max_length: Максимальная длина строки.
        :param regex: Регулярное выражение для проверки значения.
        :param validator: Регулярное выражение для проверки значения.
        :param error_message: Сообщение в случае провала проверки.
        :param bool verbose: Записывать ли сообщения в лог.
        """
        super().__init__(
            default=None,
            max_length=max_length,
            regex=regex,
            validator=validator,
            error_message=error_message,
            verbose=verbose,
        )


class RawCell(BaseCell):
    """Сырая строковая ячейка "как есть".

    В том числе с добавками Excel в зависимости от типа ячейки.
    """

    def _parse(self, value):
        return self.result(str(value))


class MaybeRawCell(RawCell):
    """Сырая строковая ячейка "как есть" или None."""

    def __init__(self):
        super().__init__(default=None)


class IntCell(BaseCell):
    """Integer ячейка."""

    def _parse(self, value):
        try:
            result = int(value)
        except (TypeError, ValueError):
            try:
                result = int(float(value))
            except (TypeError, ValueError):
                raise CellValueError(f'Число имеет неверный формат! "{value}"')
        return self.result(result)


class MaybeIntCell(IntCell):
    """Int или None."""

    def __init__(self):
        super().__init__(default=None)


class MaybeNonNegativeIntCell(MaybeIntCell):
    """Не отрицательное целое число или None.

    Не отбрасывает дробную часть (если она больше 0) и райзит ошибку.
    """

    def _parse(self, value):
        result, _ = super()._parse(value)

        if result < 0:
            raise CellValueError(f'Число должно быть не меньше нуля! "{value}"')
        if float(value) != float(int(float(value))):
            raise CellValueError(f'Число должно быть целым! "{value}"')
        return self.result(result)


class BooleanCell(BaseCell):
    """Bool-ячейка, получает True при совпадении с паттерном."""

    def __init__(self, default=_NO_DEFAULT, pattern=None, match_type=MATCH_IF_EXACT):
        """Если паттерн опущен (или None), то результат будет True при любой значащей строке в ячейке."""
        super().__init__(default=default)

        self.pattern = pattern
        self.match_type = match_type

    def _parse(self, value):
        if self.pattern is None:
            return self.result(bool(value.strip()))
        return self.result(_is_match(value, self.pattern, self.match_type))


class MaybeTrueCell(BooleanCell):
    """Bool-ячейка, которая получает значение True при успешном совпадении паттерна."""

    def __init__(self, default=None, pattern=None, match_type=MATCH_IF_EXACT):
        """Если паттерн опущен (или None), то результат будет True при любой значащей строке в ячейке.

        Параметр default игнорируется (всегда равен False).
        """
        super().__init__(default=False, pattern=pattern, match_type=match_type)

    def _parse(self, value):
        result, _ = super()._parse(value)

        if result:
            return self.result(True)
        else:
            return self.default()


class MaybeFalseCell(BooleanCell):
    """Bool-ячейка, которая получает значение False при успешном совпадении паттерна."""

    def __init__(self, default=None, pattern=None, match_type=MATCH_IF_EXACT):
        """Если паттерн опущен (или None), то результат будет False при любой значащей строке в ячейке.

        Параметр default игнорируется (всегда равен True).
        """
        super().__init__(default=True, pattern=pattern, match_type=match_type)

    def _parse(self, value):
        result, _ = super()._parse(value)

        if result:
            return self.result(False)
        else:
            return self.default()


class EnumCell(BaseCell):
    """Ячейка, которая может принимать одно из заданных значений."""

    def __init__(self, default=_NO_DEFAULT, choices=None, match_type=MATCH_IF_EXACT, blank_values=None):
        """choices - список вариантов вида (pattern, value)."""
        assert len(choices) >= 2, 'Должно быть указано хотя бы 2 варианта!'

        super().__init__(default=default)

        self.choices = choices
        self.match_type = match_type
        self.blank_values = blank_values

    def _is_blank(self, value):
        if self.blank_values is not None:
            for blank_value in self.blank_values:
                if value.lower() == str(blank_value).lower():
                    return True
        return False

    def _parse(self, value):
        if self._is_blank(value):
            return self.result(self._default)
        for result, pattern in self.choices:
            if _is_match(value, pattern, self.match_type):
                return self.result(result)
        raise CellValueError('Недопустимое значение!')


WRONG_DATE_FORMAT_MSG = 'Неправильный формат даты!'


class DateCell(BaseCell):
    """Ячейка даты."""

    # различные возможные допустимые форматы дат
    possible_date_formats = ('%d.%m.%Y', '%Y.%m.%d', '%d.%m.%y')

    def _parse(self, value):
        result = None
        try:
            result = datetime(*xlrd.xldate_as_tuple(float(value), 0))
        except (XLDateNegative, XLDateAmbiguous, XLDateTooLarge, XLDateBadDatemode):
            raise CellValueError(WRONG_DATE_FORMAT_MSG)
        except ValueError:
            value = str(value).strip()[:10]
            value = value.replace('/', '.').replace('-', '.')
            if any(x not in '0123456789.' for x in value):
                raise CellValueError(WRONG_DATE_FORMAT_MSG)
            for date_format in self.possible_date_formats:
                try:
                    result = datetime.strptime(value, date_format)
                    break
                except (ValueError, TypeError):
                    pass

        if result is None:
            raise CellValueError(WRONG_DATE_FORMAT_MSG)

        return self.result(result.date())


class MaybeDateCell(DateCell):
    """Date или None."""

    def __init__(self):
        super().__init__(default=None)


class DynamicStartRow:
    """Автоматический поиск начала таблицы по ее заголовкам ее столбцов."""

    def __init__(self, table_headers, order_sensetive=True, case_sensitive=False, search_area=[(0, 0), (50, 50)]):
        """
        :param list table_headers: Список заголовков: ['Фамилия' 'Имя']
        :param bool order_sensetive: Учитывать порядок списка table_headers
        :param bool case_sensitive: Учитывать регистр при сопоставлении
        :param list search_area: Область в которой будет производиться поиск
        """

        assert table_headers
        assert len(search_area) == 2

        self.min_row, self.min_col = search_area[0]
        self.max_row, self.max_col = search_area[1]

        self.order_sensetive = order_sensetive
        self.case_sensitive = case_sensitive
        if case_sensitive:
            self.table_headers = table_headers
        else:
            self.table_headers = [s.upper() for s in table_headers]

    def find_pos(self, sheet):
        max_row = min(self.max_row, sheet.nrows)
        max_col = min(self.max_col, sheet.ncols)

        for row in range(self.min_row, max_row):
            matched = {}
            for col in range(self.min_col, max_col):
                val = sheet.cell(row, col).value

                if isinstance(val, str) and not self.case_sensitive:
                    val = val.strip().upper()

                if val in self.table_headers:
                    matched.setdefault(val, col)

            if len(matched) == len(self.table_headers):
                cols_nums = [matched[h] for h in self.table_headers]
                if self.order_sensetive and sorted(cols_nums) != cols_nums:
                    continue

                return row, min(cols_nums)

    def find_row(self, sheet):
        pos = self.find_pos(sheet)
        if pos:
            row, col = pos
            return row


class SimpleColumnMatcher:
    """Класс сопоставления столбцов таблицы."""

    def __init__(self, column_name, unique_check=False, strip=True, case_sensitive=False, replacer=None):
        """
        :param str column_name: Название столбца
        :param bool unique_check: Нужно ли проверять на то, чтобы данный
                matcher совпал только с одним столбцом таблицы
        :param bool strip: Нужно ли удалять крайние пробельные символы
        :param bool case_sensitive: Учитывать регистр при сопоставлении
        :param callable replacer: Функция для доп. настройки значения.
            Например:
            замена нескольких пробелов одним: lambda s: re.sub(r'\s+', ' ', s)
            замена ё на е: lambda s: s.replace('ё', 'е')
        """
        self.column_name = column_name
        self._unique_check = unique_check
        self.strip = strip
        self.case_sensitive = case_sensitive
        if replacer:
            assert callable(replacer)
        self.replacer = replacer

    def get_column_name(self):
        """Возвращает название столбца."""
        return self.column_name

    @property
    def unique_check(self):
        return self._unique_check

    def _prepare_cell_value(self, cell_value):
        """Подготовка значения с учетом флагов настроек."""
        cell_value = str(cell_value)
        if self.strip:
            cell_value = cell_value.strip()

        if not self.case_sensitive:
            cell_value = cell_value.upper()

        if self.replacer:
            cell_value = self.replacer(cell_value)

        return cell_value

    def match(self, cell_value):
        """Проверка: отвечает ли значение в cell_value требуемому названию столбца."""

        column_name = self.column_name
        if not self.case_sensitive:
            column_name = column_name.upper()

        cell_value = self._prepare_cell_value(cell_value)

        return cell_value == column_name


class RegexColumnMatcher(SimpleColumnMatcher):
    """Сопоставление столбцов по регулярному выражению."""

    def __init__(self, column_name, regex, **kwargs):
        if isinstance(regex, str):
            flags = re.UNICODE
            if not kwargs.get('case_sensitive'):
                flags |= re.IGNORECASE

            regex = re.compile(regex, flags)
        self.regex = regex

        super().__init__(column_name, **kwargs)

    def match(self, cell_value):
        cell_value = self._prepare_cell_value(cell_value)

        return bool(self.regex.search(cell_value))


# =============================================================================
# XLSLoader
# =============================================================================


class XLSLoader:
    """Загрузчик xls-файла с разбором."""

    config = {}

    """
    ..code::

        config = {
            'заголовок листа': {
               'объект_1': {
                   #SUBTREE_CAN_BE_EMPTY: True,  # вся группа м.б. пустой
                   'поле_объекта': ('шапка столбца', парсер_ячейки),
                   'другое_поле_объекта': ('шапка столбца', парсер_ячейки),
               },
               'просто параметр': ('шапка столбца', парсер_ячейки)
            # начинать разбор с указанной строки:
            #START_ROW: 0,
            # все строки выше START_ROW передаются в HEADER_PARSER
            # в виде итератора ячеек, результаты вызовов которого можно
            # получить после загрузки файла через свойство headers
            #HEADER_PARSER: lambda cells: cells,
            }
        }
    """

    # ключ прокси в лоадере, который сообщает загрузчику, что имя листа - не
    # имеет значения
    ANY_SHEET = '*'

    XLS_POS = '__xls_pos__'

    __RESERVED_SHEET = 'СПРАВОЧНИК'

    def __init__(self, memory_mapped_file, config=None):
        self._file = memory_mapped_file
        if config is not None:
            self.config = config

        # основные ошибки
        self._common_log = []
        # ошибки строк; ключи: (имя_листа, № листа, № строки)
        self._row_errors_log = {}
        self._log_change_flag = False

        self._book = xlrd.open_workbook(file_contents=memory_mapped_file.read())

        if not all((self._file, self._book.nsheets > 0)):
            self._log('Не удалось загрузить файл!')
            self._book = None
            raise ValueError('See loader log')

        # древовидные парсеры листов делаются плоскими
        # накапливаются стартовые колонки и парсеры заголовка для листов
        self._start_rows, self._end_rows = {}, {}
        self._header_parsers = {}
        self._flat_config = {}
        for k, v in self.config.items():
            try:
                k = k.strip().upper()
            except AttributeError:
                pass

            self._start_rows[k] = v.pop(START_ROW, 0)
            self._end_rows[k] = v.pop(END_ROW, None)

            self._header_parsers[k] = v.pop(
                HEADER_PARSER,
                # парсер строки шапки листа по-умолчанию:
                # накапливает в список непустые ячейки
                lambda x: list(filter(bool, x)),
            )
            self._flat_config[k] = _fold(v)

        if self._XLSLoader__RESERVED_SHEET in self._flat_config:
            raise AssertionError(f'Название листа "{self._XLSLoader__RESERVED_SHEET}" зарезервировано!')

        self._loaded_data = {}
        self._headers = {}

    def _log_common_error(self, *items):
        """Запись в основной лог ошибок."""
        self._log_change_flag = True
        self._common_log.extend(items)

    def _log_row_error(self, xls_pos, *items):
        """Добавление ошибки в строке."""
        self._log_change_flag = True
        self._row_errors_log.setdefault(xls_pos, []).extend(items)

    def _reset_logs_change_state(self):
        self._log_change_flag = False

    def _logs_changed(self):
        return self._log_change_flag

    @property
    def log(self):
        return self._common_log

    @property
    def rows_log(self):
        return self._row_errors_log

    @property
    def data(self):
        return self._loaded_data

    @property
    def headers(self):
        return self._headers

    def load(self):
        """Загрузка листа по дескриптору колонок строки."""
        if self._book is None:
            return False

        self._loaded_data = {}
        self._headers = {}
        self._reset_logs_change_state()

        default_parsers = self._flat_config.get(self.ANY_SHEET)
        has_default_parser = bool(default_parsers)

        for sheet_num in range(self._book.nsheets):
            sheet = self._book.sheet_by_index(sheet_num)
            sheet_name = sheet.name.strip().upper()
            parser_key = sheet_name
            header_data = []

            try:
                parsers = self._flat_config[sheet_name]
            except KeyError:
                if sheet_name == self._XLSLoader__RESERVED_SHEET:
                    continue
                for k, v in self._flat_config.items():
                    if (isinstance(k, int) and (sheet_num + 1) == k) or (isinstance(k, tuple) and (sheet_num + 1) in k):
                        parsers = v
                        parser_key = k
                        break
                else:
                    if has_default_parser:
                        parsers = default_parsers
                    else:
                        expected_sheets = (
                            key
                            for key in map(lambda x: str(x).capitalize(), self._flat_config)
                            if key != self.ANY_SHEET
                        )

                        self._log_row_error(
                            (sheet.name, sheet_num + 1, 0),
                            f'Неверное название листа №{sheet_num + 1}: {sheet.name}.\n'
                            f'Ожидаемые названия листов: {", ".join(expected_sheets)}',
                        )
                        continue

            if not parsers:
                continue

            # парсинг шапки листа
            # если функция парсинга не задана, ячейки передаются как список
            header_parser = self._header_parsers[parser_key]
            start_row = self._start_rows.get(parser_key, 0)
            if isinstance(start_row, DynamicStartRow):
                sheet = self._book.sheet_by_index(0)
                start_row = start_row.find_row(sheet)
                if start_row is None:
                    self._log_common_error('Таблица не найдена')
                    continue

            header_data = self._headers.setdefault(parser_key, [])
            for row in range(0, start_row):
                # парсеру заголовка передаётся итератор ячеек по строкам
                header_data.append(header_parser((sheet.cell(row, i).value for i in range(sheet.ncols))))

            # разбор шапки листа
            col_parsers = []
            errors = []

            for path, (col_mather, parser), grp in parsers:
                if isinstance(col_mather, str):
                    col_mather = SimpleColumnMatcher(col_mather)
                # в шапке могут быть целочисленные ячейки
                elif isinstance(col_mather, int):
                    col_mather = SimpleColumnMatcher(str(col_mather))
                elif isinstance(col_mather, float):
                    col_mather = SimpleColumnMatcher(str(col_mather))

                column_name = col_mather.get_column_name()

                matched_cols = []
                # поиск столбца по шапке
                for col in range(sheet.ncols):
                    try:
                        cell_value = sheet.cell(start_row, col).value
                    except IndexError:
                        break

                    if col_mather.match(cell_value):
                        matched_cols.append((col, str(cell_value).strip()))

                if not matched_cols:
                    if parser.is_obligatory():
                        errors.append(
                            f'На листе "{sheet_name}" ({sheet_num + 1}) отсутствует столбец "{column_name}", '
                            'необходимый для импорта'
                        )

                elif col_mather.unique_check and len(matched_cols) > 1:
                    column_names = ', '.join(f'"{x[1]}"' for x in matched_cols)
                    errors.append(
                        f'На листе "{sheet_name}" ({sheet_num + 1}) присутствуют взаимоисключающие '
                        f'столбцы: {column_names}.'
                    )
                else:
                    col_pos, real_column_name = matched_cols[0]
                    col_parsers.append((col_pos, real_column_name, path, parser, grp))

            if errors:
                for error in errors:
                    self._log_row_error((sheet.name, sheet_num + 1, start_row + 1), error)
                continue

            # список результатов связанный с именем листа
            sheet_data = self._loaded_data.setdefault(parser_key, [])

            # тело с таблицей

            end_row = self._end_rows.get(parser_key) or 10**7
            if end_row < 0:
                end_row = max(sheet.nrows + end_row, 1)

            for row in range(start_row + 1, min(sheet.nrows, end_row)):
                # позиция в эксельке (лист, строка)
                xls_pos = (sheet_name, sheet_num + 1, row + 1)

                flat_values = []

                filled_cells_counts = {}

                def inc_counter(grp):
                    filled_cells_counts[grp] = filled_cells_counts.get(grp, 0) + 1

                row_errors = {}

                def add_err(grp, title, err):
                    row_errors.setdefault(grp, set()).add(f'Cтолбец "{title}": {err}')

                def add_warn(grp, title, msg):
                    message = f'Cтолбец "{title}": {msg}'
                    self._log_row_error(xls_pos, *[message])

                groups = set()

                for col, title, path, parser, grp in col_parsers:
                    groups.add(grp)
                    try:
                        val, is_default = parser.from_cell(sheet, row, col)

                        # Проверяем наличие сообщений о загрузке, если есть -
                        # складываем в сквозной лог
                        if hasattr(parser, 'message') and parser.message:
                            add_warn(grp, title, parser.message)

                    except EmptyObligatoryCellError as err:
                        add_err(grp, title, err)
                        continue

                    except CellValueError as err:
                        # ошибки, это ошибки - идут в общую группу
                        add_err(None, title, err)
                        # ячейка считается непустой, хоть и содержит ошибку
                        inc_counter(grp)
                        continue

                    # обработанные и непустые поля подсчитываются
                    if val is not None:
                        flat_values.append((path, val))
                        if not is_default:
                            inc_counter(grp)

                # если были ошибки в обязательных полях
                # и было обработано хоть одно непустое значение
                common_cnt = filled_cells_counts.get(None, 0)
                common_err = row_errors.pop(None, set())
                total_cnt = common_cnt + sum(filled_cells_counts.values())
                if total_cnt > 0:  # должно же быть хоть что-то
                    # сбор ошибок по группам, если они не пусты
                    for grp in groups:
                        if filled_cells_counts.get(grp, False):
                            common_err.union(row_errors.pop(grp, []))
                    # если ошибки накопились, выводим
                    if common_err:
                        # все ошибки - в лог
                        self._log_row_error(xls_pos, *common_err)
                    elif flat_values:
                        # преобразование в дерево и добавление в выходной буфер
                        flat_values = _unfold(flat_values)
                        flat_values[self.XLS_POS] = xls_pos
                        sheet_data.append(flat_values)

        non_empty = any(self._loaded_data.values())

        if not non_empty and not self._row_errors_log:
            self._log_common_error('Файл пуст!')

        # результат будет True, если есть хоть одна загруженная строка
        return non_empty

    @staticmethod
    def prepare_row_errors(log):
        """
        Преобразует словарь-лог ошибок строк в отсортированный список строк
        """
        result = []
        for pos, lines in sorted(log.items(), key=lambda x: (x[0][1], str(x[0][2]))):
            result.append(f'Лист "{pos[0]}" ({pos[1]}), строка {pos[2]}:')
            result.extend(f'  {line}' for line in sorted(lines))
            result.append('')

        return result


if __name__ == '__main__':

    def cells_to_pair(cells):
        cells = [c for c in cells if c]
        if cells:
            return cells[0], cells[1:]
        else:
            return ()

    config = {
        'test': {
            'date_and_int': {
                'date': ('date', DateCell()),
                'int': ('int', IntCell(default=-100)),
            },
            'mb_true': ('mb_true', MaybeTrueCell(pattern='y', match_type=MATCH_IF_STARTS_WITH)),
            'enum': ('enum', EnumCell(choices=((1, 'aaa'), (2, 'bbb')), default=3)),
            'opt_strs': {
                # SUBTREE_CAN_BE_EMPTY: False,
                'date': ('date', DateCell()),
                'str': ('str', StringCell()),
                'mb_str': ('mb_str', MaybeStringCell()),
                'mb_int': ('mb_int', MaybeIntCell()),
            },
            'pasport': (
                RegexColumnMatcher('Номер паспорта', '^(№|Номер) паспорта$'),
                StringCell(),
            ),
            # Авто определение начала таблицы
            START_ROW: DynamicStartRow(['Date', 'Int']),
            # Не загружать последнюю строку
            END_ROW: -1,
            HEADER_PARSER: cells_to_pair,
        }
    }
    with open('test_file.xls') as xls_file:
        ldr = XLSLoader(xls_file, config=config)

        print(f'Loaded: {ldr.load()}')

        print('---- header ----')
        print('\n'.join(f'{col} -> {val!r}' for col, val in ldr.headers['TEST'] if (col, val)))

        print('---- data ----')
        import pprint

        pprint.pprint(ldr.data)

        print('---- rows_log ----')
        print('\n'.join(ldr.prepare_row_errors(ldr.rows_log)))
        print('---- log ----')
        pprint.pprint(ldr.log)
