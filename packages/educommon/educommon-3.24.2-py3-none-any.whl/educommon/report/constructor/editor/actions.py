from collections import (
    OrderedDict,
    defaultdict,
)
from itertools import (
    chain,
    repeat,
)

from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db.transaction import (
    atomic,
)
from m3.actions.exceptions import (
    ApplicationLogicException,
)
from m3.actions.results import (
    OperationResult,
    PreJsonResult,
)
from m3_ext.ui.results import (
    ExtUIScriptResult,
)

from m3_django_compat.exceptions import (
    FieldDoesNotExist,
)
from objectpack.actions import (
    BaseAction,
    ObjectPack,
)
from objectpack.exceptions import (
    ValidationError,
)
from objectpack.ui import (
    BaseEditWindow,
    make_combo_box,
)

from educommon.m3 import (
    PackValidationMixin,
    convert_validation_error_to,
    get_id_value,
)
from educommon.report.constructor import (
    constants,
)
from educommon.report.constructor.base import (
    ColumnDescriptor,
)
from educommon.report.constructor.config import (
    report_constructor_config,
)
from educommon.report.constructor.editor.ui import (
    EditWindow,
    ListWindow,
)
from educommon.report.constructor.models import (
    ReportColumn,
    ReportFilter,
    ReportFilterGroup,
    ReportSorting,
    ReportTemplate,
)
from educommon.report.constructor.registries import (
    registry,
)
from educommon.utils.misc import (
    cached_property,
)
from educommon.utils.ui import (
    anchor100,
)


class ColumnsAction(BaseAction):
    """Действие, предоставляющее данные для дерева столбцов."""

    def context_declaration(self):
        return dict(
            data_source_name=dict(type='str'),
            parent_column_name=dict(type='str_or_none', default=None),
        )

    @staticmethod
    def _get_column_params(column):
        result = dict(
            name=column.accessor_name,
            data_type=column.data_type,
            full_name=column.full_accessor_name,
            title=column.title,
            leaf=not column.has_nested_columns(),
        )

        if result['data_type'] == constants.CT_CHOICES:
            result['choices'] = column.choices

        return result

    def run(self, request, context):
        if context.data_source_name not in registry:
            raise ApplicationLogicException('Не выбран источник данных.')

        if context.parent_column_name == '-1':
            context.parent_column_name = None

        data_source = registry.get(context.data_source_name).get_data_source_descriptor()

        if context.parent_column_name:
            parent_column = ColumnDescriptor.create(data_source.model, context.parent_column_name, data_source)
            columns = parent_column.get_nested_columns()
        else:
            columns = tuple(data_source.get_available_columns())

        return PreJsonResult(tuple(map(ColumnsAction._get_column_params, columns)))


_BUILDERS_PACKAGE = 'educommon.report.constructor.builders'


class BuildAction(BaseAction):
    """Сборка отчета на основе указанного шаблона."""

    _builders = {
        ReportTemplate.EXCEL_SIMPLE: f'{_BUILDERS_PACKAGE}.excel.product.ReportBuilder',
        ReportTemplate.EXCEL_MERGED: f'{_BUILDERS_PACKAGE}.excel.with_merged_cells.ReportBuilder',
    }

    def context_declaration(self):
        return {
            self.parent.id_param_name: dict(type=int),
            'format': dict(type='int_or_none', default=None),
        }

    def _get_report_template(self, request, context):
        # Загрузка шаблона
        try:
            return ReportTemplate.objects.get(pk=get_id_value(context, self.parent))
        except ReportTemplate.DoesNotExist:
            raise ApplicationLogicException(self.parent.MSG_DOESNOTEXISTS)

    def _check_report_template(self, report_template):
        # Проверка наличия в системе источника данных с именем, указанным в
        # шаблоне.
        if report_template.data_source_name not in registry:
            raise ApplicationLogicException(
                'Источник данных {} не существует.'.format(report_template.data_source_name)
            )

        data_source = registry.get(report_template.data_source_name).get_data_source_descriptor()

        if ReportInfo(report_template).ignored_columns_ids:
            raise ApplicationLogicException('Некоторые колонки шаблона неактуальны, требуется редактирование')

        # Проверка доступности данных для всех столбцов шаблона отчета.
        try:
            for col_name in report_template.columns.values_list('name', flat=True):
                if data_source.is_column_ignored(col_name):
                    continue
                data_source.get_column_descriptor(col_name)
        except FieldDoesNotExist as error:
            raise ApplicationLogicException('Колонка {} недоступна'.format(str(error)))

    def _check_params(self, request, context, report_template):
        """Возвращает True, если параметры сборки указаны верно."""
        if context.format is None:
            return report_template.format in self._builders

        if report_template.format == ReportTemplate.USER_DEFINED and context.format in self._builders:
            return True

        return False

    def _get_params_window(self, request, context, report_template):
        win = BaseEditWindow()

        win.field__format = make_combo_box(
            label='Формат отчета',
            name='format',
            data=ReportTemplate.FORMAT_CHOICES[1:],
        )

        win.form.items.extend(
            anchor100(
                win.field__format,
            )
        )

        win.set_params(
            dict(
                form_url=self.get_absolute_url(),
                height=100,
                title='Параметры сборки',
            )
        )

        return ExtUIScriptResult(win, context)

    def _check_format(self, report_format):
        if report_format not in self._builders:
            raise ApplicationLogicException('Указан неверный формат отчета.')

    def _build_report(self, request, context):
        report_template_id = get_id_value(context, self.parent)
        current_user_func = report_constructor_config.current_user_func
        user = current_user_func(request)
        content_type = ContentType.objects.get_for_model(user)
        params = {
            'object_id': user.id,
            'content_type': content_type,
            'report_template_id': report_template_id,
            'format': context.format or None,
        }
        report_constructor_config.async_task.apply_async(None, params)

        return OperationResult(
            message='Внимание! Задача поставлена в очередь! Результаты будут доступны в реестре Асинхронных задач.'
        )

    def run(self, request, context):
        report_template = self._get_report_template(request, context)
        self._check_report_template(report_template)
        if context.format:
            self._check_format(context.format)

        if self._check_params(request, context, report_template):
            return self._build_report(request, context)
        else:
            return self._get_params_window(request, context, report_template)


class ReportInfo:
    """Сведения о столбцах отчета, подготовленные к сериализации в JSON."""

    def __init__(self, report_template):
        """Инициализация экземпляра класса.

        :param report_template: Шаблон отчета.
        :type report_template:
            educommon.report.constructor.models.ReportTemplate
        """
        assert isinstance(report_template, ReportTemplate), type(report_template)

        self.report_template = report_template

    @cached_property
    def _data_source(self):
        """Источник данных шаблона.

        :rtype: educommon.report.constructor.base.ModelDataSourceDescriptor
        """
        data_source = registry.get(self.report_template.data_source_name).get_data_source_descriptor()
        return data_source

    @cached_property
    def ignored_columns_ids(self):
        """Список колонок исключенных из конструктора отчетов.

        Исключается параметром ``model.report_constructor_params``.

        :rtype: set
        """
        ignored_columns = set()
        for col_id, col_name in self.report_template.columns.values_list('id', 'name'):
            if self._data_source.is_column_ignored(col_name) or not self._data_source.is_column_exist(col_name):
                ignored_columns.add(col_id)

        return ignored_columns

    @cached_property
    def _report_columns_by_id(self):
        """Колонки отчета по id.

        :rtype: collections.OrderedDict
        """
        columns = self.report_template.columns.order_by('index')

        return OrderedDict((report_column.id, report_column) for report_column in columns)

    @cached_property
    def _report_columns_by_name(self):
        """Колонки отчета по имени.

        :rtype: collections.OrderedDict
        """
        return OrderedDict((report_column.name, report_column) for report_column in self._report_columns_by_id.values())

    @cached_property
    def _field_descriptors(self):
        """Дескрипторы полей в источнике данных.

        :rtype: collections.OrderedDict
        """
        get_descriptor = self._data_source.get_column_descriptor
        get_fake_descriptor = self._data_source.get_fake_column_descriptor

        descriptors = OrderedDict()

        for report_column in self._report_columns_by_name.values():
            if report_column.id in self.ignored_columns_ids:
                descriptor = get_fake_descriptor(report_column.title)
            else:
                descriptor = get_descriptor(report_column.name)
            while descriptor:
                if descriptor.full_accessor_name not in descriptors:
                    descriptors[descriptor.full_accessor_name] = descriptor
                descriptor = descriptor.parent

        return descriptors

    @cached_property
    def _fields_hierarchy(self):
        """Иерархия полей в источнике данных.

        :rtype: collections.defaultdict
        """
        hierarchy = defaultdict(list)

        for descriptor in self._field_descriptors.values():
            if not descriptor.is_root():
                hierarchy[descriptor.parent.full_accessor_name].append(descriptor)

        return hierarchy

    def _get_descriptor_data(self, descriptor):
        accessor_name = descriptor.accessor_name
        full_accessor_name = descriptor.full_accessor_name
        nested_descriptors = self._fields_hierarchy[full_accessor_name]

        result = dict(
            name=accessor_name,
            data_type=descriptor.data_type,
            full_name=full_accessor_name,
            title=descriptor.title,
            leaf=not descriptor.has_nested_columns(),
            nested=tuple(self._get_descriptor_data(descriptor) for descriptor in nested_descriptors),
        )
        column = self._report_columns_by_name.get(full_accessor_name, None)
        column_id = getattr(column, 'id', 0)
        result['is_fake'] = not column_id or column_id in self.ignored_columns_ids
        if full_accessor_name in self._report_columns_by_name:
            result['visible'] = self._report_columns_by_name[full_accessor_name].visible
            result['visible_title'] = 'Да' if result['visible'] else 'Нет'

            # "Количество"
            result['by_value'] = column.by_value
            if column.by_value:
                title = column.get_by_value_display()
            else:
                title = ''
            result['by_value_title'] = title

            # "Итог"
            result['total'] = column.total
            if column.total:
                title = column.get_total_display()
            else:
                title = ''
            result['total_title'] = title

        if descriptor.accessor_name in self._report_columns_by_name:
            report_column = self._report_columns_by_name[accessor_name]
            result['overridden_title'] = report_column.title

        return result

    def get_columns_data(self):
        """Возвращает параметры столбцов шаблона."""
        return tuple(
            self._get_descriptor_data(descriptor)
            for descriptor in self._field_descriptors.values()
            if descriptor.is_root()
        )

    _OPERATOR_MAP = {
        ReportFilterGroup.OPERATOR_AND: 'AND',
        ReportFilterGroup.OPERATOR_OR: 'OR',
    }

    @cached_property
    def _filter_groups(self):
        """Группы фильтров.

        :rtype: collections.OrderedDict
        """
        tree_manager = getattr(ReportFilterGroup, '_tree_manager')
        filter_groups_query = tree_manager.get_queryset_descendants(
            self.report_template.filter_groups.exclude(filters__column_id__in=self.ignored_columns_ids),
            include_self=True,
        ).prefetch_related('filters')

        return OrderedDict((filter_group.pk, filter_group) for filter_group in filter_groups_query)

    def _get_filter_data(self, report_filter):
        """Возвращает параметры фильтра.

        :rtype: dict
        """
        column = self._report_columns_by_id[report_filter.column_id]

        return dict(
            column=column.name,
            index=report_filter.index,
            operator=report_filter.operator,
            exclude=report_filter.exclude,
            case_sensitive=report_filter.case_sensitive,
            values=report_filter.values or [],
            comment=report_filter.comment,
        )

    def _get_filter_group_data(self, filter_group):
        """Возвращает парамеры группы фильтров.

        :rtype: dict
        """
        nested_groups = (
            nested_group for nested_group in self._filter_groups.values() if nested_group.parent_id == filter_group.pk
        )

        return {
            self._OPERATOR_MAP[filter_group.operator]: tuple(
                (self._get_filter_group_data(obj) if isinstance(obj, ReportFilterGroup) else self._get_filter_data(obj))
                for obj in chain(nested_groups, filter_group.filters.all())
            )
        }

    def get_filters_data(self):
        """Возвращает параметры фильтров.

        Т.к. в БД фильтры хранятся в виде дерева (синтаксическое дерево), а в
        окне редактирования фильтры организованы в виде плоского списка (так
        сделано из-за того, что на этапе анализа было решено делать фильтры
        в виде плоского списка, но позднее появилось понимание того, что должно
        быть дерево, но чтобы не тратить время на переработку окна
        редактирования, решили в UI сделать ограниченный функционал, а на
        сервере сделать полнофункциональную реализацию).

        В общем виде данные о фильтрах структурируются в таком виде:

        .. code-block:: python

           (
               {
                   'AND': (
                       {
                           'OR': (
                               {
                                   'column': 'group.unit.short_name',
                                   'operator': 3,
                                   'value': 'СДЮШОР1',
                                   ...
                               },
                               {
                                   'column': 'group.unit.short_name',
                                   'operator': 3,
                                   'value': 'СДЮШОР2',
                                   ...
                               },
                           ),
                       {
                           'column': 'person.date_of_birth',
                           'operator': 6,
                           'value': '01.01.2016',
                           ...
                       },
                       {
                           'column': 'person.date_of_birth',
                           'operator': 1,
                           'value': '31.12.2016',
                           ...
                       },
                   ),
               },
           )

        Но поскольку в окне фильтры организованы в плоский список, ожидается,
        что иерархия фильтров будет только одноуровневой.

        :rtype: tuple
        """
        return tuple(
            self._get_filter_group_data(filter_group)
            for filter_group in self._filter_groups.values()
            if filter_group.parent_id is None
        )

    @cached_property
    def _sorting_params_by_column_name(self):
        """Параметры сортировки.

        :rtype: tuple
        """
        result = tuple(
            ReportSorting.objects.filter(column__report_template=self.report_template)
            .exclude(column_id__in=self.ignored_columns_ids)
            .order_by('index')
        )

        for sorting_params in result:
            column_id = sorting_params.column_id
            sorting_params.column = self._report_columns_by_id[column_id]

        return result

    def _get_sorting_data(self, report_sorting):
        """Возвращает парамеры сортировки в пригодном для сериализации виде.

        :rtype: dict
        """
        return dict(
            column=report_sorting.column.name,
            direction=report_sorting.direction,
        )

    def get_sorting_data(self):
        """Возвращает параметры сортировки."""
        return tuple(self._get_sorting_data(sorting_params) for sorting_params in self._sorting_params_by_column_name)


class ReportTemplateWriter:
    """Класс, сохраняющий в БД данные шаблона отчета."""

    def __init__(self, report_template, columns_data, filters_data, sorting_data):
        """Инициализация экземпляра класса.

        :param report_template: Шаблон отчета
        :type report_template:
            educommon.report.constructor.models.ReportTemplate

        :param list columns_data: Параметры столбцов, полученные в
            HTTP-запросе из окна редактирования шаблона.

        :param dict filters_data: Параметры фильтров, полученные в
            HTTP-запросе из окна редактирования шаблона.

        :param list sorting_data: Параметры сортировки, полученные в
            HTTP-запросе из окна редактирования шаблона.
        """
        assert isinstance(report_template, ReportTemplate)

        self._report_template = report_template
        self._columns_data = columns_data
        self._filters_data = filters_data
        self._sorting_data = sorting_data

        self.errors = []

        self._column_descriptors = OrderedDict()
        self._report_columns = {}

    def _is_report_template_valid(self, report_template):
        """Возвращает True, если шаблон отчета корректный.

        Перечень проверок:

            1. Источник данных зарегистрирован в Системе.

        :rtype: bool
        """
        if report_template.data_source_name not in registry:
            self.errors.append('Источник данных "{}" не существует.'.format(report_template.data_source_name))

        return not self.errors

    def _is_columns_data_valid(self, columns_data):
        """Возвращает True, если параметры столбцов корректны.

        Перечень проверок:

            1. В источнике данных шаблона отчета должны быть все столбцы
               шаблона.

        :rtype: bool
        """
        # ---------------------------------------------------------------------
        # Проверка наличия в источнике данных указанных столбцов.

        data_source = registry.get(self._report_template.data_source_name).get_data_source_descriptor()

        for column_params in columns_data:
            if 'accessor_name' not in column_params:
                self.errors.append('Колонки отчета заданы неверно.')
                break

            full_accessor_name = column_params['accessor_name']
            if full_accessor_name in self._column_descriptors:
                self.errors.append('Колонка {} указана более одного раза.'.format(full_accessor_name))
            else:
                try:
                    column_descriptor = data_source.get_column_descriptor(full_accessor_name)
                except FieldDoesNotExist:
                    self.errors.append(
                        'Колонки "{}" нет в источнике данных "{}".'.format(full_accessor_name, data_source.title)
                    )
                else:
                    self._column_descriptors[full_accessor_name] = column_descriptor

        if not any(column_params.get('visible', False) for column_params in columns_data):
            self.errors.append('В отчете нет ни одного видимого столбца.')
        # ---------------------------------------------------------------------

        return not self.errors

    def _is_filters_data_valid(self, filters_data):
        """Возвращает True, если параметры фильтров корректны.

        :rtype: bool
        """
        if not isinstance(filters_data, dict):
            return False

        for operator, filters in filters_data.items():
            if operator not in ('AND', 'OR'):
                return False

            for filter_params in filters:
                if not isinstance(filter_params, dict):
                    return False

                # Проверка вложенной группы фильтров.
                if ('AND' in filter_params and not self._is_filters_data_valid(filter_params['AND'])) or (
                    'OR' in filter_params and not self._is_filters_data_valid(filter_params['OR'])
                ):
                    return False

                # Проверка параметров фильтра.
                param_names = (
                    'column',
                    'operator',
                    'values',
                )
                if (
                    'AND' not in filter_params
                    and 'OR' not in filter_params
                    and any(param_name not in filter_params for param_name in param_names)
                ):
                    return False

        return True

    def _is_sorting_data_valid(self, sorting_data):
        """Возвращает True, если параметры сортировки корректны.

        :rtype: bool
        """
        if not isinstance(sorting_data, list):
            return False

        for sorting_params in sorting_data:
            # Проверка параметров.
            param_names = (
                'column',
                'direction',
            )
            if any(param_name not in sorting_params for param_name in param_names):
                return False

        return True

    def validate(self):
        """Выполняет проверку параметров отчета перед его сохранением.

        :raises objectpack.exceptions.ValidationError: если во время проверки
            найдены ошибки.
        """
        if not self._is_report_template_valid(self._report_template):
            raise ValidationError('Параметры шаблона указаны некорректно.')
        if not self._is_columns_data_valid(self._columns_data):
            raise ValidationError('Параметры столбцов указаны некорректно.')
        if not self._is_filters_data_valid(self._filters_data):
            raise ValidationError('Параметры фильтров указаны некорректно.')
        if not self._is_sorting_data_valid(self._sorting_data):
            raise ValidationError('Параметры сортировки указаны некорректно.')

    def _write_template(self):
        """Сохранение в БД шаблона отчета."""
        self._report_template.clean_and_save()

    def _write_columns(self):
        """Сохранение в БД столбцов."""
        column_descriptor_names = set(
            column_descriptor.full_accessor_name for column_descriptor in self._column_descriptors.values()
        )

        columns_query = self._report_template.columns.order_by('index')
        report_columns = OrderedDict((report_column.name, report_column) for report_column in columns_query)

        columns_data = {column_data['accessor_name']: column_data for column_data in self._columns_data}
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Сначала нужно удалить столбцы, которых нет в запросе.

        for accessor_name in set(report_columns) - column_descriptor_names:
            report_column = report_columns.pop(accessor_name)
            report_column.delete()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        created_report_columns = []
        for index, column_descriptor in enumerate(self._column_descriptors.values(), 1):
            report_column = report_columns.get(column_descriptor.full_accessor_name)

            column_data = columns_data[column_descriptor.full_accessor_name]
            visible = column_data.get('visible', False)
            by_value = column_data.get('by_value')
            total = column_data.get('total')

            if report_column is None:
                created_report_columns.append(
                    ReportColumn.objects.create(
                        report_template=self._report_template,
                        name=column_descriptor.full_accessor_name,
                        index=index,
                        title=column_descriptor.title,
                        visible=visible,
                        by_value=by_value,
                        total=total,
                    )
                )

            elif (
                report_column.name != column_descriptor.full_accessor_name
                or report_column.index != index
                or report_column.title != column_descriptor.title
                or report_column.visible != visible
                or report_column.by_value != by_value
                or report_column.total != total
            ):
                report_column.name = column_descriptor.full_accessor_name
                report_column.index = index
                report_column.title = column_descriptor.title
                report_column.visible = visible
                report_column.by_value = by_value
                report_column.total = total

                report_column.clean_and_save()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Сохранение столбцов для дальнейшего использования.

        for report_column in chain(report_columns.values(), created_report_columns):
            self._report_columns[report_column.name] = report_column
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _write_filter_group(self, parent_group, operator, filters):
        """Сохранение в БД групп фильтров."""
        report_filter_group = ReportFilterGroup(
            report_template=self._report_template,
            parent=parent_group,
            operator=operator,
        )
        report_filter_group.clean_and_save()

        index = 0
        for filter_params in filters:
            if 'AND' in filter_params:
                operator = ReportFilterGroup.OPERATOR_AND
            elif 'OR' in filter_params:
                operator = ReportFilterGroup.OPERATOR_OR
            else:
                operator = None

            if operator:
                # Вложенная группа фильтров.
                self._write_filter_group(
                    parent_group=report_filter_group,
                    operator=operator,
                    filters=filter_params,
                )
            else:
                # Параметры фильтра.
                index += 1
                ReportFilter.objects.create(
                    group=report_filter_group,
                    column=self._report_columns.get(filter_params['column']),
                    index=index,
                    operator=filter_params['operator'],
                    exclude=filter_params.get('exclude', False),
                    case_sensitive=filter_params.get('case_sensitive'),
                    values=filter_params['values'],
                    comment=filter_params.get('comment'),
                )

    def _write_filters(self):
        """Сохранение в БД фильтров."""
        # Чтобы не разбираться с имеющимся деревом фильтров, удалим его и
        # создадим заново.

        self._report_template.filter_groups.all().delete()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        for operator, filters in self._filters_data.items():
            if operator == 'OR':
                operator = ReportFilterGroup.OPERATOR_OR
            else:
                operator = ReportFilterGroup.OPERATOR_AND

            self._write_filter_group(None, operator, filters)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _write_sorting(self):
        """Сохранение в БД параметров сортировки."""
        sorting_params = chain(self._sorting_data, repeat(None))
        sorting_objs = chain(
            ReportSorting.objects.filter(
                column__report_template=self._report_template,
            ).order_by('index'),
            repeat(None),
        )
        iterator = enumerate(zip(sorting_params, sorting_objs))

        for index, (params, obj) in iterator:
            if params and obj:
                obj.column = self._report_columns.get(params['column'])
                obj.index = index
                obj.direction = params['direction']
                obj.clean_and_save()
            elif params and not obj:
                ReportSorting.objects.create(
                    column=self._report_columns.get(params['column']),
                    index=index,
                    direction=params['direction'],
                )
            elif not params and obj:
                obj.delete()
            else:
                break

    @convert_validation_error_to(ValidationError)
    @atomic
    def write(self):
        """Сохранение в БД данных шаблона отчета."""
        self._write_template()
        self._write_columns()
        self._write_filters()
        self._write_sorting()


class Pack(PackValidationMixin, ObjectPack):
    """Пак реестра шаблонов отчетов."""

    model = ReportTemplate
    _is_primary_for_model = False

    columns = (
        dict(
            data_index='title',
            header=getattr(model, '_meta').get_field('title').verbose_name,
            column_renderer='pageDeleteRenderer',
        ),
        dict(
            data_index='valid',
            hidden=True,
        ),
    )
    list_sort_order = ('title',)

    list_window = ListWindow
    add_window = edit_window = EditWindow

    def __init__(self):
        super().__init__()

        self.columns_action = ColumnsAction()
        self.build_action = BuildAction()

        self.actions.extend(
            (
                self.columns_action,
                self.build_action,
            )
        )

    def prepare_row(self, obj, request, context):
        obj = super().prepare_row(obj, request, context)

        obj.valid = not (ReportInfo(obj).ignored_columns_ids)
        return obj

    def declare_context(self, action):
        result = super().declare_context(action)

        if action is self.save_action:
            result.update(
                title=dict(type='str'),
                data_source_name=dict(type='str'),
                columns=dict(type='json'),
                filters=dict(type='json', default={}),
                sorting=dict(type='json', default={}),
            )

        return result

    def get_list_window_params(self, params, request, context):
        result = super().get_list_window_params(params, request, context)

        result['build_action_url'] = self.build_action.get_absolute_url()

        return result

    def get_edit_window_params(self, params, request, context):
        result = super().get_edit_window_params(params, request, context)

        result['maximized'] = True

        result['available_columns_action_url'] = self.columns_action.get_absolute_url()

        # pylint: disable=dict-iter-method
        result['data_sources_params'] = registry.iteritems()

        if params['create_new']:
            result['columns'] = ()
            result['filters'] = ()
            result['sorting'] = ()
        else:
            report_template = params['object']
            report_info = ReportInfo(report_template)
            result['columns'] = report_info.get_columns_data()
            result['filters'] = report_info.get_filters_data()
            result['sorting'] = report_info.get_sorting_data()

        return result

    @convert_validation_error_to(ValidationError)
    @atomic
    def save_row(self, report_template, create_new, request, context):
        writer = ReportTemplateWriter(
            report_template=report_template,
            columns_data=context.columns,
            filters_data=context.filters,
            sorting_data=context.sorting,
        )

        try:
            writer.validate()
        except ValidationError as error:
            raise ValidationError('\n'.join((str(error), '\n'.join(writer.errors))))

        writer.write()

    @atomic
    def delete_row(self, obj_id, request, context):
        for report_sorting in ReportSorting.objects.filter(
            column__report_template=obj_id,
        ).iterator():
            report_sorting.safe_delete()

        for report_filter in ReportFilter.objects.filter(
            column__report_template=obj_id,
        ).iterator():
            report_filter.safe_delete()

        for report_filter_group in ReportFilterGroup.objects.filter(
            report_template_id=obj_id,
        ).iterator():
            report_filter_group.safe_delete()

        for report_column in ReportColumn.objects.filter(
            report_template_id=obj_id,
        ).iterator():
            report_column.safe_delete()

        super().delete_row(obj_id, request, context)

    def extend_menu(self, menu):
        return menu.SubMenu(
            'Отчеты',
            menu.SubMenu(
                'Конструктор отчетов',
                menu.Item('Редактор шаблонов', self.list_window_action),
            ),
        )
