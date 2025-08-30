from objectpack.actions import (
    ObjectPack,
)

from educommon.audit_log.models import (
    PostgreSQLError,
)
from educommon.audit_log.permissions import (
    PERM_GROUP__AUDIT_LOG_ERRORS,
)
from educommon.m3 import (
    PackValidationMixin,
)
from educommon.objectpack.ui import (
    BaseListWindow,
)


class PostgreSQLErrorPack(PackValidationMixin, ObjectPack):
    """Журнал кастомных ошибок PostgreSQL."""

    title = 'Журнал ошибок PostgreSQL'

    model = PostgreSQLError
    allow_paging = True
    can_delete = True

    list_sort_order = ('-time',)
    columns = (
        dict(
            data_index='time',
            width=140,
            fixed=True,
            header='Дата и время',
        ),
        dict(
            data_index='ip',
            width=80,
            fixed=True,
            header='IP',
        ),
        dict(
            data_index='level',
            width=100,
            fixed=True,
            header='Уровень ошибки',
        ),
        dict(
            data_index='text',
            header='Сообщение об ошибке',
        ),
    )

    list_window = BaseListWindow

    def __init__(self):
        super(PostgreSQLErrorPack, self).__init__()
        # ---------------------------------------------------------------------
        # Настройка разрешений для экшенов пака.
        self.need_check_permission = True
        self.perm_code = PERM_GROUP__AUDIT_LOG_ERRORS

        for action in self.actions:
            action.perm_code = 'view'

        self.delete_action.perm_code = 'delete'
        # ---------------------------------------------------------------------

    def extend_menu(self, menu):
        return menu.administry(
            menu.Item(self.title, self.list_window_action),
        )

    def get_list_window_params(self, params, request, context):
        result = super(PostgreSQLErrorPack, self).get_list_window_params(params, request, context)

        result['maximized'] = True
        result['read_only'] = not self.delete_action.has_perm(request)

        return result

    def configure_grid(self, grid):
        super(PostgreSQLErrorPack, self).configure_grid(grid)

        grid.cls = 'word-wrap-grid'
