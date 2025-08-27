import abc
import itertools
import operator
from collections import (
    defaultdict,
)
from functools import (
    partial,
    reduce,
    total_ordering,
)
from operator import (
    gt,
)

from django.db import (
    models,
)
from django.db.models import (
    Q,
)
from django.db.models.fields.related import (
    RelatedField,
)
from django.db.models.fields.reverse_related import (
    ForeignObjectRel,
)
from django.db.models.manager import (
    Manager,
)
from django.forms.fields import (
    BooleanField,
)
from django.utils.encoding import (
    force_str,
)
from xlsxwriter import (
    Workbook,
)

from m3.actions.exceptions import (
    ApplicationLogicException,
)

from educommon.report.constructor import (
    constants,
)
from educommon.report.constructor.base import (
    ColumnDescriptor,
)
from educommon.report.constructor.builders.excel.constants import (
    COUNT,
    SUM,
)
from educommon.report.constructor.constants import (
    BY_VALUE_COUNT,
    BY_VALUE_SUM,
    DIRECTION_ASC,
    FALSE,
    TOTAL_COUNT,
    TOTAL_SUM,
    TOTAL_UNIQUE_COUNT,
    TRUE,
)
from educommon.report.constructor.exceptions import (
    DataSourceParamsNotFound,
    FilterError,
    ReportConstructorException,
)
from educommon.report.constructor.models import (
    ReportFilter,
    ReportFilterGroup,
    ReportTemplate,
)
from educommon.report.constructor.registries import (
    registry,
)
from educommon.report.constructor.utils import (
    get_columns_hierarchy,
    get_field,
    get_field_value_by_display,
)
from educommon.utils.misc import (
    cached_property,
)


class FilterValuesProvider:
    """Поставщик данных фильтра.

    Используется как для формирования Q-фильтра для ORM, так и для
        последующей фильтрации полученных данных.

    Возвращает значение из фильтра, преобразованное к объекту Python.

    Тип возвращаемого значения определяется оператором сравнения, который
    указан в фильтре:

        * **Пусто**: возвращается значения ``None``.
        * **Равно одному из**: возвращает кортеж из элементов с типом,
          соответствующим типу поля, по которому выполняется фильтрация данных.
        * **Между**: возвращает кортеж из двух элементов с типом,
          соответствующим типу поля, по которому выполняется фильтрация данных.
        * Во всех остальных случаях возвращает значение фильтра,
          преобразованное к типу данных того столбца, по которому выполняется
          фильтрация.

    .. note::

       Под значением фильтра подразумевается значение поля ``values`` модели
       :class:`~educommon.report.constructor.models.ReportFilter`.

    """

    def __init__(self, as_orm_filter=True):
        """Инициализация провайдера.

        :param bool as_orm_filter: преобразовать значения к типам ORM
            или к типам отчёта (например, True/False или Да/Нет).
        """

        self._as_orm_filter = as_orm_filter

    def to_python(self, value, report_filter, column_descriptor):
        """Возвращает значение из фильтра, приведенное к объекту Python.

        В параметрах фильтра значение хранится в виде текстовой строки.
        """

        if column_descriptor.data_type == constants.CT_CHOICES:
            return get_field_value_by_display(column_descriptor.field, value) if self._as_orm_filter else value
        else:
            if isinstance(column_descriptor.field.formfield(), BooleanField):
                if isinstance(value, str) and value.lower() in ('false', '0', 'нет'):
                    return False if self._as_orm_filter else FALSE

                elif isinstance(value, str) and value.lower() in ('true', '1', 'да'):
                    return True if self._as_orm_filter else TRUE

                else:
                    raise FilterError(report_filter, 'неправильно задано значение фильтра')

            return column_descriptor.field.formfield().to_python(value)

    def __call__(self, report_filter, column_descriptor):
        """Возвращает значение из фильтра, преобразованное к объекту Python.

        :param report_filter: Фильтр шаблона отчетов.
        :type report_filter: educommon.report.constructor.models.ReportFilter

        :param column_descriptor: Дескриптор поля модели, входящего в состав
            столбца отчета.
        :type column_descriptor:
            educommon.report.constructor.base.ColumnDescriptor
        """
        if report_filter.operator == constants.IS_NULL:
            result = None

        elif report_filter.operator == constants.IN:
            result = tuple(self.to_python(value, report_filter, column_descriptor) for value in report_filter.values)

        elif report_filter.operator == constants.BETWEEN:
            result = tuple(self.to_python(value, report_filter, column_descriptor) for value in report_filter.values)

            if len(result) != 2:
                raise FilterError(report_filter, 'не правильно заданы границы диапазона')

        elif report_filter.values:
            result = self.to_python(report_filter.values[0], report_filter, column_descriptor)

        else:
            raise FilterError(report_filter, 'не указано значение для сравнения.')

        return result


def is_row(data):
    """Возвращает True, если в ``data`` содержится строка с данными.

    :rtype: bool
    """
    return isinstance(data, (tuple, list)) and any(not isinstance(cell, (tuple, list)) for cell in data)


def is_block(data):
    """Возвращает True, если в ``data`` содержится блок записей.

    :rtype: bool
    """
    return data and isinstance(data, (tuple, list)) and all(isinstance(row, (tuple, list)) for row in data)


def get_data_width(data):
    """Возвращает количество колонок, занимаемое данными.

    :param list data: Данные блока, строки или ячейки.
        - Ячейка --- это простые данные (строка, число, дата и т.п.).
        - Строка --- это кортеж из данных ячеек и вложенных блоков.
        - Блок --- это кортеж из строк. Содержит только строки.

    :rtype: int
    """
    if is_block(data):
        return max(map(get_data_width, data))
    elif is_row(data):
        return sum(map(get_data_width, data))
    else:
        return 1


class _FilterBuilder:
    """Построитель фильтров для выборки данных из БД."""

    def __init__(self, report_filter, column_descriptor):
        """Инициализация экземпляра.

        :param report_filter: Фильтр шаблона отчетов.
        :type report_filter: educommon.report.constructor.models.ReportFilter

        :param column_descriptor: Дескриптор поля модели, входящего в состав
            столбца отчета.
        ::type column_descriptor:
            educommon.report.constructor.base.ColumnDescriptor
        """
        assert isinstance(report_filter, ReportFilter), type(report_filter)
        assert isinstance(column_descriptor, ColumnDescriptor), type(column_descriptor)

        self._report_filter = report_filter
        self._column_descriptor = column_descriptor

    def _get_lookup(self, field_lookup):
        """Возвращает lookup-выражение, соответствующее параметрам фильтра.

        При формировании lookup-выражения учитываются параметры фильтра
        ``case_sensitive``, ``operator``, а также тип данных столбца, по
        которому выполняется фильтрация.

        :param str field_lookup: lookup-выражение для доступа к значению поля
        """
        if not self._report_filter.case_sensitive and self._column_descriptor.data_type == constants.CT_TEXT:
            field_lookup += {
                constants.EQ: '__iexact',
                constants.CONTAINS: '__icontains',
                constants.STARTS_WITH: '__istartswith',
                constants.ENDS_WITH: '__iendswith',
                constants.IN: '__lower__in',
            }.get(self._report_filter.operator, '')

        else:
            field_lookup += {
                constants.LE: '__lte',
                constants.LT: '__lt',
                constants.GT: '__gt',
                constants.GE: '__gte',
                constants.CONTAINS: '__contains',
                constants.STARTS_WITH: '__startswith',
                constants.ENDS_WITH: '__endswith',
                constants.BETWEEN: '__range',
                constants.IN: '__in',
            }.get(self._report_filter.operator, '')

        return field_lookup

    def _get_values(self):
        if self._report_filter.operator == constants.IS_NULL:
            values = True

        elif (
            not self._report_filter.case_sensitive
            and self._column_descriptor.data_type == constants.CT_TEXT
            and self._report_filter.operator == constants.IN
        ):
            values = tuple(v.lower() for v in self._report_filter.values)

        else:
            values = FilterValuesProvider()(self._report_filter, self._column_descriptor)

        return values

    def get_orm_filter(self):
        """Возвращает условия выборки из шаблона отчета.

        :rtype: django.db.models.Q
        """
        field_lookup = self._column_descriptor.full_lookup

        filter_values = self._get_values()

        if self._report_filter.operator == constants.IS_NULL:
            if self._column_descriptor.data_type == constants.CT_TEXT:
                result = Q(Q(**{f'{field_lookup}__isnull': True}) | Q(**{field_lookup: ''}))
            else:
                result = Q(**{f'{field_lookup}__isnull': True})

        else:
            try:
                result = Q(
                    **{
                        self._get_lookup(field_lookup): filter_values,
                    }
                )
            except ValueError as error:
                raise FilterError(self._report_filter, str(error))

        if self._report_filter.exclude:
            result = ~result

        return result


class _FilterGroupBuilder:
    """Построитель Q-выражений и фильтрующих функций для групп фильтров."""

    def __init__(self, data_filterer, filter_group):
        """Инициализация экземпляра класса.

        :param data_filterer: Фильтратор данных отчета.
        :type data_filterer: _DataFilterer

        :param filter_group: Группа фильтров.
        :type filter_group:
            educommon.report.constructor.models.ReportFilterGroup
        """
        assert isinstance(data_filterer, _DataFilterer), type(data_filterer)
        assert isinstance(filter_group, ReportFilterGroup), type(filter_group)

        self._data_filterer = data_filterer
        self._filter_group = filter_group

    def _get_nested_orm_filters(self):
        for nested_group in self._filter_group.nested_groups.all():
            if any(
                report_filter
                for report_filter in self._data_filterer.values()
                if report_filter.group_id == nested_group.id
            ):
                yield nested_group.get_orm_filter()

        data_source = self._data_filterer.data_source_descriptor

        for report_filter in self._data_filterer.filters_by_id.values():
            if report_filter.group_id == self._filter_group.id:
                column_descriptor = data_source.get_column_descriptor(report_filter.column.name)
                if isinstance(column_descriptor.field, models.Field):
                    filter_builder = _FilterBuilder(report_filter, column_descriptor)
                    yield filter_builder.get_orm_filter()

    def get_orm_filter(self):
        """Возвращает Q-выражение для данной группы фильтров.

        :rtype: django.db.models.Q
        """
        operators = {
            ReportFilterGroup.OPERATOR_AND: operator.and_,
            ReportFilterGroup.OPERATOR_OR: operator.or_,
        }

        if self._filter_group.operator not in operators:
            raise ApplicationLogicException('Неподдерживаемый оператор: {}'.format(self._filter_group.operator))

        orm_filters = tuple(self._get_nested_orm_filters())

        if orm_filters:
            result = reduce(operators[self._filter_group.operator], orm_filters)
        else:
            result = Q()

        return result


class _DataFilterer:
    """Фильтратор данных отчета.

    Фильтрация данных выполняется в два этапа:

        1. Наложение фильтров на запрос.
        2. Фильтрация полученных данных в приложении.
    """

    def __init__(self, report_template, data_source_descriptor, report_columns, ignored_columns_ids):
        """Инициализация экземпляра класса.

        :param report_template: Шаблон фильтра.
        :type report_template:
            educommon.report.constructor.models.ReportTemplate

        :param data_source_descriptor: Дескриптор источника данных..
        :type data_source_descriptor:
            educommon.report.constructor.base.ModelDataSourceDescriptor

        :param report_columns: Колонки отчета, упорядоченные по порядковому
            номеру.
        :type: tuple
        :param ignored_columns_ids: Колонки исключенные из отчета.
        :type: tuple
        """
        assert isinstance(report_template, ReportTemplate), type(report_template)

        self._report_template = report_template
        self.data_source_descriptor = data_source_descriptor
        self._report_columns = report_columns
        self._ignored_columns_ids = ignored_columns_ids

    @cached_property
    def filters_by_id(self):
        """Все фильтры шаблона по id фильтра.

        :rtype: dict
        """
        query = ReportFilter.objects.filter(
            group__report_template=self._report_template,
        ).exclude(column_id__in=self._ignored_columns_ids)

        return {report_filter.id: report_filter for report_filter in query}

    def get_orm_filters(self):
        """Возвращает фильтры для формирования SQL-запроса.

        .. note::

           Предназначена для предварительной фильтрации данных на уровне СУБД.
           Т.к. данные загружаются только для модели источника данных без
           данных зависимых объектов, эти фильтры не срабатывают при загрузке
           зависимых объектов. Поэтому дополнительно нужно применять функцию
           фильтрации, возвращаемую методом :meth:`get_filter_function`.

        :rtype: django.db.models.Q
        """
        filter_group = self._report_template.filter_groups.filter(parent__isnull=True).first()

        if filter_group:
            return _FilterGroupBuilder(self, filter_group).get_orm_filter()
        else:
            return Q()

    def _get_function_for_filter(self, report_filter):
        """Возвращает функцию для фильтрации данных в соответствии с фильтром.

        :rtype: callable
        """
        data_source = self.data_source_descriptor
        column_descriptor = data_source.get_column_descriptor(report_filter.column.name)
        filter_values = FilterValuesProvider(as_orm_filter=False)(report_filter, column_descriptor)

        if report_filter.operator == constants.LE:

            def function(value):
                return value is not None and value <= filter_values

        elif report_filter.operator == constants.LT:

            def function(value):
                return value is not None and value < filter_values

        elif report_filter.operator == constants.EQ:

            def function(value):
                return value == filter_values

        elif report_filter.operator == constants.GT:

            def function(value):
                return value is not None and value > filter_values

        elif report_filter.operator == constants.GE:

            def function(value):
                return value is not None and value >= filter_values

        elif report_filter.operator == constants.IS_NULL:

            def function(value):
                return value is None or value == ''

        elif report_filter.operator == constants.CONTAINS:
            assert isinstance(filter_values, str), type(filter_values)

            if report_filter.case_sensitive:

                def function(value):
                    return value is not None and filter_values in value
            else:

                def function(value):
                    return value is not None and any(v.lower() in value for v in filter_values)

        elif report_filter.operator == constants.STARTS_WITH:
            assert isinstance(filter_values, str), type(filter_values)

            if report_filter.case_sensitive:

                def function(value):
                    return value is not None and value.startswith(filter_values)
            else:

                def function(value):
                    return value is not None and value.lower().startswith(filter_values.lower())

        elif report_filter.operator == constants.ENDS_WITH:
            assert isinstance(filter_values, str), type(filter_values)

            if report_filter.case_sensitive:

                def function(value):
                    return value is not None and value.endswith(filter_values)
            else:

                def function(value):
                    return value is not None and value.lower().endswith(filter_values.lower())

        elif report_filter.operator == constants.BETWEEN:
            if report_filter.case_sensitive:

                def function(value):
                    return value is not None and filter_values[0] <= value <= filter_values[1]
            else:

                def function(value):
                    if isinstance(value, str):
                        value = value.lower()
                        values = tuple(v.lower() for v in filter_values)
                    else:
                        values = filter_values

                    return value is not None and values[0] <= value <= values[1]

        elif report_filter.operator == constants.IN:
            assert isinstance(filter_values, tuple), type(filter_values)

            if report_filter.case_sensitive:

                def function(value):
                    return value in filter_values
            else:

                def function(value):
                    return value.lower() in (v.lower() for v in filter_values)

        else:
            raise FilterError(report_filter, 'Неподдерживаемый оператор ({})'.format(report_filter.operator))

        if report_filter.exclude:
            return lambda value: not function(value)
        else:
            return function

    def get_filter_function(self):
        """Возвращает функцию для фильтрации данных.

        Эта функция для каждого набора данных возвращает новый набор данных,
        которые отфильтрованы в соответствии с параметрами фильтрации,
        указанными в шаблоне отчета.

        Запись может быть отфильтрована полностью, либо отфильтрованы только
        вложенные блоки. В первом случае функция возвращает ``None``. Во
        втором случае --- будут удалены записи во внутренних блоках.
        """
        filter_functions = {
            report_filter.column_id: self._get_function_for_filter(report_filter)
            for report_filter in self.filters_by_id.values()
        }
        filter_functions_by_column = tuple(
            filter_functions.get(report_column.pk) for report_column in self._report_columns
        )

        def filter_function(row_data, column_functions=None):
            """Возвращает отфильтрованные данные записи отчета."""
            if column_functions is None:
                column_functions = filter_functions_by_column

            result = []
            for cell in row_data:
                cell_width = get_data_width(cell)
                column_filter_functions = column_functions[:cell_width]
                column_functions = column_functions[cell_width:]

                if is_block(cell):
                    filtered_block = _filter_block_or_row(cell, column_filter_functions)
                    if filtered_block is None:
                        return None
                    result.append(filtered_block)
                else:
                    # Простое значение (не строка или блок)
                    assert not is_row(cell), cell
                    column_filter_function = column_filter_functions[0]
                    if column_filter_function and not column_filter_function(cell):
                        return None
                    result.append(cell)

            return result

        def _filter_block_or_row(block_or_row, column_filter_functions):
            """Возвращет отфильтрованный блок/строку или None."""
            if is_row(block_or_row):
                return filter_function(block_or_row, column_filter_functions)
            filtered = [_filter_block_or_row(item, column_filter_functions) for item in block_or_row]
            filtered = [item for item in filtered if item is not None]
            return filtered or None

        return filter_function


@total_ordering
class _OrderInverter:
    """Класс-обёртка для смены направления сортировки."""

    # pylint: disable=eq-without-hash

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return gt(self.value, other.value)


class _DataSorter:
    """Сортировщик данных отчёта.

    Структура данных для отчёта представляет из себя набор кортежей (см.
    описание класса ``DataLoader``). Все кортежи можно разделить на два типа:
    строка и блок. Блок --- это набор строк, строка, в свою очередь, может
    содержать как данные ячеек, так и другие блоки. Если строка содержит блоки,
    это означает, что объекты-источники, содержащие соответствующие данные,
    связаны между собой отношением один-ко-многим.

    Сортировка строк осуществляется внутри блока на основе данных в ячейках, но
    не на основе данных вложенных блоков. Это означает, что если в параметрах
    сортировки указаны столбцы, попадающие на вложенные блоки, то сортировка
    будет внутри этих блоков, но на порядок строк во внешнем блоке это не
    повлияет.
    """

    def __init__(self, report_template, ignored_columns_ids):
        """Инициализация сортировщика данных.

        :param report_template: шаблон отчета.
        :type report_template:
            educommon.report.constructor.models.ReportTemplate

        :param ignored_columns_ids: идентификаторы игнорируемых столбцов (эти
            столбцы были добавлены в шаблон отчета до того, как были удалены
            из моделей Системы).
        """
        assert isinstance(report_template, ReportTemplate), type(report_template)

        self._report_template = report_template
        self._ignored_columns_ids = ignored_columns_ids

    @cached_property
    def _params(self):
        data = enumerate(
            self._report_template.columns.exclude(id__in=self._ignored_columns_ids)
            .order_by(
                'index',
            )
            .values_list(
                'sorting__index',
                'sorting__direction',
            )
        )

        result = {
            index: {
                'sort_index': sort_index,
                'sort_direction': direction,
            }
            for index, (sort_index, direction) in data
            if sort_index is not None
        }

        return result

    def _get_sort_key(self, row, start_index):
        """Возвращает ключ для сортировки строки."""
        assert isinstance(row, list), (type(row), row)

        values = {}
        index = start_index

        for cell in row:
            if is_block(cell):
                index += get_data_width(cell)

            else:
                if index in self._params:
                    # Для этого столбца определены параметры сортировки.
                    sort_index = self._params[index]['sort_index']
                    direction = self._params[index]['sort_direction']
                    if direction == DIRECTION_ASC:
                        values[sort_index] = cell
                    else:
                        values[sort_index] = _OrderInverter(cell)
                index += 1

        result = tuple(values[sort_index] for sort_index in sorted(values))

        return result

    def sort(self, rows, start_index=0):
        """Возвращает отсортированные данные отчета.

        Если среди значений есть None, то сортировка не выпоняется и эти
        строки просто добавляются в конце во избежание ошибок при сравнении
        разных типов

        :param rows: данные отчета (описание структуры см. в документации
            класса ``DataLoader``).
        :param start_index: индекс, с которого начнется перебор значений в rows

        :rtype: list
        """
        for row in rows:
            assert isinstance(row, list), (type(row), row)
            index = start_index
            for cell_index, cell in enumerate(row):
                if is_block(cell):
                    row[cell_index] = self.sort(cell, index)
                    index += get_data_width(cell)
                else:
                    index += 1

        nullable_rows = filter(self._is_row_nullable, rows)
        non_nullable_rows = filter(lambda _row: not self._is_row_nullable(_row), rows)

        sorted_rows = sorted(
            non_nullable_rows,
            key=partial(self._get_sort_key, start_index=start_index),
        )
        sorted_rows.extend(nullable_rows)

        return sorted_rows

    def _is_row_nullable(self, row):
        """Проверяет, есть ли среди значений в строке,
        которые нужно отсортировать, None

        :param row: строка со значениями в отчет

        :rtype: bool
        """
        values_to_sort = (i in row and row[i] for i in self._params)
        return None in values_to_sort


class DataLoader:
    """Загрузчик данных для шаблона отчета.

    Данные каждой строки отчета представлены в виде кортежа. Элементами кортежа
    могут быть значения простых типов (числа, строки и т.п.), а также
    кортежи кортежей (вложенные блоки). Вложенные блоки добавляются в тех
    случаях, когда в параметрах отчета указаны т.н. обратные связи (связь "один
    ко многим"), когда одной записи в модели источника данных соответствует
    несколько записей в связанных моделях. В таких вложенных кортежах также
    могут быть простые данные и вложенные кортежи кортежей. Глубина вложенности
    не ограничивается и зависит от настроек шаблона отчета.

    Пример:

    .. table:: Данные в табличном виде
       :align: center

       +-------------+---------+---------------------------------------------+
       | **Фамилия** | **Имя** |                **Учащиеся**                 |
       |             |         +---------------------------------------------+
       |             |         |                 **Группа**                  |
       |             |         +--------------------------+------------------+
       |             |         |       **Учреждение**     | **Наименование** |
       |             |         +--------------------------+                  |
       |             |         | **Краткое наименование** |                  |
       +-------------+---------+--------------------------+------------------+
       | Иванов      | Иван    | СДЮШОР1                  | Бокс             |
       |             |         +--------------------------+------------------+
       |             |         | СДЮШОР1                  | Фехтование       |
       +-------------+---------+--------------------------+------------------+

    Одна запись в приведенной выше таблице будет иметь следующую структуру:

    .. code-block:: python

       (
           'Иванов',
           'Иван',
           (
               ('СДЮШОР1', 'Бокс'),
               ('СДЮШОР1', 'Фехтование'),
           ),
       )
    """

    def __init__(self, report_template, data_source, report_columns, ignored_columns_ids, user):
        assert isinstance(report_template, ReportTemplate), type(report_template)
        self._report_template = report_template
        self._data_source = data_source
        self._report_columns = report_columns
        self._ignored_columns_ids = ignored_columns_ids
        self._user = user

    @staticmethod
    def _get_column_count(columns):
        # Для иерархии столбцов возвращает количество занимаемых столбцов.
        if columns:
            return sum(map(DataLoader._get_column_count, columns.values()))
        else:
            return 1

    @staticmethod
    def _get_field_display(field, field_value):
        for value, name in field.flatchoices:
            if value == field_value:
                return force_str(name, strings_only=True)

    @staticmethod
    def _get_object_data(obj, attr_name, nested):
        field = None
        if attr_name:
            field = get_field(obj, attr_name)
            model = field.model
            if isinstance(field, ForeignObjectRel):
                descriptor = getattr(model, field.get_accessor_name())
            elif isinstance(field, RelatedField):
                descriptor = getattr(model, field.name)
            else:
                descriptor = None

            if descriptor:
                try:
                    attr_value = getattr(obj, attr_name)
                except descriptor.RelatedObjectDoesNotExist:
                    attr_value = None
            else:
                try:
                    attr_value = getattr(obj, attr_name)
                except AttributeError:
                    if (
                        hasattr(obj, 'report_constructor_params')
                        and 'extra' in obj.report_constructor_params
                        and attr_name in obj.report_constructor_params['extra']
                    ):
                        # Дополнительное поле.
                        extra = obj.report_constructor_params['extra']
                        params = extra[attr_name]
                        if 'attr' in params:
                            attr_value = getattr(obj, params['attr'])
                            if callable(attr_value):
                                attr_value = attr_value()
                        elif 'func' in params:
                            attr_value = params['func'](obj)
                        else:
                            raise

                if attr_value is not None and isinstance(field, (models.BooleanField, models.NullBooleanField)):
                    attr_value = TRUE if attr_value else FALSE
        else:
            attr_value = obj
            descriptor = None

        # Обратная связь или M2M. Такие данные выводятся в виде кортежа.
        if attr_name and (
            isinstance(field, ForeignObjectRel)
            and hasattr(descriptor, 'related_manager_cls')
            and isinstance(attr_value, descriptor.related_manager_cls)
            or isinstance(field, models.ManyToManyField)
            and isinstance(attr_value, Manager)
        ):
            objects = attr_value.all()
            if objects:
                related_obj_data_gen = (
                    list(DataLoader._get_object_data(related_obj, None, nested)) for related_obj in objects
                )
                yield list(itertools.takewhile(bool, related_obj_data_gen))
            else:
                yield [[None] * DataLoader._get_column_count(nested)]

        # Прямая связь (ForeignKey или OneToOneField).
        elif nested:
            if attr_value:
                for k, v in nested.items():
                    for object_data in DataLoader._get_object_data(attr_value, k, v):
                        yield object_data
            else:
                for _ in range(DataLoader._get_column_count(nested)):
                    yield None

        else:
            # Поле, значения которого определяются через внутренный base_field
            if getattr(field, 'base_field', False) and attr_value:
                inner_values = []
                for inner_value in attr_value:
                    if getattr(field.base_field, 'flatchoices', False):
                        inner_values.append(DataLoader._get_field_display(field.base_field, inner_value))
                    else:
                        inner_values.append(inner_value)
                yield list((str(value),) for value in inner_values)

            # Поле с choices.
            elif getattr(field, 'flatchoices', False):
                yield DataLoader._get_field_display(field, attr_value)

            # Поле с данными.
            else:
                yield attr_value

    @cached_property
    def _data_filterer(self):
        """Фильтратор данных отчета."""
        return _DataFilterer(self._report_template, self._data_source, self._report_columns, self._ignored_columns_ids)

    @cached_property
    def _data_aggregator(self):
        """Агрегатор данных отчета."""
        return DataAggregator(self._report_columns)

    def _available_units_filter(self, query):
        """Фильтратор данных отчета по доступности учреждений."""
        return self._data_source.add_source_filter(query, self._report_template.include_available_units, self._user)

    def _get_objects(self):
        result = self._data_source.model.objects.all()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Добавление фильтров в запрос.

        if (
            ReportFilter.objects.filter(
                column__report_template=self._report_template,
            )
            .exclude(column_id__in=self._ignored_columns_ids)
            .exists()
        ):
            # Является ли модель древовидной(mptt - Modified Preorder Tree Traversal)
            if hasattr(self._data_source.model, '_mptt_meta'):
                result = result.filter(self._data_filterer.get_orm_filters()).distinct(
                    self._data_source.model._mptt_meta.tree_id_attr
                )
            else:
                result = result.filter(self._data_filterer.get_orm_filters()).distinct('pk')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Добавление параметров включения вложенных учреждений.

        result = self._available_units_filter(result)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        return result

    def _get_rows_data(self, columns_hierarchy):
        filter_function = self._data_filterer.get_filter_function()

        for obj in self._get_objects():
            row_data = list(DataLoader._get_object_data(obj, None, columns_hierarchy))
            if row_data and any(row_data):
                row_data = filter_function(row_data)
                if row_data:
                    self._data_aggregator.aggregate(row_data)
                    yield row_data

    def __iter__(self):
        column_names = (
            self._report_template.columns.filter(
                visible=True,
            )
            .exclude(pk__in=self._ignored_columns_ids)
            .values_list('name', flat=True)
        )

        if not column_names:
            raise ReportConstructorException('В шаблоне нет ни одного отображаемого столбца.')

        columns_hierarchy = get_columns_hierarchy(*column_names)

        result = list(self._get_rows_data(columns_hierarchy))

        sorter = _DataSorter(self._report_template, self._ignored_columns_ids)
        result = sorter.sort(result)

        result.extend(self._data_aggregator.get_rows())

        return iter(result)


class ReportBuilderBase(metaclass=abc.ABCMeta):
    """Базовый класс построителя отчета."""

    def __init__(self, report_template, file_path, user):
        """Инициализация класса.

        :param report_template: Шаблон отчета.
        :type report_template:
            educommon.report.constructor.models.ReportTemplate

        :param str file_path: Путь к файлу отчета.
        """
        assert isinstance(report_template, ReportTemplate), type(report_template)

        if report_template.data_source_name not in registry:
            raise DataSourceParamsNotFound(report_template.data_source_name)

        self._report_template = report_template
        self._file_path = file_path
        self._user = user

    @cached_property
    def _data_source(self):
        """Имя источника данных, указанного в шаблоне.

        :rtype: str
        """
        return self._report_template.data_source

    @cached_property
    def _report_columns(self):
        """Столбцы отчета.

        :rtype: tuple
        """
        return tuple(self._report_template.columns.exclude(pk__in=self._ignored_columns_ids))

    @cached_property
    def _ignored_columns_ids(self):
        """Исключенные из отчета колонки

        :rtype: set
        """
        ignored_columns = set()
        for col_id, col_name in self._report_template.columns.values_list('id', 'name'):
            if self._data_source.is_column_ignored(col_name):
                ignored_columns.add(col_id)

        return ignored_columns

    @cached_property
    def _data(self):
        """Отфильтрованные и отсортированные данные отчета.

        :rtype: list
        """
        return list(
            DataLoader(
                self._report_template, self._data_source, self._report_columns, self._ignored_columns_ids, self._user
            )
        )

    @cached_property
    def _workbook(self):
        """Книга Excel, в которой формируется отчет."""
        result = Workbook(
            self._file_path,
            dict(
                default_date_format='dd.mm.yyyy',
            ),
        )

        for cell_format in (result.default_date_format, result.default_url_format):
            cell_format.set_border()
            cell_format.set_align('vcenter')

        return result

    @cached_property
    def _worksheet(self):
        """Страница в книге Excel."""
        return self._workbook.add_worksheet('Отчет')

    @abc.abstractmethod
    def _flush_header(self):
        """Запись заголовка отчета."""

    @abc.abstractmethod
    def _flush_data(self):
        """Запись данных в отчет."""

    def build(self):
        """Формирование отчета."""
        self._flush_header()
        self._flush_data()

        self._workbook.close()


class BaseColumnAggregator(metaclass=abc.ABCMeta):
    """Базовый класс агрегатора данных для колонки."""

    @abc.abstractmethod
    def type(self):
        """Тип агрегатора."""

    @abc.abstractmethod
    def title(self):
        """Название агрегатора."""

    def __init__(self, column_index, by_value, total, **kwargs):
        """Инициализирует агрегатор.

        :param column_name: Название колонки.
        :param column_index: Порядковый номер колонки в отчете.
        :param by_value: Требуется вывод промежуточного итога в отчет.
        :param total: Требуется вывод итога в отчет.
        :param kwargs: Дополнительные параметры.
        """
        self.__column_idx = column_index
        self.__data = defaultdict(int)
        self.__is_total = total
        self.__is_by_value = by_value

    @abc.abstractmethod
    def aggregate(self, value):
        """Реализует правила подсчета по значению колонки."""

    def get(self, value):
        """Возвращает результат подсчета для определенного элемента."""
        return self.__data[value]

    @property
    def data(self):
        """Возвращает текущий результат выполнения подсчета."""
        return self.__data

    @property
    def is_by_value(self):
        """Требуется вывод промежуточного итога в отчет."""
        return self.__is_by_value

    @property
    def is_total(self):
        """Требуется вывод итога в отчет"""
        return self.__is_total

    @property
    def total(self):
        """Считает итоговое значение по собранным промежуточным итогам."""
        return sum(self.__data.values())

    @property
    def column_index(self):
        """Позиция колонки в отчете."""
        return self.__column_idx


class ColumnCounter(BaseColumnAggregator):
    """Счетчик данных для колонки."""

    type = COUNT
    title = 'Количество'

    def __init__(self, column_index, by_value, total, **kwargs):
        super(ColumnCounter, self).__init__(column_index, by_value, total, **kwargs)

        # Требуется ли вывод в итоге количества уникальных значений.
        self.__is_total_unique = kwargs.get('total_unique', False)

    def aggregate(self, value):
        """Считает количество элементов."""
        self.data[value] += 1

    @property
    def is_total_unique(self):
        """Требуется вывод количества уникальных значений."""
        return self.__is_total_unique

    @property
    def total_unique(self):
        """Количество уникальных значений."""
        return sum(count for count in self.data.values() if count == 1)


class ColumnSum(BaseColumnAggregator):
    """Сумматор данных для колонки."""

    type = SUM
    title = 'Сумма'

    def aggregate(self, value):
        """Считает сумму элементов."""
        if isinstance(value, str):
            # Если число, то пробуем привести к int.
            if value.isdigit():
                value = int(value)
            # Иначе, пробуем привести к float.
            else:
                try:
                    value = float(value)
                except ValueError:
                    value = 0

        self.data[value] += value


def get_column_aggregator_info(column):
    """Возвращает информацию об агрегаторе колонки.

    :param column: Колонка отчета
    :type column: educommon.report.constructor.models.ReportColumn
    :return: Тип агрегатора, (промежуточный итог, итог, количество уникальных)
    :rtype: tuple
    """
    if column.by_value == BY_VALUE_COUNT or column.total in (TOTAL_COUNT, TOTAL_UNIQUE_COUNT):
        return COUNT, (
            column.by_value == BY_VALUE_COUNT,
            column.total == TOTAL_COUNT,
            column.total == TOTAL_UNIQUE_COUNT,
        )
    elif column.by_value == BY_VALUE_SUM or column.total == TOTAL_SUM:
        return SUM, (column.by_value == BY_VALUE_SUM, column.total == TOTAL_SUM, None)
    else:
        return None, (None, None, None)


class DataAggregator:
    """Агрегатор данных полученных при формировании отчета."""

    def __init__(self, report_columns):
        self._report_columns = report_columns

        self._aggregators = dict()
        self.set_aggregators((ColumnCounter, ColumnSum))

    def set_aggregators(self, aggregators):
        """Добавляет последовательность агрегаторов."""
        for aggregator in aggregators:
            self.set_aggregator(aggregator)

    def set_aggregator(self, aggregator):
        """Добавляет агрегатор."""
        self._aggregators[aggregator.type] = dict(cls=aggregator, instances=dict())

    def get_column_aggregator(self, column, column_idx):
        """Возвращает агрегатор для колонки."""
        aggregator_type, (by_value, total, total_unique) = get_column_aggregator_info(column)
        aggregator = self._aggregators.get(aggregator_type)
        if not aggregator:
            return

        instance = aggregator['instances'].get(column.name)
        if not instance:
            aggregator_cls = aggregator['cls']
            params = dict(
                column_name=column.name,
                column_index=column_idx,
                by_value=by_value,
                total=total,
            )
            if total_unique:
                params['total_unique'] = total_unique
            instance = aggregator_cls(**params)
            aggregator['instances'][column.name] = instance

        return instance

    def _process_cell_value(self, col_idx, col_value):
        """Считает промежуточный результат для значения в ячейке."""
        column = self._report_columns[col_idx]
        column_aggregator = self.get_column_aggregator(column, col_idx)
        if col_value and column_aggregator:
            column_aggregator.aggregate(col_value)

    def aggregate(self, row_data):
        """Считает промежуточный результат по элементам строки отчета."""
        for idx, value in enumerate(row_data):
            if isinstance(value, (list, tuple)):
                for nested_data in value:
                    for nested_idx, nested_value in enumerate(nested_data):
                        col_idx = idx + nested_idx
                        self._process_cell_value(col_idx, nested_value)
            else:
                self._process_cell_value(idx, value)

    def get_empty_row(self):
        """Формирует пустую строку по количеству колонок в отчете."""
        return ['' for _ in range(len(self._report_columns))]

    def _extend_rows(self, aggregators, rows):
        """Добавляет строки с промежуточными итогами."""
        aggregators_data = (
            (
                aggregator.title,
                aggregator.column_index,
                aggregator.data.items(),
            )
            for aggregator in aggregators
            if aggregator.is_by_value
        )
        for title, col_idx, data in aggregators_data:
            for idx, (value, value_data) in enumerate(data):
                try:
                    row_data = rows[idx]
                except IndexError:
                    row_data = self.get_empty_row()
                    rows.append(row_data)

                row_data[col_idx] = '{} "{}": {}'.format(title, value, value_data)

    def _extend_rows_by_count(self, rows):
        """Добавляет строки с количеством элементов."""
        counters = sorted(self._aggregators[COUNT]['instances'].values(), key=lambda c: c.column_index)
        self._extend_rows(counters, rows)

    def _extend_rows_by_sum(self, rows):
        """Добавляет строки с суммой элементов."""
        summators = sorted(self._aggregators[SUM]['instances'].values(), key=lambda c: c.column_index)
        self._extend_rows(summators, rows)

    def get_total_row(self):
        """Возвращает строку с итоговыми значениями."""
        row = self.get_empty_row()
        for aggregator in self._aggregators.values():
            for instance in aggregator['instances'].values():
                if instance.is_total:
                    row[instance.column_index] = 'Итог({}): {}'.format(instance.title, instance.total)
                elif instance.is_total_unique:
                    row[instance.column_index] = 'Итог(Уникальных): {}'.format(instance.total_unique)

        return row

    def get_rows(self):
        """Возвращает строки отчета с результатами подсчета значений."""
        rows = list()
        self._extend_rows_by_count(rows)
        self._extend_rows_by_sum(rows)

        # Добавляем итоговые значения
        total_row = self.get_total_row()
        if any(total_row):
            rows.append(total_row)
        return rows
