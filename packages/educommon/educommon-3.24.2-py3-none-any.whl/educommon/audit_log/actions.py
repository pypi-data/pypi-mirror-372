from abc import (
    ABCMeta,
    abstractmethod,
)
from datetime import (
    date,
    timedelta,
)
from functools import (
    partial,
)

from django.contrib.postgres.fields.hstore import (
    HStoreField,
)
from django.db.models import (
    GenericIPAddressField,
)
from m3.actions.results import (
    PreJsonResult,
)
from m3_ext.ui.all_components import (
    ExtStringField,
)

from objectpack.actions import (
    BaseAction,
    ObjectPack,
)
from objectpack.filters import (
    ColumnFilterEngine,
)
from objectpack.ui import (
    make_combo_box,
)

from educommon import (
    ioc,
)
from educommon.audit_log.permissions import (
    PERM_GROUP__AUDIT_LOG,
)
from educommon.audit_log.proxies import (
    LogProxy,
)
from educommon.audit_log.ui import (
    ViewChangeWindow,
)
from educommon.audit_log.utils import (
    get_model_choices,
    make_hstore_filter,
)
from educommon.m3 import (
    PackValidationMixin,
)
from educommon.objectpack.actions import (
    ViewWindowPackMixin,
)
from educommon.utils.ui import (
    DatetimeFilterCreator,
    FilterByField,
)


class AuditLogPack(ViewWindowPackMixin, PackValidationMixin, ObjectPack, metaclass=ABCMeta):
    """Журнал изменений."""

    title = 'Журнал изменений'
    model = LogProxy
    width = 1000
    height = 600
    allow_paging = True

    list_sort_order = ('-time',)

    filter_engine_clz = ColumnFilterEngine
    ff = partial(FilterByField, model, model_register=ioc.get('observer'))

    edit_window = ViewChangeWindow

    can_delete = False

    # Фильтр интервала дат
    date_filter = DatetimeFilterCreator(
        model, 'time', get_from=lambda: date.today() - timedelta(days=2), get_to=date.today
    )

    def _generate_columns(self):
        """Формирует наполнение столбцов."""
        columns = [
            {
                'data_index': 'time',
                'width': 140,
                'header': 'Дата и время',
                'sortable': True,
                'filter': self.date_filter.filter
            },
            {
                'data_index': 'user_name',
                'width': 130,
                'header': 'Пользователь',
                'filter': self.ff('table__name', lookup=lambda x: self._make_name_filter('surname', x))
                & self.ff('table__name', lookup=lambda x: self._make_name_filter('firstname', x))
                & self.ff('table__name', lookup=lambda x: self._make_name_filter('patronymic', x)),
            },
            {
                'data_index': 'operation',
                'width': 60,
                'header': 'Операция',
                'filter': self.ff('operation', ask_before_deleting=False),
            },
            {
                'data_index': 'model_name',
                'width': 220,
                'header': 'Модель объекта',
                'filter': self.ff(
                    'table',
                    control_creator=lambda: make_combo_box(
                        data=get_model_choices(),
                        ask_before_deleting=False,
                    ),
                ),
            },
            {
                'data_index': 'object_id',
                'width': 50,
                'header': 'Код объекта',
                'filter': self.ff('object_id'),
            },
            {
                'data_index': 'ip',
                'width': 60,
                'header': 'IP',
                'filter': self.ff(
                    'ip',
                    parser_map=(GenericIPAddressField, 'str', '%s__contains'),
                    control_creator=ExtStringField,
                ),
            },
            {
                'data_index': 'object_string',
                'width': 180,
                'header': 'Объект',
                'filter': self.ff(
                    'data',
                    parser_map=(HStoreField, 'str', '%s__values__icontains'),
                    lookup=lambda x: make_hstore_filter('data', x),
                    control_creator=ExtStringField,
                ),
            },
        ]

        return columns

    def __init__(self):
        self.columns = self._generate_columns()

        super().__init__()

        self.view_changes_action = ViewChangeAction()
        self.actions.append(self.view_changes_action)

        self.need_check_permission = True
        self.perm_code = PERM_GROUP__AUDIT_LOG

        for action in self.actions:
            action.perm_code = 'view'

    def configure_grid(self, grid):
        """Настройка грида.

        Устанавливает интервал дат фильтрации по умолчанию
        в параметрах запроса.
        """
        super().configure_grid(grid)

        grid.store.base_params = self.date_filter.base_params

    def get_edit_window_params(self, params, request, context):
        """Возвращает словарь параметров, которые будут переданы окну редактирования."""
        params = super().get_edit_window_params(params, request, context)

        params['grid_action'] = self.view_changes_action

        return params

    def get_list_window_params(self, params, request, context):
        """Возвращает словарь параметров, которые будут переданы окну списка."""
        params = super().get_list_window_params(params, request, context)

        params['maximized'] = True

        return params

    def get_rows_query(self, request, context):
        """Возвращает выборку из БД для получения списка данных."""
        return super().get_rows_query(request, context).prefetch_related('table')

    def extend_menu(self, menu):
        """Расширение главного меню."""
        return menu.administry(
            menu.Item(self.title, self.list_window_action),
        )

    @abstractmethod
    def _make_name_filter(self, field, value):
        """Создает lookup фильтра по фамилии/имени/отчеству пользователя.

        :param str field: название поля ('firstname', 'surname', 'patronymic').
        :param str value: значение, по которому фильтруется queryset.
        """


class ViewChangeAction(BaseAction):
    """Action для просмотра изменений."""

    def context_declaration(self):
        """Делегирует декларацию контекста в пак."""
        result = super().context_declaration()

        result[self.parent.id_param_name] = dict(type='int')

        return result

    def run(self, request, context):
        """Тело Action, вызывается при обработке запроса к серверу."""
        object_id = getattr(context, self.parent.id_param_name)
        if object_id:
            rows = self.parent.model.objects.get(id=object_id).diff
        else:
            rows = []

        return PreJsonResult({'rows': rows, 'total': len(rows)})
