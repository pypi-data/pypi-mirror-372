# pylint: disable=attribute-defined-outside-init, no-member
import json

from django.utils.safestring import (
    mark_safe,
)
from m3.actions.context import (
    ActionContext,
)
from m3_ext.ui.containers.containers import (
    ExtContainer,
    ExtToolbarMenu,
)
from m3_ext.ui.containers.context_menu import (
    ExtContextMenu,
)
from m3_ext.ui.containers.forms import (
    ExtPanel,
)
from m3_ext.ui.containers.grids import (
    ExtGridCheckBoxSelModel,
)
from m3_ext.ui.containers.trees import (
    ExtTree,
)
from m3_ext.ui.fields import (
    ExtMultiSelectField,
)
from m3_ext.ui.icons import (
    Icons,
)
from m3_ext.ui.menus import (
    ExtContextMenuItem,
)
from m3_ext.ui.misc import (
    ExtDataStore,
)
from m3_ext.ui.misc.label import (
    ExtLabel,
)
from m3_ext.ui.panels.grids import (
    ExtObjectGrid,
)

from objectpack.tree_object_pack.ui import (
    BaseObjectTree,
    BaseTreeSelectWindow,
)
from objectpack.ui import (
    BaseListWindow,
    ColumnsConstructor,
    ObjectTab,
    WindowTab,
)

from educommon import (
    ioc,
)
from educommon.auth.rbac.constants import (
    PERM_SOURCES,
)
from educommon.auth.rbac.models import (
    Role,
)
from educommon.objectpack.ui import (
    ModelEditWindow,
    TabbedEditWindow,
)
from educommon.utils.ui import (
    switch_window_in_read_only_mode,
)


class RolesTree(BaseObjectTree):
    """Грид для отображения иерархии ролей.

    Отличается от обычного грида для отображения деревьев тем, что помимо
    кнопок "Новый в корне" и "Новый дочерний" имеет кнопку "Добавить в роль".
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Меню "Добавить"
        self.top_bar.button_add_to_role = ExtContextMenuItem(
            text='Добавить в роль',
            icon_cls='add_item',
            handler='topBarAddToRole',
        )
        self.top_bar.add_menu.menu.items.append(self.top_bar.button_add_to_role)

        # Меню "Удалить"
        self.top_bar.items.remove(self.top_bar.button_delete)
        self.top_bar.button_delete_from_role = ExtContextMenuItem(
            text='Удалить из роли',
            icon_cls='delete_item',
            handler='topBarDeleteFromRole',
        )
        self.top_bar.button_delete = ExtContextMenuItem(
            text='Удалить из системы',
            icon_cls='delete_item',
            handler='topBarDelete',
        )

        menu = ExtContextMenu()
        menu.items.extend(
            (
                self.top_bar.button_delete_from_role,
                self.top_bar.button_delete,
            )
        )
        self.top_bar.delete_menu = ExtToolbarMenu(icon_cls='delete_item', menu=menu, text='Удалить')
        self.top_bar.items.append(self.top_bar.delete_menu)

        # Передаем индексы, так как некорректно
        # формируется client_id для данных элементов.
        self.add_menu_index = self.top_bar.items.index(self.top_bar.add_menu)
        self.new_child_index = self.top_bar.add_menu.menu.items.index(self.top_bar.button_new_child)
        self.add_to_role_index = self.top_bar.add_menu.menu.items.index(self.top_bar.button_add_to_role)
        self.delete_menu_index = self.top_bar.items.index(self.top_bar.delete_menu)
        self.delete_from_role_index = menu.items.index(self.top_bar.button_delete_from_role)


class RolesListWindow(BaseListWindow):
    """Окно для отображения иерархии ролей."""

    def _init_components(self):
        """Метод создаёт визуальные компоненты, отражающие поля модели.

        Не определяет расположение компонентов в окне.
        """
        super()._init_components()

        self.grid = RolesTree()

    def set_params(self, params):
        """Метод принимает словарь, содержащий параметры окна, передаваемые в окно слоем экшенов."""
        super().set_params(params)

        template = 'rbac/roles-list-window.js'
        self.pack = params['pack']

        # Включение/отключение элементов окна в зависимости от прав доступа
        if not params['can_edit']:
            template = 'rbac/roles-view-list-window.js'
            # Отключение контролов для добавления ролей
            self.grid.action_new = None

            # Отключение контролов для изменения ролей
            for control in (self.grid.top_bar.button_edit, self.grid.context_menu_row.menuitem_edit):
                control.text = 'Просмотр'
                control.icon_cls = Icons.APPLICATION_VIEW_DETAIL

            # Изменение контролов для удаления ролей
            self.grid.action_delete = None
            self.grid.url_delete = None
            self.grid.top_bar.items.remove(self.grid.top_bar.delete_menu)

        self.template_globals = template


class RoleSelectWindow(BaseTreeSelectWindow):
    """Окно выбора роли, в которую будет добавлена указанная роль."""

    def _init_components(self):
        """Создание компонентов."""
        super()._init_components()

        self.label_message = ExtLabel(
            text='Выберите роль, в которую будет добавлена роль "{}":',
            style={'padding': '5px'},
            region='north',
        )

    def _do_layout(self):
        """Метод располагает уже созданные визуальные компоненты на окне."""
        super()._do_layout()

        self.layout = 'border'

        self.items.insert(0, self.label_message)

    def set_params(self, params):
        """Установка параметров окна."""
        super().set_params(params)

        self.title = 'Добавление одной роли в другую'

        self.grid.region = 'center'
        self.grid.action_new = None
        self.grid.action_edit = None
        self.grid.action_delete = None

        if self.grid.action_context is None:
            self.grid.action_context = ActionContext()
        self.grid.action_context.role_id = params['role'].id

        self.label_message.text = mark_safe(self.label_message.text.format(params['role'].name))


# -----------------------------------------------------------------------------


def _make_user_type_field(name='user_type_ids', **kwargs):
    field = ExtMultiSelectField(
        label='Может быть назначена',
        anchor='100%',
        hide_edit_trigger=False,
        hide_trigger=False,
        hide_dict_select_trigger=False,
        **kwargs,
    )
    field.name = name

    return field


class PermissionsChangeTab(ObjectTab):
    """Вкладка "Разрешения роли" окна редактирования роли.

    Содержит элементы интерфейса для изменения параметров роли: названия,
    текстового описания, перечня разрешений и т.д.
    """

    title = 'Разрешения роли'

    model = Role

    field_fabric_params = dict(
        field_list=('name', 'description', 'can_be_assigned'),
    )

    def init_components(self, win):
        """Создаются компоненты, но не задаётся расположение."""
        super().init_components(win)

        self.field__user_types = _make_user_type_field()
        self.container__top = ExtPanel(
            body_cls='x-window-mc',
            border=False,
        )
        self.grid__partitions = ExtObjectGrid()
        self.grid__partitions.top_bar.hidden = True
        self.container__right = ExtContainer()

        self.grid__permissions = ExtObjectGrid()
        self.grid__permissions.top_bar.hidden = True
        self.grid__permissions.store.auto_load = False

        self.panel__description = ExtPanel(
            header=True,
            padding=5,
            title='Описание разрешения',
        )

    def do_layout(self, win, tab):
        """Задаётся расположение компонентов."""
        super().do_layout(win, tab)

        tab.border = False

        win.tab__permissions_change = tab
        win.field__name = self.field__name
        win.field__description = self.field__description
        win.field__can_be_assigned = self.field__can_be_assigned
        win.field__user_types = self.field__user_types
        win.grid__partitions = self.grid__partitions
        win.container__right = self.container__right
        win.grid__permissions = self.grid__permissions
        win.panel__description = self.panel__description

        self.container__top.items[:] = (
            self.field__name,
            self.field__description,
            self.field__can_be_assigned,
        )
        self.container__right.items[:] = (
            self.grid__permissions,
            self.panel__description,
        )
        tab.items[:] = (
            self.container__top,
            self.grid__partitions,
            self.container__right,
        )

        tab.layout = 'border'
        self.container__top.region = 'north'
        self.container__top.height = 130
        self.grid__partitions.region = 'west'
        self.grid__partitions.width = '20%'
        self.container__right.region = 'center'
        self.container__right.width = '80%'

        self.container__top.layout = 'form'
        self.container__top.label_width = 60
        self.container__top.padding = 5

        self.container__right.layout = 'vbox'
        self.container__right.layout_config = {
            'align': 'stretch',
        }
        self.panel__description.flex = 0
        self.panel__description.height = 100
        self.grid__permissions.flex = 1

    def set_params(self, win, params):
        """Установка параметров."""
        super().set_params(win, params)

        if params.get('show_user_types', False):
            self.container__top.height += 45
            self.container__top.label_width = 140
            self.container__top.items.append(self.field__user_types)

            self.field__user_types.set_store(ExtDataStore(data=params['user_types']))
            self.field__user_types.value = params.get('user_type_ids', ())

        if params['can_edit']:
            self.grid__permissions.sm = ExtGridCheckBoxSelModel(
                check_only=True,
            )

        params['partitions_pack'].configure_grid(self.grid__partitions)
        params['permissions_pack'].configure_grid(self.grid__permissions)


class ResultPermissionsTree(ExtTree):
    """Панель для отображения итоговых разрешений в виде дерева.

    В дереве отображается три уровня: разделы, группы и сами разрешения.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()

        ColumnsConstructor.from_config(
            (
                dict(
                    data_index='title',
                    header='Наименование',
                ),
                dict(
                    data_index='description',
                    hidden=True,
                ),
                dict(
                    data_index='source',
                    header='Источник',
                ),
            )
        ).configure_grid(self)


class ResultPermissionsTab(WindowTab):
    """Вкладка "Итоговые разрешения" окна редактирования роли.

    Предназначена для отображения результирующего набора разрешений, которые
    предоставляет роль. В этот набор входят:

        - разрешения, добавленные в роль;
        - разрешения, зависящие тех, которые добавлены в роль;
        - разрешения вложенных ролей.

    Для каждого разрешения указывается источник: сама роль, зависимое
    разрешение или вложенная роль.
    """

    title = 'Итоговые разрешения'

    def init_components(self, win):
        """Создаются компоненты, но не задаётся расположение."""
        super().init_components(win)

        self.tree__result_permissions = ResultPermissionsTree()

        self.panel__description = ExtPanel(
            header=True,
            padding=5,
            title='Описание разрешения',
        )

    def do_layout(self, win, tab):
        """Задаётся расположение компонентов."""
        super().do_layout(win, tab)

        win.tab__result_permissions = tab
        tab.tree__result_permissions = self.tree__result_permissions
        tab.panel__description = self.panel__description

        tab.items.extend(
            (
                self.tree__result_permissions,
                self.panel__description,
            )
        )

        tab.layout = 'vbox'
        tab.layout_config = dict(
            align='stretch',
        )
        self.tree__result_permissions.flex = 1
        self.panel__description.flex = 0
        self.panel__description.height = 100


class RoleAddWindow(ModelEditWindow):
    """Окно добавления роли."""

    model = Role

    field_fabric_params = dict(
        field_list=('name', 'description', 'can_be_assigned'),
        model_register=ioc.get('observer'),
    )

    def _init_components(self):
        """Метод создаёт визуальные компоненты, отражающие поля модели.

        Не определяет расположение компонентов в окне.
        """
        super()._init_components()
        self.field__user_types = _make_user_type_field()

    def _do_layout(self):
        """Метод располагает уже созданные визуальные компоненты на окне."""
        super()._do_layout()
        self.form.items.append(self.field__user_types)

    def set_params(self, params):
        """Метод принимает словарь, содержащий параметры окна, передаваемые в окно слоем экшенов."""
        super().set_params(params)

        self.template_globals = 'rbac/role-add-window.js'

        if params.get('show_user_types', False):
            self.field__user_types.set_store(ExtDataStore(data=params['user_types']))


class RoleEditWindow(TabbedEditWindow):
    """Окно редактирования роли."""

    model = Role

    tabs = (
        PermissionsChangeTab,
        ResultPermissionsTab,
    )

    def set_params(self, params):
        """Метод принимает словарь, содержащий параметры окна, передаваемые в окно слоем экшенов."""
        super().set_params(params)

        self.width = 1100
        self.height = 700

        self.template_globals = 'rbac/role-edit-window.js'

        self.id_param_name = params['roles_pack']
        self.role = params['object']
        self.roles_pack = params['roles_pack']
        self.perm_sources = PERM_SOURCES
        self.permission_ids = params['permission_ids']
        self.can_edit = json.dumps(params['can_edit'])
        self.result_action_url = params['result_action_url']

        if not params['can_edit']:
            switch_window_in_read_only_mode(self)


# -----------------------------------------------------------------------------
