"""Экшены и паки приложения логирования СМЭВ."""

import datetime
import functools

from django.db.models import (
    Q,
)

from objectpack.actions import (
    ObjectPack,
)
from objectpack.filters import (
    ColumnFilterEngine,
    FilterByField,
)

from educommon.m3 import (
    PackValidationMixin,
)
from educommon.utils.ui import (
    ChoicesFilter,
    ColumnFilterWithDefaultValue,
    FilterByTextField,
)
from educommon.ws_log import (
    models,
    ui,
)


ALL_TYPES = -1  # Тип "Все", выбираемого значения в фильтре.


class SmevLogPack(ObjectPack):
    """Лог запросов СМЭВ."""

    model = models.SmevLog
    edit_window = ui.SmevLogEditWindow
    list_window = ui.SmevLogListWindow

    column_name_on_select = 'method_name'
    list_sort_order = ['-time']
    can_delete = False

    filter_engine_clz = ColumnFilterEngine
    filter_field = functools.partial(FilterByField, model)
    date_field = functools.partial(ColumnFilterWithDefaultValue, model)
    text_field_filter = functools.partial(FilterByTextField, model)

    columns = [
        {
            'data_index': 'time',
            'header': 'Дата время',
            'filter': date_field(
                'time',
                lookup=lambda d: Q(
                    time__range=(
                        datetime.datetime.combine(d, datetime.time.min),
                        datetime.datetime.combine(d, datetime.time.max),
                    )
                )
                if d
                else Q(),
                tooltip='Дата время',
                value=datetime.date.today(),
                allow_blank=False,
            ),
            'sortable': True,
            'sort_fields': ('time',),
        },
        {
            'data_index': 'service_address',
            'header': 'Адрес сервиса',
            'filter': filter_field('service_address', 'service_address__icontains'),
            'sortable': True,
            'sort_fields': ('service_address',),
        },
        {
            'data_index': 'consumer_type_verbose',
            'header': 'Потребитель сервиса',
            'filter': ChoicesFilter(
                choices=models.SmevLog.CONSUMER_TYPES + ((ALL_TYPES, 'Все'),),
                parser=int,
                lookup=lambda index: Q(consumer_type=index) if index != ALL_TYPES else Q(),
                tooltip='Потребитель сервиса',
            ),
            'sortable': True,
            'sort_fields': ('consumer_type',),
        },
        {
            'data_index': 'consumer_name',
            'header': 'Наименование потребителя',
            'filter': filter_field('consumer_name', 'consumer_name__icontains'),
            'sortable': True,
            'sort_fields': ('consumer_name',),
        },
        {
            'data_index': 'source_verbose',
            'header': 'Источник взаимодействия',
            'filter': ChoicesFilter(
                choices=models.SmevLog.SOURCE_TYPES + ((ALL_TYPES, 'Все'),),
                parser=int,
                lookup=lambda index: Q(source=index) if index != ALL_TYPES else Q(),
                tooltip='Источник взаимодействия',
            ),
            'sortable': True,
            'sort_fields': ('source',),
        },
        {
            'data_index': 'target_name',
            'header': 'Наименование электронного сервиса',
            'filter': filter_field('target_name', 'target_name__icontains'),
            'sortable': True,
            'sort_fields': ('target_name',),
        },
        {
            'data_index': 'method_name',
            'header': 'Код метода',
            'filter': filter_field('method_name', 'method_name__icontains'),
            'sortable': True,
            'sort_fields': ('method_name',),
        },
        {
            'data_index': 'method_verbose_name',
            'header': 'Наименование метода',
            'filter': filter_field('method_verbose_name', 'method_verbose_name__icontains'),
            'sortable': True,
            'sort_fields': ('method_verbose_name',),
        },
        {
            'data_index': 'result_with_default',
            'header': 'Результат',
            'filter': text_field_filter('result', 'result_with_default__icontains'),
            'sortable': True,
            'sort_fields': ('result_with_default',),
        },
        {
            'data_index': 'interaction_type_verbose',
            'header': 'Вид взаимодействия',
            'filter': ChoicesFilter(
                choices=models.SmevLog.INTERACTION_TYPES + ((ALL_TYPES, 'Все'),),
                parser=int,
                lookup=lambda index: Q(interaction_type=index) if index != ALL_TYPES else Q(),
                tooltip='Вид взаимодействия',
            ),
            'sortable': True,
            'sort_fields': ('interaction_type',),
        },
    ]

    # Название фильтра для столбца "Дата время" в ajax-запросе
    date_time_filter_param_name = 'filter_1'

    def get_rows_query(self, request, context):
        """Получение данных."""
        query = self.model.extended_manager.all()
        return query

    def configure_grid(self, grid):
        """Настройка грида."""
        super().configure_grid(grid)

        grid.top_bar.button_edit.text = 'Просмотр'

        grid.store.base_params = {self.date_time_filter_param_name: str(datetime.date.today())}

    def prepare_row(self, obj, request, context):
        """Настройка строки грида, вызывается посточно для каждой строки."""
        obj.interaction_type_verbose = dict(self.model.INTERACTION_TYPES)[obj.interaction_type]

        obj.consumer_type_verbose = dict(self.model.CONSUMER_TYPES).get(obj.consumer_type, '')

        obj.source_verbose = dict(self.model.SOURCE_TYPES).get(obj.source, '')

        return obj

    def get_edit_window_params(self, params, request, context):
        """Дополняет параметры для окна редактирования."""
        log = params['object']
        method_name = log.method_name or log.method_verbose_name

        params['title'] = 'Лог по методу: {}'.format(method_name)

        return params

    def extend_menu(self, menu):
        """Размещение в меню."""
        return menu.SubMenu(
            'Администрирование',
            menu.SubMenu('Взаимодействие со СМЭВ', menu.Item('Логи СМЭВ', pack=self.get_default_action())),
        )


class SmevProviderPack(PackValidationMixin, ObjectPack):
    """Пак поставщики СМЭВ."""

    model = models.SmevProvider
    add_window = edit_window = ui.SmevProviderEditWindow
    list_window = ui.SmevProviderListWindow

    columns = [
        {'data_index': 'mnemonics', 'header': 'Мнемоника', 'sortable': True, 'searchable': True, 'width': 1},
        {'data_index': 'address', 'header': 'Адрес СМЭВ', 'sortable': True, 'searchable': True, 'width': 1},
        {
            'data_index': 'service_name',
            'header': 'Наименование электронного сервиса',
            'sortable': True,
            'searchable': True,
            'width': 3,
        },
        {'data_index': 'source', 'header': 'Источник взаимодействия', 'sortable': True, 'searchable': True, 'width': 2},
        {'data_index': 'entity', 'header': 'Наименование юр. лица', 'sortable': True, 'searchable': True, 'width': 2},
        {
            'data_index': 'service_address_status_changes',
            'header': 'Адрес сервиса изменения статуса',
            'sortable': True,
            'searchable': True,
            'width': 3,
        },
    ]

    def extend_menu(self, menu):
        """Размещение в меню."""
        return menu.SubMenu(
            'Администрирование',
            menu.SubMenu('Взаимодействие со СМЭВ', menu.Item('Поставщики СМЭВ', pack=self.get_default_action())),
        )
